from dataclasses import dataclass, field
from typing import Dict

@dataclass
class LectureProcessorConfig:
    base_path: str = "cloud_native_lessons"
    topic: str = "Cloud Native Applications on Kubernetes"
    analyzer_type: str = "openai"
    ollama_url: str = "http://localhost:11434"
    processing_steps: Dict[str, bool] = field(default_factory=lambda: {
        "transcription": False,
        "pdf_to_image": False,
        "image_analysis": False,
        "slide_analysis": False,
        "lecture_data": False,
        "summarize_lecture": False,
        "format_lecture_data": False,
        "translate_lecture_data": False,
        "pdf_generation": True
    })