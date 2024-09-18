import os
from typing import List, Dict, Tuple

def get_courses_and_lectures(base_path: str) -> List[Tuple[str, List[Tuple[str, str]]]]:
    """
    Возвращает список кортежей (путь_к_курсу, список_кортежей_лекций),
    где каждый кортеж лекции содержит (путь_к_лекции, тема_лекции),
    исключая курсы и лекции, где есть файл .skip
    """
    courses_and_lectures = []
    for course in os.listdir(base_path):
        course_path = os.path.join(base_path, course)
        if os.path.isdir(course_path):
            if os.path.exists(os.path.join(course_path, '.skip')):
                print(f"Пропускаем курс {course_path}, так как обнаружен файл .skip")
                continue
            
            lectures = []
            for lecture in os.listdir(course_path):
                lecture_path = os.path.join(course_path, lecture)
                if os.path.isdir(lecture_path):
                    if os.path.exists(os.path.join(lecture_path, '.skip')):
                        print(f"Пропускаем лекцию {lecture_path}, так как обнаружен файл .skip")
                    else:
                        topic = read_topic(lecture_path)
                        if topic:
                            lectures.append((lecture_path, topic))
                        else:
                            print(f"Пропускаем лекцию {lecture_path}, так как не найден файл topic.txt")
            
            if lectures:
                courses_and_lectures.append((course_path, sorted(lectures)))
    
    return courses_and_lectures

def read_topic(lecture_path: str) -> str:
    """
    Читает тему лекции из файла topic.txt в директории лекции
    """
    topic_file = os.path.join(lecture_path, 'topic.txt')
    if os.path.exists(topic_file):
        with open(topic_file, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""

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
        "generated_lecture_questions_path": os.path.join(lecture_dir, "generated_lecture_questions.json"),
        "notes_path": os.path.join(lecture_dir, "notes.txt"),
        "pdf_generation_path": os.path.join(lecture_dir, f"{os.path.basename(lecture_dir)}_result.pdf"),
        "practice_links_path": os.path.join(lecture_dir, "prictice_links.txt"),  # Исправлено название файла
        "practice_content_path": os.path.join(lecture_dir, "practice_content.md"),
        "practice_translated_path": os.path.join(lecture_dir, "practice_content/practice_content_translated.md"),
    }