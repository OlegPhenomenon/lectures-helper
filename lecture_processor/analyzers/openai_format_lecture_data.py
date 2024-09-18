from openai import OpenAI
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import json
import os
from time import sleep
from dotenv import load_dotenv
import random
from collections import defaultdict

load_dotenv()

batch_file_name = "courses/cloud_native_lessons/1_lecture/format_lecture_batch_file.json"

class OpenAIFormatLectureData(SlideAnalyzerBase):
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.prompt = """
          Ignore all previous instructions.

          <task> You are an experienced specialist in text formatting. The problem: we already have a well-formatted and edited text that highlights the key ideas and provides more informative explanations from the lecture. The issue is that it's broken into fragments, and when you read one fragment, the text abruptly jumps to another. Additionally, some headings might be misleading.
          Your task is to read the provided excerpts from the lecture, remove duplicates, and edit the text so that it reads as a cohesive narrative. You should not simplify or shorten the information. The goal is not to extract key phrases, as they are not very useful for learning. It is important to present the information in a way that reads like a study guide. You need to eliminate multiple headings. If you see that some headings are similar, it makes sense to combine the content so that it forms a logical flow of reasoning, rather than jumping from one topic to another. The sequence should be logical.

          I will be using this to prepare for my exam, so don't let me down!
          Please, don't write conclusions, only the lecture text.
          </task>

          <excerpts from the professor's lecture> {excerpt} </excerpts from the professor's lecture>

          <response format> While generating the output, the model should produce reasoning inside <thinking></thinking> tags. If the model detects an error, it should use <reflection></reflection> tags for self-correction before proceeding.
          Only after self-correction, the model should provide the final answer enclosed in <output></output> tags.

          Return JSON with the following structure:

          json
          {{
              "thinking": string,  // model's reasoning
              "reflection": string,  // model's self-correction
              "output": string,  // formatted response
          }}
          </response format>
        """
        
    def process_batch(self, input_file: str, output_file: str):
      self.create_batch_file(input_file)
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
          json_content['slide_number'] = result['custom_id']
          
          all_content.append(json_content)

      # Изменим запись результатов в JSON формат
      with open(output_file, 'w') as f:
          json.dump(all_content, f, indent=2)

      os.remove(batch_file_name)
    
    def create_batch_file(self, input_file: str):
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        grouped_data = defaultdict(list)
        for item in data:
            key = item['slide_number'][:-6]  # Отбрасываем последние 6 символов
            grouped_data[key].append(item)
            
        merged_data = []
        for key, group in grouped_data.items():
            merged_outputs = []
            for i in range(0, len(group), 8):
                merged_output = ""
                for item in group[i:i+8]:
                    merged_output += item['output'] + "\n\n"
                merged_outputs.append(merged_output.strip())
            
            merged_item = {
                'slide_number': key,
                'output': merged_outputs
            }
            
            merged_data.append(merged_item)
            
        tasks = []
        
        for item in merged_data:
            slider_name = item['slide_number']

            for output in item['output']:
                last_5_hex_digits = ''.join(random.choices('0123456789ABCDEF', k=5))
                task = {
                    "custom_id": f"{slider_name}-{last_5_hex_digits}",
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
                                "content": self.prompt.format(excerpt=output)
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
