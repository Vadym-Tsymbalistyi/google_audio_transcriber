import os

class AudioManager:
    def __init__(self, workspace):
        self.workspace = workspace
        os.makedirs(workspace, exist_ok=True)

    def get_local_audio_path(self, filename):
        return os.path.join(self.workspace, filename)

    def get_local_transcript_path(self, audio_filename):
        return os.path.join(self.workspace, audio_filename.rsplit(".", 1)[0] + ".txt")

    def is_transcribed(self, audio_filename):
        return os.path.exists(self.get_local_transcript_path(audio_filename))
