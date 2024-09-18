from ..analyzers.openai_translator import OpenAITranslator
from ..analyzers.ollama_translator import OllamaTranslator

class TranslatorFactory:
    @staticmethod
    def get_translator(analyzer_type: str, config: dict):
        if analyzer_type.lower() == "ollama":
            return OllamaTranslator(config.get('ollama_url'))
        elif analyzer_type.lower() == "openai":
            return OpenAITranslator()
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")