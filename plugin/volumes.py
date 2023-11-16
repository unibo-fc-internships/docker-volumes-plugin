import pathlib
import os


ROOT = pathlib.Path("/mnt")
USABLE_PATHS = os.getenv("USABLE_PATHS", "/mnt").split(os.pathsep)
DRIVES = [p for path in USABLE_PATHS for p in (ROOT / path).glob()]

assert DRIVES, f"No drives found in ${ROOT}"
