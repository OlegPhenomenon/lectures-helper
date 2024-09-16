# python -m lecture_processor.main

from .processors.transcription_processor import TranscriptionProcessor
from .processors.pdf_to_image_processor import PDFToImageProcessor
from .processors.image_analysis_processor import ImageAnalysisProcessor
from .processors.slide_analysis_processor import SlideAnalysisProcessor
from .processors.lecture_data_processor import LectureDataProcessor
from .processors.summarize_lecture_processor import SummarizeLectureProcessor
from .processors.format_lecture_data_processor import FormatLectureDataProcessor
from .processors.pdf_generation_processor import PDFGenerationProcessor
from .processors.translate_lecture_data_processor import TranslateLectureDataProcessor
from .utils.file_utils import get_lecture_directories, get_lecture_files
from .config import LectureProcessorConfig
import os

def build_processing_chain(config, processors):
    """
    Динамически строит цепочку обработки на основе конфигурации.
    """
    chain = None
    last = None
    for processor_name, processor in processors.items():
        if config.processing_steps.get(processor_name, True):
            if chain is None:
                chain = processor
            else:
                last.set_next(processor)
            last = processor
    return chain

def process_lecture(lecture_dir: str, config: LectureProcessorConfig):
    # Создаем процессоры
    processors = {
        "transcription": TranscriptionProcessor(),
        "pdf_to_image": PDFToImageProcessor(),
        "image_analysis": ImageAnalysisProcessor(),
        "slide_analysis": SlideAnalysisProcessor(),
        "lecture_data": LectureDataProcessor(),
        "summarize_lecture": SummarizeLectureProcessor(),
        "format_lecture_data": FormatLectureDataProcessor(),
        "translate_lecture_data": TranslateLectureDataProcessor(),
        "pdf_generation": PDFGenerationProcessor()
    }

    # Получаем пути к файлам для текущей лекции
    lecture_files = get_lecture_files(lecture_dir)

    # Объединяем данные конфигурации и пути к файлам
    initial_data = {
        **lecture_files,
        "topic": config.topic,
        "analyzer_type": config.analyzer_type,
        "ollama_url": config.ollama_url,
    }

    # Создаем необходимые директории
    os.makedirs(initial_data['images_output_dir'], exist_ok=True)
    os.makedirs(initial_data['slide_analyses_path'], exist_ok=True)

    # Строим динамическую цепочку обработки
    processing_chain = build_processing_chain(config, processors)

    # Запускаем цепочку обработки
    if processing_chain:
        final_result = processing_chain.process(initial_data)
        print(f"Обработка лекции {lecture_dir} завершена. Результат:", final_result)
    else:
        print(f"Ошибка: не удалось построить цепочку обработки для лекции {lecture_dir}.")

def main():
    config = LectureProcessorConfig()
    lecture_dirs = get_lecture_directories(config.base_path)

    for lecture_dir in lecture_dirs:
        process_lecture(lecture_dir, config)

if __name__ == "__main__":
    main()