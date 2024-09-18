from .base_translator import BaseTranslator
from openai import OpenAI
from ..utils.text_utils import split_text_to_the_chunk

class OpenAITranslator(BaseTranslator):
    def __init__(self):
        self.client = OpenAI()

    def translate(self, text: str, target_language: str = 'ru') -> str:
        chunks = split_text_to_the_chunk(text, 3500, 700)
        translated_chunks = []

        for chunk in chunks:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a translator. Translate the following text to Russian, preserving all formatting, including Markdown syntax."},
                    {"role": "user", "content": chunk}
                ]
            )
            translated_chunks.append(response.choices[0].message.content.strip())

        return "\n".join(translated_chunks)