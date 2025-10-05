import os
import gspread
from drive_client import GoogleDriveClient
from audio_manager import AudioManager
from transcriber import Transcriber
from config import Config

class MainController:
    def __init__(self):
        self.drive_client = GoogleDriveClient()
        self.audio_manager = AudioManager(Config.WORKSPACE)
        self.transcriber = Transcriber()
        self.gc = gspread.service_account(filename='test.json')
        self.sh = self.gc.open_by_key(Config.GOOGLE_SHEET_ID)
        self.worksheet = self.sh.sheet1

    def process_files(self):
        copied_files = self.drive_client.copy_to_workspace_folder()
        if not copied_files:
            print("No new audio files found.")
            return

        data = self.worksheet.get_all_values()
        headers = data[1]  # second row
        try:
            date_col_index = headers.index("Дата") + 1
        except ValueError:
            print("'Дата' column not found in the sheet!")
            return

        for file in copied_files:
            audio_name = file['name']
            local_audio_path = self.audio_manager.get_local_audio_path(audio_name)
            local_transcript_path = self.audio_manager.get_local_transcript_path(audio_name)

            if not os.path.exists(local_audio_path):
                print(f"Downloading audio: {audio_name}")
                self.drive_client.download_file(file['id'], local_audio_path)

            transcript_name = os.path.basename(local_transcript_path)
            existing_transcript = self.drive_client.find_file_by_name(transcript_name, Config.WORKSPACE_FOLDER_ID)

            if existing_transcript:
                print(f"Transcript exists on Drive: {transcript_name}")
                self.drive_client.download_file(existing_transcript['id'], local_transcript_path)
                with open(local_transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                    transcript_text = f.read()
            else:
                print(f"Transcribing audio: {audio_name}")
                transcript_text = self.transcriber.transcribe(local_audio_path)
                with open(local_transcript_path, "w", encoding="utf-8") as f:
                    f.write(transcript_text)
                self.drive_client.upload_file(local_transcript_path)
                print(f"Transcript uploaded to Drive: {transcript_name}")

            col_values = self.worksheet.col_values(date_col_index)[3:]
            for idx, val in enumerate(col_values):
                if not val:
                    row_idx = idx + 4
                    self.worksheet.update_cell(row_idx, date_col_index, transcript_text)
                    print(f"Transcript added to row {row_idx}, column 'Дата'")
                    break
            else:
                next_row_idx = len(col_values) + 4
                self.worksheet.update_cell(next_row_idx, date_col_index, transcript_text)
                print(f"Transcript added to new row {next_row_idx}, column 'Дата'")
