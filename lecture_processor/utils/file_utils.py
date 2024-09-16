import os
from typing import List, Dict

def get_lecture_directories(base_path: str) -> List[str]:
    """
    Возвращает список директорий лекций, исключая те, где есть файл .skip
    """
    lecture_dirs = []
    for item in os.listdir(base_path):
        full_path = os.path.join(base_path, item)
        if os.path.isdir(full_path) and not os.path.exists(os.path.join(full_path, '.skip')):
            lecture_dirs.append(full_path)
    return sorted(lecture_dirs)

def get_lecture_files(lecture_dir: str) -> Dict[str, str]:
    """
    Возвращает словарь с путями к файлам лекции
    """
    return {
        "video_path": os.path.join(lecture_dir, "lecture_video.mp4"),
        "pdf_path": os.path.join(lecture_dir, "lecture_slides.pdf"),
        "transcript_path": os.path.join(lecture_dir, "lecture_transcript.txt"),
        "images_output_dir": os.path.join(lecture_dir, "images"),
        "slide_analyses_path": os.path.join(lecture_dir, "images_analysis"),
        "lecture_with_slides_path": os.path.join(lecture_dir, "lecture_with_slides.json"),
        "source_data_path": os.path.join(lecture_dir, "source_data.json"),
        "processed_lecture_data_path": os.path.join(lecture_dir, "processed_lecture_data.json"),
        "summarized_lecture_data_path": os.path.join(lecture_dir, "summarized_lecture_data.json"),
        "formatted_lecture_data_path": os.path.join(lecture_dir, "formatted_lecture_data.json"),
        "translated_lecture_data_path": os.path.join(lecture_dir, "translated_lecture_data.json"),
        "pdf_generation_path": os.path.join(lecture_dir, f"{os.path.basename(lecture_dir)}_result.pdf"),
    }