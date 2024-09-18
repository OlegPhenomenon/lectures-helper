from dataclasses import dataclass, field
from typing import Dict

@dataclass
class LectureProcessorConfig:
    base_path: str = "courses"
    # openai or ollama
    analyzer_type: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    processing_steps: Dict[str, bool] = field(default_factory=lambda: {
        "transcription": True,
        "pdf_to_image": True,
        "image_analysis": True,
        "slide_analysis": True,
        "lecture_data": True,
        "summarize_lecture": True,
        "format_lecture_data": True,
        "translate_lecture_data": True,
        "generate_lecture_questions": True,
        "practice_content": True,  # Добавлен новый шаг обработки
        "pdf_generation": True
    })