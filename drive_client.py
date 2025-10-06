import os
import pickle
import logging
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from config import Config

class GoogleDriveClient:
    def __init__(self):
        self.logger = logging.getLogger("GoogleDriveClient")
        self.logger.debug("Initializing GoogleDriveClient...")
        self.creds = None
        self.credentials_path = Config.CREDENTIALS_PATH
        self._authenticate()
        self.logger.debug("GoogleDriveClient initialized successfully.")

    def _authenticate(self):
        self.logger.debug("Authenticating with Google Drive...")
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
                self.logger.debug("Loaded credentials from token.pickle")
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
                self.logger.debug("Refreshed expired credentials")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, Config.SCOPES)
                self.creds = flow.run_local_server(port=0)
                self.logger.debug("Obtained new credentials via OAuth flow")
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)
                self.logger.debug("Saved credentials to token.pickle")

        self.service = build('drive', 'v3', credentials=self.creds)

    def list_audio_files(self) -> list:
        self.logger.debug("Listing audio files in folder %s", Config.DRIVE_FOLDER_ID)
        results = self.service.files().list(
            q=f"'{Config.DRIVE_FOLDER_ID}' in parents and mimeType contains 'audio/'",
            pageSize=100,
            fields="files(id, name)"
        ).execute()
        files = results.get('files', [])
        self.logger.info("Found %d audio files", len(files))
        return files

    def copy_to_workspace_folder(self) -> list:
        self.logger.debug("Copying files to Workspace folder...")
        files = self.list_audio_files()
        if not files:
            self.logger.info("No audio files to copy.")
            return []

        copied_files = []
        for file in files:
            existing = self.find_file_by_name(file['name'], Config.WORKSPACE_FOLDER_ID)
            if existing:
                self.logger.info("File '%s' already in Workspace, skipping copy.", file['name'])
                copied_files.append({'id': existing['id'], 'name': existing['name']})
                continue

            copied = self.service.files().copy(
                fileId=file['id'],
                body={'name': file['name'], 'parents': [Config.WORKSPACE_FOLDER_ID]}
            ).execute()

            self.logger.info("Copied file: %s", file['name'])
            copied_files.append({'id': copied['id'], 'name': copied['name']})
        return copied_files

    def download_file(self, file_id: str, destination_path: str):
        if os.path.exists(destination_path):
            self.logger.debug("File %s already exists locally, skipping download.", destination_path)
            return
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        self.logger.debug("Downloading file ID %s to %s", file_id, destination_path)
        request = self.service.files().get_media(fileId=file_id)
        with open(destination_path, "wb") as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
        self.logger.info("Downloaded file to %s", destination_path)

    def upload_file(self, local_path: str) -> str:
        folder_id = Config.WORKSPACE_FOLDER_ID
        file_name = os.path.basename(local_path)
        self.logger.debug("Uploading file %s to Workspace folder", file_name)
        media = MediaFileUpload(local_path, mimetype='text/plain')
        uploaded_file = self.service.files().create(
            body={'name': file_name, 'parents': [folder_id]},
            media_body=media,
            fields='id'
        ).execute()
        self.logger.info("Uploaded file %s with ID %s", file_name, uploaded_file['id'])
        return uploaded_file['id']

    def find_file_by_name(self, file_name, folder_id):
        self.logger.debug("Searching for file '%s' in folder %s", file_name, folder_id)
        query = f"'{folder_id}' in parents and name='{file_name}' and trashed=false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])
        if files:
            self.logger.debug("File found: %s", files[0]['name'])
            return files[0]
        self.logger.debug("File '%s' not found", file_name)
        return None

    def copy_sheet_template_to_workspace(self) -> dict:
        self.logger.debug("Copying sheet template to Workspace folder...")
        copied_file = self.service.files().copy(
            fileId=Config.SHEET_TEMPLATE_ID,
            body={'name': 'Workspace Sheet Copy', 'parents': [Config.WORKSPACE_FOLDER_ID]}
        ).execute()
        self.logger.info("Sheet template copied: %s", copied_file['name'])
        return {'id': copied_file['id'], 'name': copied_file['name']}
