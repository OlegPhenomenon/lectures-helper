from .base_processor import BaseProcessor
import requests
import json
import os
import base64

class ImageAnalysisProcessor(BaseProcessor):
    def process(self, data):
        print('Анализ изображений слайдов')
        
        analyzer = ImageAnalyzer(data['ollama_url'])
        
        for filename in os.listdir(data['images_output_dir']):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(data['images_output_dir'], filename)
                result = analyzer.analyze_image(image_path)
                
                output_filename = os.path.splitext(filename)[0] + "_analysis.json"
                output_path = os.path.join(data['slide_analyses_path'], output_filename)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                
                print(f"Анализ изображения {filename} сохранен в {output_path}")
        
        print('Анализ изображений слайдов завершен!')
        return self._process_next(data)

class ImageAnalyzer:
    def __init__(self, ollama_url):
        self.ollama_url = ollama_url
        self.model_name = "llava-llama3:8b"

    def analyze_image(self, image_path):
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')

        response = requests.post(
            f"{self.ollama_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": "Please describe what is discussed on the slide, what topics are covered, and what is written on it.",
                "stream": False,
                "images": [image_base64]
            }
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "description": result["response"],
                "topic": self._extract_topic(result["response"]),
                "information": self._extract_information(result["response"])
            }
        else:
            raise Exception(f"Ошибка при анализе изображения: {response.text}")

    def _extract_topic(self, response):
        return response.split(".")[0]

    def _extract_information(self, response):
        return ".".join(response.split(".")[1:])