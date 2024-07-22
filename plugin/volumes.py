import pathlib
import os
import shutil
import typing
from plugin._log import logging
import plugin.nfs as nfs
import uuid
import re
from plugin.nfs import NFSFilesystem


_REGEX_UUID = r"[0-9a-fA-F]{8}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{4}\b-[0-9a-fA-F]{12}"
_PATTERN_UUID = re.compile(f"^{_REGEX_UUID}$")
_PATTERN_VOLUME_PATH = re.compile(f"^(.+?)-({_REGEX_UUID})$")


ROOT = nfs.ROOT
DRIVES = [mount.local_path for mount in nfs.NFS_MOUNTS]


if not DRIVES:
    DRIVES = [ROOT / "drive"]


logging.debug("Environment: {%s}", ", ".join([f"{k}={v}" for k, v in os.environ.items()]))
logging.info("ROOT='%s'", str(ROOT))
logging.debug("Content of ROOT: %s", [str(f) for f in ROOT.glob("*")])
logging.info("DRIVES=%s", [str(d) for d in DRIVES])


class VolumeDescriptor:
    def __init__(self, drive: pathlib.Path, name: str, id=None):
        self.drive = drive or ValueError("Missing drive for volume")
        self.name = name or ValueError("Missing volume name")
        self.id = id or str(uuid.uuid4())

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        if other is self:
            return True
        if not isinstance(other, VolumeDescriptor):
            return False
        return self.drive == other.drive and self.name == self.name and self.id == other.id

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return f"{VolumeDescriptor.__name__}(drive='{str(self.drive)}', name='{self.name}', id='{self.id}')"

    def __hash__(self) -> int:
        return hash((self.drive, self.name, self.id))

    @property
    def path(self) -> pathlib.Path:
        return self.drive / f"{self.name}-{self.id}"

    @property
    def data_dir(self) -> pathlib.Path:
        return self.path / "_data"

    def exists(self):
        return self.data_dir.exists()

    def create(self, mod: int = 0o744, data_mod: int = 0o777):
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.chmod(mode=data_mod)
        self.path.chmod(mode=mod)

    def lock_file(self, container_id: str) -> pathlib.Path:
        return self.path / f"mounted-by-{container_id}.lock"

    def _lock_file_glob(self) -> typing.Iterable[pathlib.Path]:
        return self.path.glob("mounted-by-*.lock")

    def _container_id(self, lock_file: pathlib.Path) -> str:
        name = lock_file.name.split("-by-")[1]
        name = name.replace(".lock", "")
        return name

    def mount(self, container_id: str) -> pathlib.Path:
        lock = self.lock_file(container_id)
        if lock.exists():
            return None
        lock.touch(exist_ok=False)
        return lock

    def unmount(self, container_id: str) -> pathlib.Path:
        lock = self.lock_file(container_id)
        if not lock.exists():
            return None
        lock.unlink(missing_ok=False)
        return lock

    @property
    def mounted_by(self):
        return [self._container_id(file) for file in self._lock_file_glob()]

    def remove(self):
        return shutil.rmtree(self.path)

    @classmethod
    def find_all_in_drive(cls, drive: pathlib.Path) -> typing.Iterable['VolumeDescriptor']:
        for file in drive.glob("*"):
            if file.is_dir():
                match = _PATTERN_VOLUME_PATH.fullmatch(file.name)
                if match:
                    yield VolumeDescriptor(drive, match.group(1), match.group(2))

    @classmethod
    def find_all_with_name(cls, drive: pathlib.Path, name: str) -> typing.Iterable['VolumeDescriptor']:
        for volume in cls.find_all_in_drive(drive):
            if volume.name == name:
                yield volume

    @classmethod
    def find_one_with_name(cls, drive: pathlib.Path, name: str) -> 'VolumeDescriptor':
        candidates = list(cls.find_all_with_name(drive, name))
        if candidates:
            if len(candidates) > 1:
                raise RuntimeError(f"Too many volumes with name {name} in {str(drive)}")
            return candidates[0]
        raise KeyError(f"No volume named {name} in {str(drive)}")


class DriveSelector:
    def __init__(self, drives: typing.Iterable[pathlib.Path | str] = DRIVES):
        self._drives = [pathlib.Path(path) for path in drives]
        assert self._drives, f"No drives provided"
        self._drives.sort()

    def select_drive_for_new_volume(self, name: str, **opts) -> pathlib.Path:
        ...

    def find_drive_of_volume(self, name: str) -> pathlib.Path | None:
        volumes = list(v for v in self.all_volumes() if v[1] == name)
        if len(volumes) > 1:
            raise RuntimeError(f"Too many volumes with name {name}")
        if len(volumes) == 0:
            return None
        return volumes[0][0]

    def all_volumes(self) -> typing.Iterable[tuple[pathlib.Path, str]]:
        for drive in self._drives:
            for volume in VolumeDescriptor.find_all_in_drive(drive):
                yield volume.drive, volume.name


class SelectedDriveSelector(DriveSelector):
    def select_drive_for_new_volume(self, name: str, drive: str = None, **opts) -> pathlib.Path:
        if drive is None:
            raise RuntimeError("No drive provided")

        drive_path = NFSFilesystem.sanitize_path(drive)
        for d in self._drives:
            if str(d).removeprefix(str(ROOT) + '/').startswith(drive_path):
                return d

        raise RuntimeError(f"Drive {drive} not found")


class SpaceDriveSelector(DriveSelector):
    def get_drive_data(self, drive: pathlib.Path):
        total, used, free = shutil.disk_usage(drive)
        return total, used, free


class LowestUsedSpaceDriveSelector(SpaceDriveSelector):
    def select_drive_for_new_volume(self, name: str, **opts) -> pathlib.Path:
        os.system(f"ls -R {ROOT}")
        for storage in self._drives:
            total, used, free = self.get_drive_data(storage)
            print(f"Drive {storage} has {free} bytes free, {used} bytes used, {total} bytes total")

        drive = min(self._drives, key=lambda d: self.get_drive_data(d)[1])
        return drive


class HighestAvailableSpaceDriveSelector(SpaceDriveSelector):
    def select_drive_for_new_volume(self, name: str, **opts) -> pathlib.Path:
        drive = max(self._drives, key=lambda d: self.get_drive_data(d)[2])
        return drive


class LowestPercentageAvailableDriveSelector(SpaceDriveSelector):
    def select_drive_for_new_volume(self, name: str, **opts) -> pathlib.Path:
        def drive_percentage(d: pathlib.Path):
            total, used, free = self.get_drive_data(d)
            return used / total

        return min(self._drives, key=drive_percentage)


def create_volume(drive: pathlib.Path, name: str, mod: int = 0o777) -> pathlib.Path | None:
    collisions = list(VolumeDescriptor.find_all_with_name(drive, name))
    if collisions:
        return None
    candidate = VolumeDescriptor(drive, name)
    candidate.create(data_mod=mod)
    return candidate.data_dir


def remove_volume(drive: pathlib.Path, name: str) -> bool:
    try:
        volume = VolumeDescriptor.find_one_with_name(drive, name)
        volume.remove()
        if volume.exists():
            raise RuntimeError(f"Failed to remove volume {name}")
        return True
    except KeyError:
        return False


def mount_volume(drive: pathlib.Path, name: str, id: str) -> bool:
    try:
        volume = VolumeDescriptor.find_one_with_name(drive, name)
        result = volume.mount(id)
        return result is not None and result.exists()
    except KeyError:
        return False


def unmount_volume(drive: pathlib.Path, name: str, id: str) -> bool:
    try:
        volume = VolumeDescriptor.find_one_with_name(drive, name)
        result = volume.unmount(id)
        return result is not None and not result.exists()
    except KeyError:
        return False


def get_data_dir_for_volume(drive: pathlib.Path, name: str) -> pathlib.Path | None:
    try:
        return VolumeDescriptor.find_one_with_name(drive, name).data_dir
    except KeyError:
        return None


def volume_mounts(drive: pathlib.Path, name: str) -> typing.Iterable[str]:
    try:
        volume = VolumeDescriptor.find_one_with_name(drive, name)
        return volume.mounted_by
    except KeyError:
        return []
