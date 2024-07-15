import logging
import os
from pathlib import Path


__all__ = ['file_logs_handler']


DEFAULT_LOG_DIR = Path("/var/log")
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / os.getenv("PLUGIN_NAME")


logging.root.addHandler(logging.StreamHandler())


try:
    if DEFAULT_LOG_DIR.exists() and DEFAULT_LOG_DIR.is_dir():
        if not DEFAULT_LOG_FILE.exists():
            DEFAULT_LOG_FILE.touch()
        file_logs_handler = logging.FileHandler(str(DEFAULT_LOG_FILE))
        logging.root.addHandler(file_logs_handler)
    else:
        file_logs_handler = None
except PermissionError:
    file_logs_handler = None


logging.root.setLevel(logging.DEBUG)
