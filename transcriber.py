import whisper
import  os
class Transcriber:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_path):
        print(f"We transcribe the file{os.path.basename(audio_path)} ...")
        result = self.model.transcribe(audio_path)
        return result["text"]
