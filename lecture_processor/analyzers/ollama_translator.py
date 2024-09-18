from .base_translator import BaseTranslator
import requests
from ..utils.text_utils import split_text_to_the_chunk

class OllamaTranslator(BaseTranslator):
    def __init__(self, ollama_url: str):
        self.ollama_url = ollama_url

    def translate(self, text: str, target_language: str = 'ru') -> str:
        chunks = split_text_to_the_chunk(text, 1000, 200)
        translated_chunks = []

        for chunk in chunks:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "gemma:latest",
                    "prompt": f"Translate the following text to Russian, preserving all formatting, including Markdown syntax:\n\n{chunk}",
                    "stream": False,
                }
            )
            if response.status_code == 200:
                translated_chunks.append(response.json()['response'].strip())
            else:
                raise Exception(f"Error in Ollama translation: {response.text}")

        return "\n".join(translated_chunks)