from ..factory.format_lecture_data_factory import FormatLectureDataFactory
from .base_processor import BaseProcessor

class FormatLectureDataProcessor(BaseProcessor):
    def process(self, data):
        analyzer_type = data.get('analyzer_type', 'openai')
        
        analyzer = FormatLectureDataFactory.get_analyzer(analyzer_type)
        analyzer.process_batch(data['summarized_lecture_data_path'], data['formatted_lecture_data_path'])
        
        print(f"Lecture summarized. Result saved in {data['formatted_lecture_data_path']}")
        
        return self._process_next(data)