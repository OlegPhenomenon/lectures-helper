from .base_processor import BaseProcessor
import fitz
import os

class PDFToImageProcessor(BaseProcessor):
    def process(self, data):
        print(f'Конвертация PDF в изображения: {data["pdf_path"]}')
        
        pdf_document = fitz.open(data['pdf_path'])
        
        for page_number in range(len(pdf_document)):
            page = pdf_document[page_number]
            pix = page.get_pixmap()
            image_path = os.path.join(data['images_output_dir'], f"page_{page_number + 1}.png")
            pix.save(image_path)
        
        pdf_document.close()
        print('Конвертация PDF в изображения завершена!')
        return self._process_next(data)