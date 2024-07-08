import pathlib
import os
from plugin._log import logging
from dataclasses import dataclass
import typing
import subprocess

ROOT = pathlib.Path("/var/lib/docker/x-drives")


@dataclass
class NFSFilesystem:
    server: str
    remote_path: pathlib.Path
    local_path: pathlib.Path
    options: typing.Set[str] = None

    def __post_init__(self):
        self.options = self.options or set()

    @classmethod
    def parse(cls, string: str) -> 'NFSFilesystem':
        """
        init an NFSFilesystem object from a string
        :param str string: '\<server>:\<remote_path> \<options>(option)' format
        """

        def sanitize_string(s: str):
            forbidden_chars = '/'
            return ''.join('_' if c in forbidden_chars else c for c in s)

        parts = string.split()
        assert len(parts) in {1, 2}, f"Invalid NFS mount point string: {string}"

        options = set() if len(parts) == 1 else {s.strip() for s in parts[2].split(",")}

        server, remote_path = parts[0].split(":")
        server = server.strip()
        remote_path = pathlib.Path(remote_path.strip())

        local_path = pathlib.Path(ROOT / str(sanitize_string(parts[0])))

        return cls(server, remote_path, local_path, options)

    def __str__(self):
        return f"mount -t nfs {','.join(self.options)} {self.server}:{self.remote_path} {self.local_path}"

    def mount(self):
        if not self.local_path.exists():
            self.local_path.mkdir(parents=True)

        # assert os.system(str(self)) == 0, f"Failed to mount {self.server}:{self.remote_path} to {self.local_path}"
        process = subprocess.run(str(self).split())
        process.check_returncode()


NFS_MOUNTS = [
    NFSFilesystem.parse(mount.strip())
    for k in os.environ.keys()
    if k.startswith("NFS_MOUNT")
    for mount in os.environ[k].split(';')
]

if __name__ == "__main__":
    logging.info(f"NFS directories to mount: {len(NFS_MOUNTS)}")
    for mount in NFS_MOUNTS:
        mount.mount()
        logging.info(f"Mounted {mount.server}:{mount.remote_path} to {mount.local_path} with options {mount.options}")
