import os
from drive_client import GoogleDriveClient
from audio_manager import AudioManager
from transcriber import Transcriber
from config import Config

class MainController:
    def __init__(self):
        self.drive_client = GoogleDriveClient()
        self.audio_manager = AudioManager(Config.WORKSPACE)
        self.transcriber = Transcriber()

    def process_files(self):
        copied_files = self.drive_client.copy_to_workspace_folder()
        if not copied_files:
            print("No files to process.")
            return

        # Download locally
        for f in copied_files:
            local_path = self.audio_manager.get_local_audio_path(f['name'])
            if not os.path.exists(local_path):
                self.drive_client.download_file(f['id'], local_path)

        # Transcribution and download on Drive
        for f in copied_files:
            audio_name = f['name']
            local_audio_path = self.audio_manager.get_local_audio_path(audio_name)
            local_transcript_path = self.audio_manager.get_local_transcript_path(audio_name)

            if self.audio_manager.is_transcribed(audio_name):
                print(f"File {audio_name} already transcribed, pass.")
                self.drive_client.upload_file(local_transcript_path, Config.WORKSPACE_FOLDER_ID)
                continue

            transcript_text = self.transcriber.transcribe(local_audio_path)
            with open(local_transcript_path, "w", encoding="utf-8") as f_txt:
                f_txt.write(transcript_text)
            print(f"File {audio_name} transcribed locally.")

            self.drive_client.upload_file(local_transcript_path, Config.WORKSPACE_FOLDER_ID)
            print(f"Transcript {os.path.basename(local_transcript_path)} download to Google Drive.\n")
