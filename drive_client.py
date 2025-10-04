import os
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import Config

class GoogleDriveClient:
    def __init__(self, credentials_path='client_secret.json'):
        self.creds = None
        self.credentials_path = credentials_path
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

    def _file_exists_in_folder(self, file_name: str, folder_id: str) -> dict | None:
        query = f"'{folder_id}' in parents and name='{file_name}'"
        files = self.service.files().list(q=query, fields="files(id, name)").execute().get('files', [])
        return files[0] if files else None

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
            print("Audio files not found for copying.")
            return []

        copied_files = []
        for file in files:
            existing_file = self._file_exists_in_folder(file['name'], Config.WORKSPACE_FOLDER_ID)
            if existing_file:
                print(f"File {file['name']} are already in the work folder, pass copi.")
                copied_files.append({'id': existing_file['id'], 'name': existing_file['name']})
                continue

            copied = self.service.files().copy(
                fileId=file['id'],
                body={'name': file['name'], 'parents': [Config.WORKSPACE_FOLDER_ID]}
            ).execute()
            copied_files.append({'id': copied['id'], 'name': copied['name']})
            print(f"File {file['name']} copied in a work folder Drive.")
        return copied_files

    def download_file(self, file_id: str, destination_path: str):
        if os.path.exists(destination_path):
            print(f"File {destination_path} already exists locally, pass download.")
            return

        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        request = self.service.files().get_media(fileId=file_id)
        with open(destination_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    print(f"Download {int(status.progress() * 100)}%")
        print(f"The file is downloaded locally: {destination_path}")

    def upload_file(self, local_path: str, folder_id: str) -> str:
        file_name = os.path.basename(local_path)
        existing_file = self._file_exists_in_folder(file_name, folder_id)
        if existing_file:
            print(f"File {file_name} already in the folderDrive (id={existing_file['id']}), пропускаємо завантаження.")
            return existing_file['id']

        media = MediaFileUpload(local_path)
        uploaded_file = self.service.files().create(
            body={'name': file_name, 'parents': [folder_id]},
            media_body=media,
            fields='id'
        ).execute()
        print(f"File {file_name} download to Drive (id={uploaded_file['id']})")
        return uploaded_file['id']
