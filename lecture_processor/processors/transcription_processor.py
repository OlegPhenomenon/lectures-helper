from .base_processor import BaseProcessor
import whisper

class TranscriptionProcessor(BaseProcessor):
    def process(self, data):
        print(f'Транскрибирование видео: {data["video_path"]}')
        
        model = whisper.load_model('base')
        result = model.transcribe(data['video_path'])
        
        with open(data['transcript_path'], 'w') as f:
            f.write(result['text'])
        
        print('Транскрибирование завершено!')
        return self._process_next(data)