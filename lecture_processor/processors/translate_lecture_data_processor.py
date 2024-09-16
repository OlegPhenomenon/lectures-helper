from ..factory.translate_lecture_data_factory import TranslateLectureDataFactory
from .base_processor import BaseProcessor

class TranslateLectureDataProcessor(BaseProcessor):
    def process(self, data):
        analyzer_type = data.get('analyzer_type', 'openai')
        
        analyzer = TranslateLectureDataFactory.get_analyzer(analyzer_type)
        analyzer.process_batch(data['formatted_lecture_data_path'], data['translated_lecture_data_path'])
        
        print(f"Lecture translated. Result saved in {data['translated_lecture_data_path']}")
        
        return self._process_next(data)