import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    WORKSPACE_FOLDER_ID = os.getenv('WORKSPACE_FOLDER_ID')
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')
    SHEET_TEMPLATE_ID=os.getenv('SHEET_TEMPLATE_ID')
    SCOPES = ['https://www.googleapis.com/auth/drive']