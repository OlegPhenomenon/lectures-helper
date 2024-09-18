from .base_processor import BaseProcessor
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import shutil
import html2text
from ..factory.translator_factory import TranslatorFactory

class PracticeContentProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.html2text_converter = html2text.HTML2Text()
        self.html2text_converter.ignore_links = False
        self.html2text_converter.ignore_images = False
        self.html2text_converter.ignore_emphasis = False
        self.html2text_converter.body_width = 0  # Отключаем перенос строк

    def process(self, data):
        print("Обработка практического контента начата")

        if 'practice_links_path' not in data:
            print("Ошибка: 'practice_links_path' отсутствует в данных")
            return self._process_next(data)

        practice_links_path = data['practice_links_path']
        print(f"Путь к файлу со ссылками: {practice_links_path}")

        if not os.path.exists(practice_links_path):
            print(f"Ошибка: Файл {practice_links_path} не существует")
            return self._process_next(data)

        practice_link = self._read_practice_link(practice_links_path)
        if practice_link:
            print(f"Найдена ссылка на практический материал: {practice_link}")
            data['practice_link'] = practice_link
            
            # Создаем отдельную папку для практического контента
            practice_dir = os.path.join(os.path.dirname(data['practice_links_path']), 'practice_content')
            os.makedirs(practice_dir, exist_ok=True)
            
            # Скачиваем HTML и изображения
            html_content, images = self._download_html_and_images(practice_link, os.path.join(practice_dir, 'images'))
            
            if html_content:
                # Сохраняем HTML контент
                html_file_path = os.path.join(practice_dir, 'practice_content.html')
                with open(html_file_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"HTML-контент сохранен в {html_file_path}")
                
                # Конвертируем HTML в Markdown
                markdown_content = self._convert_html_to_markdown(html_content)
                markdown_file_path = os.path.join(practice_dir, 'practice_content.md')
                with open(markdown_file_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"Markdown-контент сохранен в {markdown_file_path}")
                
                # Переводим Markdown-контент
                translator = TranslatorFactory.get_translator(data['analyzer_type'], {'ollama_url': data.get('ollama_url')})
                translated_content = translator.translate(markdown_content)
                translated_file_path = os.path.join(practice_dir, 'practice_content_translated.md')
                with open(translated_file_path, 'w', encoding='utf-8') as f:
                    f.write(translated_content)
                print(f"Переведенный Markdown-контент сохранен в {translated_file_path}")
                
                # Сохраняем информацию о скачанных изображениях и путях к файлам
                data['practice_images'] = images
                data['practice_html_path'] = html_file_path
                data['practice_markdown_path'] = markdown_file_path
                data['practice_translated_path'] = translated_file_path
            else:
                print("Не удалось скачать HTML-контент")
        else:
            print(f"Ссылка на практический материал не найдена в файле {practice_links_path}")

        print("Обработка практического контента завершена")
        return self._process_next(data)

    def _read_practice_link(self, practice_links_path):
        try:
            with open(practice_links_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                print(f"Содержимое файла {practice_links_path}: {content}")
                return content
        except Exception as e:
            print(f"Ошибка при чтении файла {practice_links_path}: {e}")
            return None

    def _download_html_and_images(self, url, images_output_dir):
        try:
            response = requests.get(url)
            response.raise_for_status()
            html_content = response.text
            
            # Создаем директорию для изображений
            os.makedirs(images_output_dir, exist_ok=True)
            
            # Парсим HTML и скачиваем изображения
            soup = BeautifulSoup(html_content, 'html.parser')
            images = []
            for img in soup.find_all('img'):
                img_url = urljoin(url, img['src'])
                img_filename = os.path.basename(urlparse(img_url).path)
                img_path = os.path.join(images_output_dir, img_filename)
                
                # Скачиваем изображение
                with requests.get(img_url, stream=True) as r:
                    r.raise_for_status()
                    with open(img_path, 'wb') as f:
                        shutil.copyfileobj(r.raw, f)
                
                # Обновляем src в HTML
                img['src'] = os.path.join('images', img_filename)
                images.append(img_path)
            
            # Обновляем HTML-контент с новыми путями к изображениям
            html_content = str(soup)
            
            return html_content, images
        except requests.RequestException as e:
            print(f"Ошибка при скачивании контента: {e}")
            return None, []

    def _convert_html_to_markdown(self, html_content):
        return self.html2text_converter.handle(html_content)