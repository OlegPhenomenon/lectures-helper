import requests
import json
from .slide_analyzer_base import SlideAnalyzerBase
import re

class OllamaGenerateLectureQuestions(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
        self.prompt = """
            Игнорируй все предыдущии инструкции.
        
          Перед тобой представлен текст пособия. Твоя задача сгенерировать проверочные вопросы. Вопросы должны быть направлены на проверку знаний студентов по данной лекции. Вопросы касаются только конкретно материала лекции, если в лекции присуствуют какие-то организованные моменты, которые не относятся к теме лекции, то не учитывай их. Вопросы должны быть заданы только в рамках контекста и не должны выходить за рамки лекции:
          
          {excerpt}

        <response format>
          json
          {{
              "questions": array[string]  // array of questions
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
        
        processed_data = self._process_data(data)
        
        for item in processed_data:
            content = processed_data[item]
            slider_name = item
            
            result = self.analyze_slide(content)
            result['slide_number'] = slider_name
            all_content.append(result)
            
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, ensure_ascii=False, indent=2)
  
  
    def _parse_slide_number(self, slide_number):
        return slide_number[:-11].split('.')[0].replace('_analysis', '')
      
    def _process_data(self, data):
        processed_data = {}
        for item in data:
            slide_number = item.get('slide_number', '')
            output = item.get('output', '')
            
            parsed_slide_number = self._parse_slide_number(slide_number)
            
            if parsed_slide_number in processed_data:
                processed_data[parsed_slide_number] += "\n" + output
            else:
                processed_data[parsed_slide_number] = output
        return processed_data