from abc import ABC, abstractmethod

class BaseTranslator(ABC):
    @abstractmethod
    def translate(self, text: str, target_language: str = 'ru') -> str:
        pass