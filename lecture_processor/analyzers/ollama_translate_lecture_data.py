import requests
import json
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import re
class OllamaTranslateLectureData(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
        self.prompt = """
          Please translate the following text into Russian. Do not format the text in any way, just translate it. But if text is in html format, please translate it into markdown format:
          
          {excerpt}

          <response format>
          json
          {{
              "output": string  // translated text in markdown format
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
            
        all_content = []
        
        for item in data:
            content = item['output']
            slider_name = item['slide_number']
            
            translated_content = self.analyze_slide(content)
            translated_content['slide_number'] = slider_name

            all_content.append(translated_content)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, ensure_ascii=False, indent=2)
            
            