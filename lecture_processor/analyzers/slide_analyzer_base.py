from abc import ABC, abstractmethod

class SlideAnalyzerBase(ABC):
    # @abstractmethod
    # def analyze_slide(self, topic: str, slide_description: str, excerpt: str) -> dict:
    #     pass

    @abstractmethod
    def process_batch(self, cleaned_text: str, slide_analyses: dict, output_file: str):
        pass