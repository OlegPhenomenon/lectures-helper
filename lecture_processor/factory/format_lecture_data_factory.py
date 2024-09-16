from ..analyzers.ollama_format_lecture_data import OllamaFormatLectureData
from ..analyzers.openai_format_lecture_data import OpenAIFormatLectureData

class FormatLectureDataFactory:
    @staticmethod
    def get_analyzer(analyzer_type: str):
        if analyzer_type.lower() == "ollama":
            return OllamaFormatLectureData()
        elif analyzer_type.lower() == "openai":
            return OpenAIFormatLectureData()
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")