from openai import OpenAI
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import json
import os
from time import sleep
from dotenv import load_dotenv
import random

load_dotenv()

# Изменим расширение файла на .json
source_data_file_name = 'courses/cloud_native_lessons/1_lecture/source_data.json'

class OpenAIAnalyzer(SlideAnalyzerBase):
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.prompt = """
        Ignore all previous instructions.

        <task> You are an experienced specialist in finding connections. Your task is to read the description of the slide and the excerpt from the lecture transcript, and determine whether the excerpt from the lecture delivered by the professor relates to this slide (the slide description should help) or most likely to another slide. </task>

        <lecture title>
        {topic}
        </lecture title>

        <slide description for analysis>
        {slide_description}
        </slide description for analysis>

        <excerpt from the professor's lecture>
        {excerpt}
        </excerpt from the professor's lecture>

        <response format> While generating output, the model produces reasoning inside the <thinking></thinking> tags.
        If it detects an error, it uses the <reflection></reflection> tags for self-correction before continuing.

        Only after self-correction, the model provides the final answer enclosed in <output></output> tags.

        In <result></result> tags you should put True or False.

        Return JSON with the following structure:
        {{
            "thinking": string // reasoning of the model
            "reflection": string // self-correction of the model
            "output": string // final answer
            "result": boolean // True or False
        }}
        </response format>
        """

    def process_batch(self, topic: str, cleaned_text: str, slide_analyses: dict, output_file: str):
        batch_file_name = 'batch_data.jsonl'
        self.create_batch_file(topic, cleaned_text, slide_analyses, output_file, batch_file_name)
        batch_file = self.upload_batch_file(batch_file_name)
        batch_job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )

        while True:
            batch_job = self.client.batches.retrieve(batch_job.id)
            print(batch_job)
            status = batch_job.status

            if status == 'completed' or status == 'failed':
                break

            sleep(20)
            
        result_file_id = batch_job.output_file_id
        
        file_content = self.client.files.content(result_file_id)
        results = [json.loads(line) for line in file_content.text.split('\n') if line.strip()]

        all_content = []
        for result in results:
            # parse and add json to all_content
            json_content = json.loads(result['response']['body']['choices'][0]['message']['content'])
            # remove hex from slide_number and add to json_content
            json_content['slide_number'] = result['custom_id']
            
            all_content.append(json_content)

        # Изменим запись результатов в JSON формат
        with open(output_file, 'w') as f:
            json.dump(all_content, f, indent=2)

        os.remove(batch_file_name)

    def create_batch_file(self, topic, cleaned_text, slide_analyses, output_file, batch_file_name):
        sorted_slides = sorted(slide_analyses.items(), key=lambda x: int(x[0].split('_')[1]))
        
        chunks = split_text_to_the_chunk(cleaned_text, 3500, 700)

        tasks = []
        source_data = []

        for chunk in chunks:
            for slide in sorted_slides:
                current_slide, current_analysis = slide
                
                print(f"Приступаем к обработке слайда {current_slide}")
                print(f"Чанк: {chunk}")
                
                last_3_hex_digits = ''.join(random.choices('0123456789ABCDEF', k=3))
                task = {
                    "custom_id": f"{current_slide}-{last_3_hex_digits}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": "gpt-4o-mini",
                        "temperature": 0.1,
                        "max_tokens": 16000,
                        "response_format": { 
                                "type": "json_object"
                            },
                        "messages": [
                            {
                                "role": "user",
                                "content": self.prompt.format(topic=topic, slide_description=current_analysis['description'], excerpt=chunk)
                            }
                        ],
                        }
                    }
                
                source_data.append({
                    "chunk": chunk,
                    "slide_number": f"{current_slide}-{last_3_hex_digits}"
                })


                tasks.append(task)

        with open(batch_file_name, 'w') as f:
            for obj in tasks:
                f.write(json.dumps(obj) + '\n')
                
        # Изменим запись source_data в JSON формат
        with open(source_data_file_name, 'w') as f:
            json.dump(source_data, f, indent=2)

        print(f"Результаты сохранены в файл: {output_file}")

    def upload_batch_file(self, batch_file_name):
        return self.client.files.create(
            file=open(f"{batch_file_name}", "rb"), purpose="batch"
        )