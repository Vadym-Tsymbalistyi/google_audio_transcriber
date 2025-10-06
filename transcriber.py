import whisper
import os
import logging

class Transcriber:
    def __init__(self, model_name="small"):
        self.logger = logging.getLogger("Transcriber")
        self.logger.debug("Loading Whisper model '%s'...", model_name)
        self.model = whisper.load_model(model_name)
        self.logger.info("Whisper model '%s' loaded successfully.", model_name)

    def transcribe(self, audio_path):
        file_name = os.path.basename(audio_path)
        self.logger.info("Starting transcription for file: %s", file_name)

        result = self.model.transcribe(
            audio_path,
            task="transcribe",
            language="uk",
            temperature=0.0
        )
        text = result["text"].strip()
        self.logger.info("Transcription completed for file: %s", file_name)
        return text
