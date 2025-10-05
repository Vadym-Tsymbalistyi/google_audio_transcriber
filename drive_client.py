import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import Config

class GoogleDriveClient:
    def __init__(self):
        self.creds = None
        self.credentials_path = Config.CREDENTIALS_PATH
        self._authenticate()

    def _authenticate(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, Config.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

        self.service = build('drive', 'v3', credentials=self.creds)

    def list_audio_files(self) -> list:
        results = self.service.files().list(
            q=f"'{Config.DRIVE_FOLDER_ID}' in parents and mimeType contains 'audio/'",
            pageSize=100,
            fields="files(id, name)"
        ).execute()
        return results.get('files', [])

    def copy_to_workspace_folder(self) -> list:
        files = self.list_audio_files()
        if not files:
            print("No audio files to copy.")
            return []

        copied_files = []
        for file in files:
            existing = self.find_file_by_name(file['name'], Config.WORKSPACE_FOLDER_ID)
            if existing:
                print(f" File '{file['name']}' already in Workspace, skipping copy.")
                copied_files.append({'id': existing['id'], 'name': existing['name']})
                continue

            copied = self.service.files().copy(
                fileId=file['id'],
                body={'name': file['name'], 'parents': [Config.WORKSPACE_FOLDER_ID]}
            ).execute()

            print(f" Copied: {file['name']}")
            copied_files.append({'id': copied['id'], 'name': copied['name']})
        return copied_files

    def download_file(self, file_id: str, destination_path: str):
        if os.path.exists(destination_path):
            return
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        request = self.service.files().get_media(fileId=file_id)
        with open(destination_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

    def upload_file(self, local_path: str) -> str:
        folder_id = Config.WORKSPACE_FOLDER_ID
        file_name = os.path.basename(local_path)
        media = MediaFileUpload(local_path, mimetype='text/plain')
        uploaded_file = self.service.files().create(
            body={'name': file_name, 'parents': [folder_id]},
            media_body=media,
            fields='id'
        ).execute()
        return uploaded_file['id']

    def find_file_by_name(self, file_name, folder_id):
        query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        return files[0] if files else None

    def copy_sheet_template_to_workspace(self) -> dict:
        copied_file = self.service.files().copy(
            fileId=Config.SHEET_TEMPLATE_ID,
            body={'name': 'Workspace Sheet Copy', 'parents': [Config.WORKSPACE_FOLDER_ID]}
        ).execute()
        print(f" Sheet template copied: {copied_file['name']}")
        return {'id': copied_file['id'], 'name': copied_file['name']}
