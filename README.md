# Lecture Analyzer

## Project Description

This project is an automated tool for analyzing and processing lecture materials. It is designed to work with video lectures and accompanying PDF presentations, performing the following main tasks:

1. Video lecture transcription
2. Splitting PDF into individual slide images
3. Slide image analysis using the LLaVa language model
4. Matching video lecture content with corresponding slides
5. Editing and optimizing the resulting content
6. Processing additional practical materials
7. Translating content to Russian (optional)
8. Generating a final PDF file with combined materials
9. Generating questions based on the lecture content

## Project Structure

```
lecture_helper/
├── lecture_processor/
│   ├── __init__.py
│   ├── main.py
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── base_processor.py
│   │   ├── transcription_processor.py
│   │   ├── pdf_to_image_processor.py
│   │   ├── image_analysis_processor.py
│   │   ├── slide_analysis_processor.py
│   │   ├── lecture_data_processor.py
│   │   ├── pdf_generation_processor.py
│   │   ├── format_lecture_data_processor.py
│   │   └── summarize_lecture_data_processor.py
│   │   └── translate_lecture_data_processor.py
│   │   └── practice_content_processor.py
│   │   └── generate_lecture_questions_processor.py
│   ├── factory/
│   │   ├── __init__.py
│   │   └── analyzer_factory.py
│   │   └── format_lecture_data_factory.py
│   │   └── summarize_lecture_data_factory.py
│   │   └── translate_lecture_data_factory.py
│   │   └── generate_lecture_questions_factory.py
│   │   └── practice_content_factory.py
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── ollama_analyzer.py
│   │   └── openai_analyzer.py
│   │   └── ollama_summarize_lecture.py
│   │   └── openai_summarize_lecture.py
│   │   └── ollama_format_lecture_data.py
│   │   └── openai_format_lecture_data.py
│   │   └── ollama_translate_lecture_data.py
│   │   └── openai_translate_lecture_data.py
│   │   └── ollama_generate_lecture_questions.py
│   │   └── openai_generate_lecture_questions.py
│   │   └── ollama_practice_content.py
│   │   └── openai_practice_content.py
│   └── utils/
│       ├── __init__.py
│       └── text_utils.py
│       └── file_utils.py
└── requirements.txt
└── fonts/
    ├── dejavu-sans/
    │   ├── DejaVuSans.ttf
    │   ├── DejaVuSans-Bold.ttf
    │   ├── DejaVuSans-Oblique.ttf
    │   ├── DejaVuSans-BoldOblique.ttf
    │   └── DejaVuSans-ExtraLight.ttf
└── courses/
    ├── some_course/
    │   ├── 1_lecture/
    │   │   ├── lecture_video.mp4
    │   │   ├── lecture_slides.pdf
    │   │   ├── topic.txt
    │   │   ├── practice_links.txt
    │   │   ├── notes.txt
```

## Main Components

- `processors/`: Modules for processing various aspects of the lecture
- `factory/`: Factories for creating analyzer objects
- `analyzers/`: Implementations of different analyzers (Ollama, OpenAI)
- `utils/`: Helper utilities

## Usage

1. Place the video lecture and PDF presentation in the corresponding lecture directory (e.g., `cloud_native_lessons/1_lecture/`)
2. Ensure that the required files are present in the lecture directory:
   - `topic.txt`: Lecture topic
   - `practice_links.txt`: Links to practical materials (optional)
   - `notes.txt`: Additional notes (optional)
   - `lecture_video.mp4`: Video lecture
   - `lecture_slides.pdf`: PDF presentation
3. Run the main script to process the lecture materials
4. The script will generate a final PDF file with combined materials, including:
   - Slides with corresponding lecture content
   - Practical materials
   - Additional notes

## Note

If a `.skip` file is present in a lecture directory, that directory will be skipped during processing.

## Requirements

See `requirements.txt` for a list of required Python packages.

## Font

The project uses DejaVu Sans font family for PDF generation. Font files are located in the `fonts/dejavu-sans/` directory.

## How to run

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install git+https://github.com/openai/whisper.git
sudo apt update && sudo apt install ffmpeg
python -m lecture_processor.main
```
