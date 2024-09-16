import requests
import json
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk

class OllamaAnalyzer(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
        self.prompt = """
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

        <response format> While generating output, the model produces reasoning inside the <thinking></thinking> tags.
        If it detects an error, it uses the <reflection></reflection> tags for self-correction before continuing.

        Only after self-correction, the model provides the final answer enclosed in <output></output> tags.

        In <result></result> tags you should put True or False.
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
                    return {"result": result["response"]}
            except json.JSONDecodeError:
                return None

    def process_batch(self, topic: str, cleaned_text: str, slide_analyses: dict, output_file: str):
        sorted_slides = sorted(slide_analyses.items(), key=lambda x: int(x[0].split('_')[1]))
        chunks = split_text_to_the_chunk(cleaned_text, 1000, 200)
        all_content = []

        for chunk in chunks:
            for slide in sorted_slides:
                current_slide, current_analysis = slide
                result = self.analyze_slide(topic, current_analysis['description'], chunk)
                
                all_content.append(f"Slide Number: {current_slide}\n\n")
                all_content.append(result['result'])
                all_content.append("\n\n ==== \n\n")
                
                print(result['result'])

        with open(output_file, 'w') as f:
            for obj in all_content:
                f.write(obj)