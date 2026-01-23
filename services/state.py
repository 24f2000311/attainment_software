import os
import sys
from pathlib import Path

# ----------------------------
# READ-ONLY RESOURCE PATH
# (templates, static, fonts)
# ----------------------------
def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource.
    Works for normal run and PyInstaller EXE.
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ----------------------------
# WRITEABLE USER DATA PATH
# (uploads, reports)
# ----------------------------
def get_user_data_dir() -> Path:
    """
    Safe writable directory for EXE and web.
    """
    base = Path.home() / "Documents" / "AttainmentSoftware"
    base.mkdir(parents=True, exist_ok=True)
    return base


# ----------------------------
# DIRECTORIES
# ----------------------------
USER_DATA_DIR = get_user_data_dir()

UPLOAD_FOLDER = USER_DATA_DIR / "uploads"
REPORTS_FOLDER = USER_DATA_DIR / "reports"

UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORTS_FOLDER.mkdir(exist_ok=True)


# ----------------------------
# APPLICATION STATE
# ----------------------------
class AppState:
    cleaned_normalized_data = None
    config_sheets = None
    cqi_actions = []


state = AppState()
