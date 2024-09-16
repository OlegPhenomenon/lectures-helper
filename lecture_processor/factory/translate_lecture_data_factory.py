from ..analyzers.ollama_translate_lecture_data import OllamaTranslateLectureData
from ..analyzers.openai_translate_lecture_data import OpenAITranslateLectureData

class TranslateLectureDataFactory:
    @staticmethod
    def get_analyzer(analyzer_type: str):
        if analyzer_type.lower() == "ollama":
            return OllamaTranslateLectureData()
        elif analyzer_type.lower() == "openai":
            return OpenAITranslateLectureData()
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")