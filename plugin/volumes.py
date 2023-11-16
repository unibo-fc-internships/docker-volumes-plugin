import pathlib
import os
import shutil
import typing


ROOT = pathlib.Path("/mnt")
USABLE_PATHS = os.getenv("USABLE_PATHS", "/mnt").split(os.pathsep)
DRIVES = [p for path in USABLE_PATHS for p in (ROOT / path).glob()]


class DriveSelector:
    def __init__(self, drives=DRIVES):
        assert drives, f"No drives provided"
        self._drives = list(drives)
        self._drives.sort()
    
    def select_drive_for_new_volume(self, name: str) -> pathlib.Path:
        ...

    def find_drive_of_volume(self, name: str) -> pathlib.Path:
        ...

    def all_volumes(self) -> typing.Iterable[(pathlib.Path, str)]:
        for drive in self._drives:
            for path in drive.glob("*"):
                if path.is_dir():
                    yield drive, path.name


class FirstDriveSelector(DriveSelector):
    @property
    def _first_drive(self):
        return self._drives[0]

    def select_drive_for_new_volume(self, name: str) -> pathlib.Path:
        return self._first_drive
    
    def find_drive_of_volume(self, name: str) -> pathlib.Path:
        candidate = self._first_drive / name
        if candidate.exists():
            return self._first_drive
        return None
    

def create_volume(drive: pathlib.Path, name: str, mod: int = 0o777) -> bool:
    candidate = drive / name
    if candidate.exists():
        return False
    candidate.mkdir()
    candidate.chmod(mod)
    return True


def remove_volume(drive: pathlib.Path, name: str) -> bool:
    candidate = drive / name
    if not candidate.exists():
        return False
    shutil.rmtree(candidate)
    if candidate.exists():
        raise RuntimeError(f"Failed to remove {candidate}")
    return True


def mount_volume(drive: pathlib.Path, name: str, id: str) -> bool:
    candidate = drive / f"${name}-used-by-${id}.lock"
    if candidate.exists():
        return False
    candidate.touch()
    return candidate.exists()


def unmount_volume(drive: pathlib.Path, name: str, id: str) -> bool:
    candidate = drive / f"${name}-used-by-${id}.lock"
    if not candidate.exists():
        return False
    candidate.unlink()
    return not candidate.exists()


def volume_mounts(drive: pathlib.Path, name: str) -> typing.Iterable[str]:
    for path in drive.glob(f"${name}-used-by-*.lock"):
        yield path.name.split("-used-by-")[1].split(".lock")[0]
