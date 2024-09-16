import re
import json
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

def pre_clean_text(text):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    non_english = re.compile(r'[^a-zA-Z\s.,!?]')
    clean_sentences = [sent for sent in sentences if not non_english.search(sent)]
    return ' '.join(clean_sentences)

def load_transcript(file_path):
    with open(file_path, 'r') as f:
        return f.read()

def load_slide_analyses(directory):
    analyses = {}
    for filename in os.listdir(directory):
        if filename.endswith('_analysis.json'):
            with open(os.path.join(directory, filename), 'r') as file:
                analyses[filename] = json.load(file)
    return analyses

def split_text_to_the_chunk(cleaned_text, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    return text_splitter.split_text(cleaned_text)