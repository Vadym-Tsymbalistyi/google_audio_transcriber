import os
from dotenv import load_dotenv

load_dotenv()
class Config:
    WORKSPACE_FOLDER_ID = os.getenv('WORKSPACE_FOLDER_ID')
    DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')
    SHEET_TEMPLATE_ID=os.getenv('SHEET_TEMPLATE_ID')
    SCOPES = os.getenv('SCOPES')
    CREDENTIALS_PATH=os.getenv('CREDENTIALS_PATH')
    CREDENTIALS=os.getenv('CREDENTIALS')
    GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')
    WORKSPACE = os.path.join(os.path.dirname(__file__), "workspace")
    os.makedirs(WORKSPACE, exist_ok=True)

    AZURE_OPENAI_ENDPOINT=os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_KEY=os.getenv('AZURE_OPENAI_KEY')
    CHAT_COMPLETION_NAME=os.getenv('CHAT_COMPLETION_NAME')