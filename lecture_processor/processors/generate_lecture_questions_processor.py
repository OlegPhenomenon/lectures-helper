import logging
from ..factory.generate_lecture_questions_factory import GenerateLectureQuestionsFactory
from .base_processor import BaseProcessor

logging.basicConfig(level=logging.DEBUG)

class GenerateLectureQuestionsProcessor(BaseProcessor):
    def process(self, data):
        logging.debug("Starting GenerateLectureQuestionsProcessor")
        analyzer_type = data.get('analyzer_type', 'openai')
        logging.debug(f"Analyzer type: {analyzer_type}")
        
        analyzer = GenerateLectureQuestionsFactory.get_analyzer(analyzer_type)
        logging.debug(f"Input file: {data['translated_lecture_data_path']}")
        logging.debug(f"Output file: {data['generated_lecture_questions_path']}")
        analyzer.process_batch(data['translated_lecture_data_path'], data['generated_lecture_questions_path'])
        
        logging.debug(f"Lecture questions generated. Result saved in {data['generated_lecture_questions_path']}")
        
        return self._process_next(data)