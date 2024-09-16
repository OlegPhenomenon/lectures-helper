from ..analyzers.ollama_analyzer import OllamaAnalyzer
from ..analyzers.openai_analyzer import OpenAIAnalyzer

class AnalyzerFactory:
    @staticmethod
    def get_analyzer(analyzer_type: str):
        if analyzer_type.lower() == "ollama":
            return OllamaAnalyzer()
        elif analyzer_type.lower() == "openai":
            return OpenAIAnalyzer()
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")