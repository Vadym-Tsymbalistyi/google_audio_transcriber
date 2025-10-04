import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import Config

class GoogleDriveClient:
    def __init__(self, credentials_path='client_secret_241925377185-6im4o0aamidu4i1ec7id0hc1a5vt6glm.apps.googleusercontent.com.json'):
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

    def list_audio_files(self):
        results = self.service.files().list(
            q=f"'{Config.DRIVE_FOLDER_ID}' in parents and mimeType contains 'audio/'",
            pageSize=100,
            fields="files(id, name)"
        ).execute()
        return results.get('files', [])

    def copy_to_workspace_folder(self):
        files = self.list_audio_files()
        if not files:
            print("Audio files were not found for copying.")
            return []

        copied_files = []
        for file in files:
            copy_metadata = {
                'name': file['name'],
                'parents': [Config.WORKSPACE_FOLDER_ID]
            }
            copied = self.service.files().copy(
                fileId=file['id'],
                body=copy_metadata
            ).execute()
            copied_files.append({'id': copied['id'], 'name': copied['name']})
            print(f"File {file['name']} copied in a work folder Drive.")
        return copied_files

