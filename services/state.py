import os
import sys

def get_runtime_dir():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        return os.path.dirname(sys.executable)
    else:
        # Running normally
        return os.path.dirname(os.path.abspath(__file__))
    
BASE_DIR = get_runtime_dir()

# Go up one level from services/state.py if we want BASE_DIR to be the root,
# but the original code had BASE_DIR as the directory of app.py.
# If state.py is in 'services', os.path.dirname(__file__) is '.../services'.
# app.py was in root.
# So if we want to maintain the same BASE_DIR relative to the script entry point (app.py),
# we should actually rely on the main entry point to set this or calculate it carefully.
# However, `get_runtime_dir` in app.py used `__file__`.
# If I move get_runtime_dir to services/state.py, `__file__` is `.../services/state.py`.
# So I need to go up one level.
if not getattr(sys, 'frozen', False):
     BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
REPORTS_FOLDER = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

class AppState:
    cleaned_normalized_data = None
    config_sheets = None
    cqi_actions = []

state = AppState()
