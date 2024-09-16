import json
from .base_processor import BaseProcessor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.colors import black
import os
import re
import markdown
from xml.etree import ElementTree
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class PDFGenerationProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY))
        
        # Регистрируем шрифт с поддержкой кириллицы
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/dejavu-sans/DejaVuSans.ttf'))
        
        # Модифицируем существующие стили для заголовков
        self.styles['Heading1'].fontName = 'DejaVuSans'
        self.styles['Heading1'].fontSize = 24
        self.styles['Heading1'].leading = 28
        self.styles['Heading1'].textColor = black

        self.styles['Heading2'].fontName = 'DejaVuSans'
        self.styles['Heading2'].fontSize = 20
        self.styles['Heading2'].leading = 24
        self.styles['Heading2'].textColor = black

        self.styles['Heading3'].fontName = 'DejaVuSans'
        self.styles['Heading3'].fontSize = 16
        self.styles['Heading3'].leading = 20
        self.styles['Heading3'].textColor = black

        self.styles['Normal'].fontName = 'DejaVuSans'
        self.styles['Justify'].fontName = 'DejaVuSans'

    def process(self, data):
        with open(data['translated_lecture_data_path'], 'r', encoding='utf-8') as file:
            formatted_data = json.load(file)

        processed_data = self._process_data(formatted_data)
        self._create_pdf(processed_data, data['pdf_generation_path'], data['images_output_dir'])

        return {"status": "PDF generated successfully", "path": data['pdf_generation_path']}

    def _process_data(self, data):
        processed_data = {}
        for item in data:
            slide_number = item.get('slide_number', '')
            output = item.get('output', '')
            parsed_slide_number = self._parse_slide_number(slide_number)
            if parsed_slide_number in processed_data:
                processed_data[parsed_slide_number] += "\n" + output
            else:
                processed_data[parsed_slide_number] = output
        return processed_data

    def _parse_slide_number(self, slide_number):
        return slide_number[:-6].split('.')[0].replace('_analysis', '')

    def _create_pdf(self, processed_data, output_path, images_dir):
        doc = SimpleDocTemplate(output_path, pagesize=letter, encoding='utf-8')
        story = []

        image_files = sorted(
            [f for f in os.listdir(images_dir) if f.endswith('.png')],
            key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf')
        )

        for image_file in image_files:
            image_key = os.path.splitext(image_file)[0]
            image_path = os.path.join(images_dir, image_file)

            img = Image(image_path, width=500, height=300)
            story.append(img)
            story.append(Spacer(1, 12))

            if image_key in processed_data:
                markdown_text = processed_data[image_key]
                html = markdown.markdown(markdown_text)
                story.extend(self._html_to_reportlab(html))
                story.append(Spacer(1, 12))

        doc.build(story)

    def _html_to_reportlab(self, html):
        wrapped_html = f"<root>{html}</root>"
        root = ElementTree.fromstring(wrapped_html)
        return self._process_element(root)

    def _process_element(self, element):
        items = []
        if element.tag == 'root':
            for child in element:
                items.extend(self._process_element(child))
        elif element.tag in ['h1', 'h2', 'h3', 'p']:
            style = self.styles['Heading1'] if element.tag == 'h1' else \
                    self.styles['Heading2'] if element.tag == 'h2' else \
                    self.styles['Heading3'] if element.tag == 'h3' else \
                    self.styles['Justify']
            items.append(Paragraph(self._get_element_text(element), style))
        elif element.tag in ['ul', 'ol']:
            sub_items = []
            for li in element:
                sub_items.append(ListItem(Paragraph(self._get_element_text(li), self.styles['Normal'])))
            bullet_type = 'bullet' if element.tag == 'ul' else '1'
            items.append(ListFlowable(sub_items, bulletType=bullet_type, start='•' if element.tag == 'ul' else 1))
        
        for child in element:
            items.extend(self._process_element(child))
        
        return items

    def _get_element_text(self, element):
        return ''.join(element.itertext()).strip() if element.text else ''
