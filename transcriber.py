import whisper
import os

class Transcriber:
    def __init__(self, model_name="medium"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path):
        file_name = os.path.basename(audio_path)
        print(f" I transcribe the file: {file_name} ...")

        result = self.model.transcribe(
            audio_path,
            task="transcribe",
            language="uk",
            temperature=0.0
        )
        text = result["text"].strip()
        return text
