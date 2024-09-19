import logging
from openai import OpenAI
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import json
import os
from time import sleep
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

batch_file_name = "courses/cloud_native_lessons/1_lecture/questions_lecture_batch_file.json"

class OpenAIGenerateLectureQuestions(SlideAnalyzerBase):
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.max_questions = 10
        self.max_tokens = 15000
        self.chunk_overlap = 200
        self.prompt = """
        Игнорируй все предыдущие инструкции.
        
        Перед тобой представлен текст лекции. Твоя задача сгенерировать максимум {num_questions} проверочных вопросов. Вопросы должны быть направлены на проверку знаний студентов по данной лекции. Вопросы касаются только конкретно материала лекции, если в лекции присутствуют какие-то организационные моменты, которые не относятся к теме лекции, то не учитывай их. Вопросы должны быть заданы только в рамках контекста и не должны выходить за рамки лекции. Избегай вопросы которые не относятся к предмету, например, мне не обязательно задавать вопросы про преподователей, про экзамены и про другие организационные моменты. Если контекст подразумневает что подходящих вопросов не составить, то верни просто пустой список:
        
        {excerpt}

        <response format>
        json
        {{
            "questions": array[string]  // array of questions
        }}
        </response format>
        """
        
    def process_batch(self, input_file: str, output_file: str):
        logging.debug(f"Starting process_batch with input_file: {input_file}, output_file: {output_file}")
        self.create_batch_file(input_file)
        batch_file = self.upload_batch_file(batch_file_name)
        batch_job = self.client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h"
        )
        
        while True:
            batch_job = self.client.batches.retrieve(batch_job.id)
            logging.debug(f"Batch job status: {batch_job.status}")
            if batch_job.status in ['completed', 'failed']:
                break
            sleep(20)
        
        if batch_job.status == 'completed':
            result_file_id = batch_job.output_file_id
            file_content = self.client.files.content(result_file_id)
            results = [json.loads(line) for line in file_content.text.split('\n') if line.strip()]
            
            all_questions = []
            for result in results:
                json_content = json.loads(result['response']['body']['choices'][0]['message']['content'])
                all_questions.extend(json_content['questions'])

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"questions": all_questions}, f, ensure_ascii=False, indent=2)
            logging.debug(f"Questions saved to {output_file}")
        else:
            logging.error("Batch job failed")

        os.remove(batch_file_name)

    def create_batch_file(self, input_file: str):
        with open(input_file, 'r', encoding='utf-8') as f:
            lecture_data = json.load(f)
        
        lecture_text = "\n".join([item['output'] for item in lecture_data])
        chunks = split_text_to_the_chunk(lecture_text, self.max_tokens, self.chunk_overlap)
        
        tasks = []
        for i, chunk in enumerate(chunks):
            num_questions = max(1, min(self.max_questions // len(chunks), self.max_questions))
            task = {
                "custom_id": f"chunk_{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": self.model,
                    "temperature": 0.1,
                    "response_format": {"type": "json_object"},
                    "messages": [
                        {
                            "role": "user",
                            "content": self.prompt.format(excerpt=chunk, num_questions=num_questions)
                        }
                    ],
                }
            }
            tasks.append(task)

        with open(batch_file_name, 'w') as f:
            for obj in tasks:
                f.write(json.dumps(obj) + '\n')

    def upload_batch_file(self, batch_file_name):
        return self.client.files.create(
            file=open(f"{batch_file_name}", "rb"), purpose="batch"
        )