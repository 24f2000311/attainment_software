import os
import sys
from pathlib import Path

#this function is used to get the correct path for resources whether the app is run as a script or as a frozen executable when using as exe it will get the path from the temp folder created by pyinstaller
def resource_path(relative_path: str) -> str:
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


#used for getting the user data directory
def get_user_data_dir() -> Path:
    base = Path.home() 
    base.mkdir(parents=True, exist_ok=True)
    return base



USER_DATA_DIR = get_user_data_dir()

UPLOAD_FOLDER = USER_DATA_DIR / "uploads"
REPORTS_FOLDER = USER_DATA_DIR / "reports"

UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORTS_FOLDER.mkdir(exist_ok=True)

#global state management 
class AppState:
    cleaned_normalized_data = None
    config_sheets = None
    cqi_actions = []


state = AppState()
