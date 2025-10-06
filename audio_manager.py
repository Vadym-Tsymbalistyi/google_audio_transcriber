import os
import logging

class AudioManager:
    def __init__(self, workspace):
        self.logger = logging.getLogger("AudioManager")
        self.logger.debug("Initializing AudioManager with workspace: %s", workspace)

        self.workspace = workspace
        os.makedirs(workspace, exist_ok=True)
        self.logger.debug("Workspace directory ensured: %s", workspace)

    def get_local_audio_path(self, filename):
        path = os.path.join(self.workspace, filename)
        self.logger.debug("Local audio path for '%s': %s", filename, path)
        return path

    def get_local_transcript_path(self, audio_filename):
        path = os.path.join(self.workspace, audio_filename.rsplit(".", 1)[0] + ".txt")
        self.logger.debug("Local transcript path for '%s': %s", audio_filename, path)
        return path

    def is_transcribed(self, audio_filename):
        path = self.get_local_transcript_path(audio_filename)
        exists = os.path.exists(path)
        self.logger.debug("Check if transcript exists for '%s': %s", audio_filename, exists)
        return exists
