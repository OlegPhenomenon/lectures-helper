import requests
import json
import re
import ast
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk
import random

source_data_file_name = 'courses/cloud_native_lessons/1_lecture/source_data.json'

class OllamaAnalyzer(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
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

        <response format> While generating output, the model produces reasoning inside the `thinking` key.
        If it detects an error, it uses the `reflection` key for self-correction before continuing.

        Only after self-correction, the model provides the final answer enclosed in `output` key.

        In `result` key you should put True or False.
        
        Return JSON with the following structure:
        {{
            "thinking": string // reasoning of the model
            "reflection": string // self-correction of the model
            "output": string // final answer
            "result": boolean // True or False
        }}
        </response format>
        """

    def analyze_slide(self, topic: str, slide_description: str, excerpt: str) -> dict:
        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": self.prompt.format(slide_description=slide_description, excerpt=excerpt, topic=topic),
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

    def process_batch(self, topic: str, cleaned_text: str, slide_analyses: dict, output_file: str):
        sorted_slides = sorted(slide_analyses.items(), key=lambda x: int(x[0].split('_')[1]))
        chunks = split_text_to_the_chunk(cleaned_text, 1000, 200)
        all_content = []
        source_data = []

        for chunk in chunks:
            for slide in sorted_slides:
                current_slide, current_analysis = slide
                last_3_hex_digits = ''.join(random.choices('0123456789ABCDEF', k=3))
                
                print('???')
                print(f"Analyzing slide {current_slide} with chunk {chunk}")
                print('???')
                
                
                result = self.analyze_slide(topic, current_analysis['description'], chunk)
                if result:
                    result['slide_number'] = f"{current_slide}-{last_3_hex_digits}"
                    
                    all_content.append(result)
                    
                    source_data.append({
                        "chunk": chunk,
                        "slide_number": f"{current_slide}-{last_3_hex_digits}"
                    })
                    
                    print(json.dumps(result, ensure_ascii=False, indent=2))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_content, f, ensure_ascii=False, indent=2)

        with open(source_data_file_name, 'w', encoding='utf-8') as f:
            json.dump(source_data, f, ensure_ascii=False, indent=2)
