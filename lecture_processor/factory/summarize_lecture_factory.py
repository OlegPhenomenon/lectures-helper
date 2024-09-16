from ..analyzers.ollama_summarize_lecture import OllamaSummarizeLecture
from ..analyzers.openai_summarize_lecture import OpenAISummarizeLecture

class SummarizeLectureFactory:
    @staticmethod
    def get_analyzer(analyzer_type: str):
        if analyzer_type.lower() == "ollama":
            return OllamaSummarizeLecture()
        elif analyzer_type.lower() == "openai":
            return OpenAISummarizeLecture()
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")