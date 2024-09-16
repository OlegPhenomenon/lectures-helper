from ..factory.summarize_lecture_factory import SummarizeLectureFactory
from .base_processor import BaseProcessor

class SummarizeLectureProcessor(BaseProcessor):
    def process(self, data):
        analyzer_type = data.get('analyzer_type', 'openai')
        
        analyzer = SummarizeLectureFactory.get_analyzer(analyzer_type)
        analyzer.process_batch(data['processed_lecture_data_path'], data['summarized_lecture_data_path'])
        
        print(f"Lecture summarized. Result saved in {data['summarized_lecture_data_path']}")
        
        return self._process_next(data)