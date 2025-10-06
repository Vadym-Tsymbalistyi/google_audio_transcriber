import os
import gspread
from drive_client import GoogleDriveClient
from audio_manager import AudioManager
from transcriber import Transcriber
from ai_manager import AIManager
from config import Config
from sheet_manager import SheetManager

class MainController:
    def __init__(self):
        self.drive_client = GoogleDriveClient()
        self.audio_manager = AudioManager(Config.WORKSPACE)
        self.transcriber = Transcriber()
        self.ai_manager = AIManager()

        self.gc = gspread.service_account(Config.CREDENTIALS)
        self.sh = self.gc.open_by_key(Config.GOOGLE_SHEET_ID)
        self.worksheet = self.sh.sheet1
        self.sheet_manager = SheetManager(self.worksheet)

        # copied_file_info = self.drive_client.copy_sheet_template_to_workspace()
        # print(f"Copied sheet: {copied_file_info['name']} with ID {copied_file_info['id']}")

    def get_transcript(self, audio_name, local_audio_path, local_transcript_path):
        existing_transcript = self.drive_client.find_file_by_name(
            os.path.basename(local_transcript_path), Config.WORKSPACE_FOLDER_ID
        )
        if existing_transcript:
            self.drive_client.download_file(existing_transcript['id'], local_transcript_path)
            with open(local_transcript_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        else:
            transcript_text = self.transcriber.transcribe(local_audio_path)
            with open(local_transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript_text)
            self.drive_client.upload_file(local_transcript_path)
            return transcript_text

    def find_next_empty_row(self, col_index: int, start_row: int = 4) -> int:
        col_values = self.worksheet.col_values(col_index)
        for i in range(start_row-1, len(col_values)):
            if not col_values[i].strip():
                return i + 1
        return len(col_values) + 1

    def process_files(self):
        copied_files = self.drive_client.copy_to_workspace_folder()
        if not copied_files:
            return

        headers = self.worksheet.row_values(2)
        try:
            transcript_col_index = headers.index("Дата") + 1
        except ValueError:
            return

        for file in copied_files:
            audio_name = file['name']
            local_audio_path = self.audio_manager.get_local_audio_path(audio_name)
            local_transcript_path = self.audio_manager.get_local_transcript_path(audio_name)

            if not os.path.exists(local_audio_path):
                self.drive_client.download_file(file['id'], local_audio_path)

            transcript_text = self.get_transcript(audio_name, local_audio_path, local_transcript_path)
            analysis_result = self.ai_manager.analyze_transcript(transcript_text)

            row_number = self.find_next_empty_row(transcript_col_index)
            self.worksheet.update_cell(row_number, transcript_col_index, transcript_text)
            self.sheet_manager.update_row_with_analysis(row_number, analysis_result)
