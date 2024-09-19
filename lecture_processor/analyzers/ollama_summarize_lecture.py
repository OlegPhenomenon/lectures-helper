import requests
import json
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import re
import random
class OllamaSummarizeLecture(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
        self.prompt = """
            Ignore all previous instructions.
        
          <task> You are an experienced specialist in extracting the main essence from the text. Your task is to read the provided lecture excerpts, remove duplicates, and highlight only the core ideas and key information that will help me better understand the lecture for learning purposes.
          You should not just list key phrases from the text, as that won't be very useful for my learning. It's important to present the information in a way that feels like a study guide. In other words, you need to simplify, structure, and make the lecturer's speech easy to digest and useful for learning. </task>

          <excerpts from the professor's lecture> {excerpt} </excerpts from the professor's lecture>

          <response format> While generating output, the model produces reasoning inside `thinking` key. If the model detects an error, it uses `reflection` key for self-correction before continuing.
          Only after self-correction, the model provides the final answer enclosed in `output` key.

          Return JSON with the following structure:

          json
          {{
              "thinking": string,  // model's reasoning
              "reflection": string,  // model's self-correction
              "output": string,  // formatted response
          }}
          </response format>
        """
        

    def analyze_slide(self, excerpt: str) -> dict:
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": self.prompt.format(excerpt=excerpt),
                "stream": False,
            }
        )
        
        if response.status_code == 200:
            try:
                result = response.json()
                if isinstance(result, dict) and "response" in result:
                    # Удаляем обертку ```json и ``` из ответа модели
                    json_content = re.sub(r'^```json\n|\n```$', '', result["response"].strip())
                    
                    def escape_newlines_in_strings(json_str):
                        # Regex pattern to find string literals
                        pattern = re.compile(r'("(?:[^"\\]|\\.)*")', re.DOTALL)
                        def replace_newlines(match):
                            string = match.group(1)
                            # Replace unescaped newlines with escaped ones
                            string_escaped = string.replace('\n', '\\n')
                            return string_escaped
                        return pattern.sub(replace_newlines, json_str)
                    
                    json_content_clean = escape_newlines_in_strings(json_content)
                    parsed_response = json.loads(json_content_clean)
                    
                    return parsed_response
            except json.JSONDecodeError:
                print("Ошибка при разборе JSON-ответа от модели")
            except KeyError:
                print("Отсутствует ключ 'response' в ответе модели")
        
        return None
    
    def process_batch(self, input_file: str, output_file: str):
        with open(input_file, 'r') as f:
            data = json.load(f)

        for item in data:
          slider_name = item
          content = '... '.join(data[item])
          chunks = split_text_to_the_chunk(content, 6000, 100)
          all_content = []
          
          for chunk in chunks:
              last_10_hex_digits = ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))
              result = self.analyze_slide(chunk)
              
              if result:
                  result['slide_number'] = f"{slider_name}-{last_10_hex_digits}"
                  all_content.append(result)
                  
          with open(output_file, 'w') as f:
              json.dump(all_content, f, indent=2)
