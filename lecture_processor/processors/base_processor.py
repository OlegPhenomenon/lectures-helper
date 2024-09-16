from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    def __init__(self):
        self.next_processor = None

    def set_next(self, processor):
        self.next_processor = processor
        return processor

    @abstractmethod
    def process(self, data):
        pass

    def _process_next(self, data):
        if self.next_processor:
            return self.next_processor.process(data)
        return data