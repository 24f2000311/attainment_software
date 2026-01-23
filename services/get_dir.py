import os,sys

def get_runtime_dir():
    if getattr(sys, 'frozen', False):
        # Running as .exe
        return os.path.dirname(sys.executable)
    else:
        # Running normally
        return os.path.dirname(os.path.abspath(__file__))