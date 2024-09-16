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

batch_file_name = "cloud_native_lessons/1_lecture/translate_lecture_batch_file.json"

class OpenAITranslateLectureData(SlideAnalyzerBase):
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.prompt = """
          Please translate the following text into Russian. Do not format the text in any way, just translate it:
          
          {excerpt}

          json
          {{
              "output": string  // translated text
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
          json_content = json.loads(result['response']['body']['choices'][0]['message']['content'])
          json_content['slide_number'] = result['custom_id']
          all_content.append(json_content)

      # Изменим запись результатов в JSON формат с корректной кодировкой
      with open(output_file, 'w', encoding='utf-8') as f:
          json.dump(all_content, f, ensure_ascii=False, indent=2)

      os.remove(batch_file_name)
    
    def create_batch_file(self, input_file: str):
        with open(input_file, 'r') as f:
            data = json.load(f)
            
        tasks = []
        
        for item in data:
            content = item['output']
            slider_name = item['slide_number']
            
            task = {
                "custom_id": slider_name,
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
                            "content": self.prompt.format(excerpt=content)
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
