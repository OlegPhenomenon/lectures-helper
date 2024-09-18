import requests
import json
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import random
from collections import defaultdict
import re

class OllamaFormatLectureData(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
        self.prompt = """
            Ignore all previous instructions.
        
          <task> You are an experienced specialist in text formatting. The problem: we already have a well-formatted and edited text that highlights the key ideas and provides more informative explanations from the lecture. The issue is that it's broken into fragments, and when you read one fragment, the text abruptly jumps to another. Additionally, some headings might be misleading.
          Your task is to read the provided excerpts from the lecture, remove duplicates, and edit the text so that it reads as a cohesive narrative. You should not simplify or shorten the information. The goal is not to extract key phrases, as they are not very useful for learning. It is important to present the information in a way that reads like a study guide. You need to eliminate multiple headings. If you see that some headings are similar, it makes sense to combine the content so that it forms a logical flow of reasoning, rather than jumping from one topic to another. The sequence should be logical.

          I will be using this to prepare for my exam, so don't let me down!
          Please, don't write conclusions, only the lecture text.
          </task>

          <excerpts from the professor's lecture> {excerpt} </excerpts from the professor's lecture>

          <response format> While generating the output, the model should produce reasoning inside `thinking` key. If the model detects an error, it should use `reflection` key for self-correction before proceeding.
          Only after self-correction, the model should provide the final answer enclosed in `output` key.

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
            
        grouped_data = defaultdict(list)
        for item in data:
            key = item['slide_number'][:-6]  # Отбрасываем последние 6 символов
            grouped_data[key].append(item)


        merged_data = []
        for key, group in grouped_data.items():
            merged_outputs = []
            for i in range(0, len(group), 4):
                merged_output = ""
                for item in group[i:i+4]:
                    merged_output += item['output'] + "\n\n"
                merged_outputs.append(merged_output.strip())
            
            merged_item = {
                'slide_number': key,
                'output': merged_outputs
            }
            
            merged_data.append(merged_item)
        
        all_content = []
        for item in merged_data:
            last_5_hex_digits = ''.join(random.choices('0123456789ABCDEF', k=5))
            result = self.analyze_slide(item['output'])
            result['slide_number'] = item['slide_number'] + '-' + last_5_hex_digits
            all_content.append(result)
            
        with open(output_file, 'w') as f:
            json.dump(all_content, f, indent=2)
            

            