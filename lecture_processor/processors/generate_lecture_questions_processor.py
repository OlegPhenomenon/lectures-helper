from ..factory.generate_lecture_questions_factory import GenerateLectureQuestionsFactory
from .base_processor import BaseProcessor

class GenerateLectureQuestionsProcessor(BaseProcessor):
    def process(self, data):
        analyzer_type = data.get('analyzer_type', 'openai')
        
        analyzer = GenerateLectureQuestionsFactory.get_analyzer(analyzer_type)
        analyzer.process_batch(data['translated_lecture_data_path'], data['generated_lecture_questions_path'])
        
        print(f"Lecture questions generated. Result saved in {data['generated_lecture_questions_path']}")
        
        return self._process_next(data)