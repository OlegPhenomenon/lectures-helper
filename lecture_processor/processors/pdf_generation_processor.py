import json
from .base_processor import BaseProcessor
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable, ListItem, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import black, darkgray
import os
import re
import markdown
from xml.etree import ElementTree
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch

class PDFGenerationProcessor(BaseProcessor):
    def __init__(self):
        super().__init__()
        self.styles = getSampleStyleSheet()
        
        # Register fonts with Cyrillic support
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'fonts/dejavu-sans/DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', 'fonts/dejavu-sans/DejaVuSans-Bold.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-Oblique', 'fonts/dejavu-sans/DejaVuSans-Oblique.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVuSans-BoldOblique', 'fonts/dejavu-sans/DejaVuSans-BoldOblique.ttf'))

        # Register font family
        pdfmetrics.registerFontFamily('DejaVuSans',
            normal='DejaVuSans',
            bold='DejaVuSans-Bold',
            italic='DejaVuSans-Oblique',
            boldItalic='DejaVuSans-BoldOblique',
        )
        
        # Update existing styles
        self.styles['Normal'].fontName = 'DejaVuSans'
        self.styles['Normal'].fontSize = 10
        self.styles['Normal'].leading = 14
        
        # Add new styles
        self.styles.add(ParagraphStyle(
            name='Justify',
            fontName='DejaVuSans',
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBodyText',
            fontName='DejaVuSans',
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            fontName='DejaVuSans',
            fontSize=10,
            leading=14,
            leftIndent=20,
            bulletIndent=10,
            firstLineIndent=-10,
            spaceAfter=3
        ))
        
        # Update heading styles
        self.styles['Heading1'].fontName = 'DejaVuSans-Bold'
        self.styles['Heading1'].fontSize = 20
        self.styles['Heading1'].leading = 24
        self.styles['Heading1'].textColor = black
        self.styles['Heading1'].spaceAfter = 12

        self.styles['Heading2'].fontName = 'DejaVuSans-Bold'
        self.styles['Heading2'].fontSize = 18
        self.styles['Heading2'].leading = 22
        self.styles['Heading2'].textColor = darkgray
        self.styles['Heading2'].spaceAfter = 10

        self.styles['Heading3'].fontName = 'DejaVuSans-Bold'
        self.styles['Heading3'].fontSize = 16
        self.styles['Heading3'].leading = 20
        self.styles['Heading3'].textColor = darkgray
        self.styles['Heading3'].spaceAfter = 8
        
        self.styles['Normal'].fontName = 'DejaVuSans'
        self.styles['CustomBodyText'].fontName = 'DejaVuSans'
        self.styles['BulletPoint'].fontName = 'DejaVuSans'

        # Add new style for image captions
        self.styles.add(ParagraphStyle(
            name='Caption',
            fontName='DejaVuSans',
            fontSize=8,
            leading=10,
            # alignment=TA_CENTER,
            spaceAfter=6
        ))

    def process(self, data):
        with open(data['translated_lecture_data_path'], 'r', encoding='utf-8') as file:
            formatted_data = json.load(file)

        with open(data['generated_lecture_questions_path'], 'r', encoding='utf-8') as file:
            questions_data = json.load(file)

        processed_data = self._process_data(formatted_data)
        self._create_pdf(processed_data, questions_data, data['pdf_generation_path'], data['images_output_dir'], data['notes_path'], data.get('practice_translated_path'))

        return {"status": "PDF generated successfully", "path": data['pdf_generation_path']}

    def _process_data(self, data):
        processed_data = {}
        for item in data:
            slide_number = self._parse_slide_number(item.get('slide_number', ''))
            output = item.get('output', '')
            
            if slide_number in processed_data:
                processed_data[slide_number] += "\n\n" + output
            else:
                processed_data[slide_number] = output
        
        return processed_data

    def _parse_slide_number(self, slide_number):
        # Извлекаем номер страницы из ключа
        match = re.search(r'page_(\d+)', slide_number)
        if match:
            return f"page_{match.group(1)}"
        return slide_number  # Возвращаем исходное значение, если парсинг не удался

    def _create_pdf(self, processed_data, questions_data, output_path, images_dir, notes_path, practice_translated_path):
        print("Processed data keys:", processed_data.keys())
        
        doc = SimpleDocTemplate(output_path, pagesize=letter, encoding='utf-8')
        story = []

        if 'title' in processed_data:
            story.append(Paragraph(processed_data['title'], self.styles['Heading1']))
            story.append(Spacer(1, 12))

        sorted_keys = sorted(processed_data.keys(), key=lambda x: int(x.split('_')[1]) if x != 'title' else 0)

        for key in sorted_keys:
            print(f"Processing key: {key}")

            if key == 'title':
                continue

            slide_number = key.split('_')[1]
            content = processed_data[key]

            image_file = f"page_{slide_number}.png"
            image_path = os.path.join(images_dir, image_file)
            if os.path.exists(image_path):
                img = Image(image_path, width=500, height=300)
                story.append(img)
                story.append(Spacer(1, 12))

            html_content = markdown.markdown(content)
            flowables = self._html_to_reportlab(html_content)
            story.extend(flowables)
            story.append(Spacer(1, 12))

        # Добавляем вопросы в конце материала
        if questions_data and "questions" in questions_data:
            story.append(PageBreak())
            story.append(Paragraph("Вопросы по лекции:", self.styles['Heading1']))
            for i, question in enumerate(questions_data["questions"], 1):
                story.append(Paragraph(f"{i}. {question}", self.styles['BulletPoint']))
            story.append(Spacer(1, 12))

        if practice_translated_path and os.path.exists(practice_translated_path):
            story.append(PageBreak())
            story.append(Paragraph("Практический материал", self.styles['Heading1']))
            story.append(Spacer(1, 12))

            with open(practice_translated_path, 'r', encoding='utf-8') as practice_file:
                practice_content = practice_file.read()

            # Set base path for images
            self.practice_base_path = os.path.dirname(practice_translated_path)

            # Convert the entire Markdown content to HTML
            try:
                html_content = markdown.markdown(practice_content)
                flowables = self._html_to_reportlab(html_content)
                story.extend(flowables)
            except Exception as e:
                # If processing fails, add as plain text
                print(f"Error processing practical material: {e}")
                story.append(Paragraph(practice_content, self.styles['CustomBodyText']))

            # Разделяем содержимое на строки
            lines = practice_content.split('\n')
            
            for line in lines:
                if line.startswith('# '):
                    story.append(Paragraph(line[2:], self.styles['Heading1']))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], self.styles['Heading2']))
                elif line.startswith('### '):
                    story.append(Paragraph(line[4:], self.styles['Heading3']))
                elif line.startswith('!['):
                    # Обработка изображений
                    img_parts = line.split('](')
                    img_alt = img_parts[0][2:]
                    img_path = img_parts[1][:-1]
                    img_full_path = os.path.join(os.path.dirname(practice_translated_path), img_path)
                    if os.path.exists(img_full_path):
                        img = Image(img_full_path, width=6*inch, height=4*inch)
                        story.append(img)
                        story.append(Paragraph(img_alt, self.styles['Caption']))
                    else:
                        story.append(Paragraph(f"Изображение не найдено: {img_path}", self.styles['Normal']))
                elif line.strip().startswith('* '):
                    story.append(Paragraph(line.strip()[2:], self.styles['BulletPoint']))
                elif line.strip():
                    story.append(Paragraph(line, self.styles['Normal']))
                else:
                    story.append(Spacer(1, 6))

            story.append(Spacer(1, 12))
        else:
          print('-----')
          print(practice_translated_path)
          print("Файл с практическим материалом не найден")
          print('-----')
        if os.path.exists(notes_path):
            story.append(Paragraph("Заметки по курсу", self.styles['Heading1']))
            story.append(Spacer(1, 12))
            
            with open(notes_path, 'r', encoding='utf-8') as notes_file:
                notes_content = notes_file.read()
            
            # Попробуем обработать содержимое как Markdown
            try:
                html_content = markdown.markdown(notes_content)
                notes_flowables = self._html_to_reportlab(html_content)
                story.extend(notes_flowables)
            except:
                # Если не удалось обработать как Markdown, добавляем как простой текст
                story.append(Paragraph(notes_content, self.styles['CustomBodyText']))

        doc.build(story)

    def _get_questions_for_slide(self, questions_data, slide_index):
        for item in questions_data:
            slide_number = item['slide_number'].lower().replace('page_', '')
            if slide_number.isdigit() and int(slide_number) == slide_index:
                return item['questions']
        print(f"Вопросы не найдены для слайда {slide_index}")
        return []

    def _html_to_reportlab(self, html):
        wrapped_html = f"<root>{html}</root>"
        root = ElementTree.fromstring(wrapped_html)
        return self._process_element(root)

    def _process_element(self, element):
        items = []
        process_children = True

        if element.tag == 'root':
            for child in element:
                items.extend(self._process_element(child))
            process_children = False
        elif element.tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            style = self.styles.get(f'Heading{element.tag[1]}', self.styles['Heading3'])
            text = self._process_inline_markup(element)
            items.append(Paragraph(text, style))
            items.append(Spacer(1, style.spaceAfter))
            process_children = False
        elif element.tag == 'p':
            text = self._process_inline_markup(element)
            items.append(Paragraph(text, self.styles['CustomBodyText']))
            process_children = False
        elif element.tag in ['ul', 'ol']:
            sub_items = []
            for li in element:
                li_content = self._process_inline_markup(li)
                sub_items.append(Paragraph(li_content, self.styles['BulletPoint']))
            bullet_type = 'bullet' if element.tag == 'ul' else '1'
            items.append(ListFlowable(sub_items, bulletType=bullet_type, leftIndent=20, spaceBefore=6, spaceAfter=6))
            process_children = False
        elif element.tag == 'img':
            # Handle image
            img_src = element.attrib.get('src')
            if img_src:
                img_full_path = os.path.join(self.practice_base_path, img_src)
                if os.path.exists(img_full_path):
                    img = Image(img_full_path, width=6*inch, height=4*inch)
                    items.append(img)
                    if 'alt' in element.attrib:
                        items.append(Paragraph(element.attrib['alt'], self.styles.get('Caption', self.styles['Normal'])))
                else:
                    items.append(Paragraph(f"Изображение не найдено: {img_src}", self.styles['Normal']))
            process_children = False
        elif element.tag == 'a':
            # Handle hyperlinks
            href = element.attrib.get('href', '')
            link_text = self._process_inline_markup(element)
            text = f'<link href="{href}">{link_text}</link>'
            items.append(Paragraph(text, self.styles['CustomBodyText']))
            process_children = False
        else:
            text = self._process_inline_markup(element)
            if text:
                items.append(Paragraph(text, self.styles['CustomBodyText']))

        if process_children:
            for child in element:
                items.extend(self._process_element(child))

        if element.tail and element.tail.strip():
            items.append(Paragraph(element.tail.strip(), self.styles['CustomBodyText']))

        return items

    def _process_inline_markup(self, element):
        text = []
        if element.text:
            text.append(element.text)
        for child in element:
            # Recursively process child elements
            child_text = self._process_inline_markup(child)
            if child.tag in ['strong', 'b']:
                text.append(f"<b>{child_text}</b>")
            elif child.tag in ['em', 'i']:
                text.append(f"<i>{child_text}</i>")
            elif child.tag == 'br':
                text.append('<br/>')
            else:
                text.append(child_text)
            if child.tail:
                text.append(child.tail)
        return ''.join(text)

    def _get_element_text(self, element):
        return ''.join(element.itertext()).strip() if element.text else ''
