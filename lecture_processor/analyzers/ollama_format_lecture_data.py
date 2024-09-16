import requests
import json
from .slide_analyzer_base import SlideAnalyzerBase
from ..utils.text_utils import split_text_to_the_chunk

class OllamaFormatLectureData(SlideAnalyzerBase):
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model_name = "gemma2:latest"
        # ... TODO
        
    def process_batch(input_file: str, output_file: str):
      print("NEED IMPLEMENT")
      # TODO: Implement batch processing

      pass