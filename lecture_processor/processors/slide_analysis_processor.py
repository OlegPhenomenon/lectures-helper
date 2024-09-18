from ..factory.analyzer_factory import AnalyzerFactory
from ..utils.text_utils import pre_clean_text, load_transcript, load_slide_analyses
from .base_processor import BaseProcessor

class SlideAnalysisProcessor(BaseProcessor):
    def process(self, data):
        analyzer_type = data.get('analyzer_type', 'openai')
        
        transcript = load_transcript(data['transcript_path'])
        cleaned_text = pre_clean_text(transcript)
        slide_analyses = load_slide_analyses(data['slide_analyses_path'])
        
        analyzer = AnalyzerFactory.get_analyzer(analyzer_type)
        analyzer.process_batch(data['topic'], cleaned_text, slide_analyses, data['lecture_with_slides_path'])
        
        print(f"Анализ слайдов завершен. Результат сохранен в {data['lecture_with_slides_path']}")
        
        return self._process_next(data)