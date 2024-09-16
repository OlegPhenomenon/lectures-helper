from .base_processor import BaseProcessor
import json

class LectureDataProcessor(BaseProcessor):
    def process(self, data):
        # Загрузка данных из lecture_with_slides.json
        with open(data['lecture_with_slides_path'], 'r') as f:
            lecture_data = json.load(f)
        
        # Загрузка данных из source_data.json
        with open(data['source_data_path'], 'r') as f:
            source_data = json.load(f)

        # Создание словаря для хранения результатов
        result = {}

        # Обработка данных
        for item in lecture_data:
            if item['result']:
                slide_number = item['slide_number'][:-4]  # Удаление последних 4 символов
                
                # Поиск соответствующих chunk'ов в source_data
                chunks = [sd['chunk'] for sd in source_data if sd['slide_number'][:-4] == slide_number]
                
                # Добавление или обновление данных в результирующем словаре
                if slide_number in result:
                    result[slide_number].extend(chunks)
                else:
                    result[slide_number] = chunks

        # Сохранение результата в JSON файл
        with open(data['processed_lecture_data_path'], 'w') as f:
            json.dump(result, f, indent=2)

        print("Обработка завершена. Результат сохранен в файл:", data['processed_lecture_data_path'])

        return self._process_next(data)