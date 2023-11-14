import json
from abc import ABC
from enum import Enum
from pathlib import Path


class paths(Enum):
    VOLUME_CREATE = "/VolumeDriver.Create"
    VOLUME_REMOVE = "/VolumeDriver.Remove"
    VOLUME_PATH = "/VolumeDriver.Path"
    VOLUME_MOUNT = "/VolumeDriver.Mount"
    VOLUME_UNMOUNT = "/VolumeDriver.Unmount"
    VOLUME_GET = "/VolumeDriver.Get"
    VOLUME_LIST = "/VolumeDriver.List"
    CAPABILITIES = "/VolumeDriver.Capabilities"


class scopes(Enum):
    GLOBAL = "global"
    LOCAL = "local"


class Message(ABC):
    def __init__(self, **args):
        self.__dict__.update(args)
    
    def to_json(self):
        tmp = dict(self.__dict__)
        tmp = self._alter_json(tmp)
        return json.dumps(self.__dict__)
    
    def _alter_json(self, json):
        return json
    
    def __str__(self):
        return json.dumps(self.__dict__)
    
    def __repr__(self) -> str:
        return str(self)

    def __hash__(self) -> int:
        return hash(self.__dict__)
    
    def __eq__(self, o: object) -> bool:
        return self.__dict__ == o.__dict__

    def _ensure_has_fields(self, *fields):
        for field in fields:
            assert hasattr(self, field), f"`{field}` field is missing"


class Request(Message):
    pass


class Response(Message):
    def __init__(self, **args):
        super().__init__(**args)
        if not hasattr(self, "err"):
            self.err = ""


class VolumeCreateRequest(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("name", "opts")


class VolumeCreateResponse(Response):
    pass


class VolumeRemoveRequest(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("name", "opts")


class VolumeRemoveResponse(Response):
    pass


class _NameIdRequest(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("name", "id")


class VolumeMountRequest(_NameIdRequest):
    pass


class _MountPointResponse(Response):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("mountpoint")
        if not isinstance(self.mountpoint, Path):
            self.mountpoint = Path(self.mountpoint)

    def _alter_json(self, json):
        json['mountpoint'] = str(self.mountpoint) 


class VolumeMountResponse(_MountPointResponse):
    pass


class VolumeUnmountRequest(_NameIdRequest):
    pass


class VolumeUnmountResponse(Response):
    pass


class DriverCapabilitiesRequest(Request):
    pass


class DriverCapabilitiesResponse(Response):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("scope")
        if not isinstance(self.scope, scopes):
            self.scope = scopes(self.scope)

    def _alter_json(self, json):
        json['scope'] = self.scope.value
