from openai import OpenAI
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import json
import os
from time import sleep
from dotenv import load_dotenv
import random

load_dotenv()

batch_file_name = "cloud_native_lessons/1_lecture/summarize_batch_file.json"

class OpenAISummarizeLecture(SlideAnalyzerBase):
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4o-mini"
        self.prompt = """
        Ignore all previous instructions.
        
          <task> You are an experienced specialist in extracting the main essence from the text. Your task is to read the provided lecture excerpts, remove duplicates, and highlight only the core ideas and key information that will help me better understand the lecture for learning purposes.
          You should not just list key phrases from the text, as that won't be very useful for my learning. It's important to present the information in a way that feels like a study guide. In other words, you need to simplify, structure, and make the lecturer's speech easy to digest and useful for learning. </task>

          <excerpts from the professor's lecture> {excerpt} </excerpts from the professor's lecture>

          <response format> While generating output, the model produces reasoning inside <thinking></thinking> tags. If the model detects an error, it uses <reflection></reflection> tags for self-correction before continuing.
          Only after self-correction, the model provides the final answer enclosed in <output></output> tags.

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
            
        tasks = []
        
        for item in data:
          slider_name = item
          content = '... '.join(data[item])
          chunks = split_text_to_the_chunk(content, 8000, 100)

          for chunk in chunks:
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
                            "content": self.prompt.format(excerpt=chunk)
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