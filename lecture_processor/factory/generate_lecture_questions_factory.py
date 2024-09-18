from ..analyzers.ollama_generate_lecture_questions import OllamaGenerateLectureQuestions
from ..analyzers.openai_generate_lecture_questions import OpenAIGenerateLectureQuestions

class GenerateLectureQuestionsFactory:
    @staticmethod
    def get_analyzer(analyzer_type: str):
        if analyzer_type.lower() == "ollama":
            return OllamaGenerateLectureQuestions()
        elif analyzer_type.lower() == "openai":
            return OpenAIGenerateLectureQuestions()
        else:
            raise ValueError(f"Unknown analyzer type: {analyzer_type}")