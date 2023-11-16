import json
from abc import ABC
from enum import Enum
from pathlib import Path
from dataclasses import dataclass


class paths(Enum):
    VOLUME_CREATE = "/VolumeDriver.Create"
    VOLUME_REMOVE = "/VolumeDriver.Remove"
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
        return json.dumps(tmp)
    
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

    @classmethod
    def parse_json(cls, input):
        dict = json.loads(input)
        return cls(**dict)


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
        self._ensure_has_fields("name")


class VolumeRemoveResponse(Response):
    pass


class _NameIdRequest(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("name", "id")


class VolumeMountRequest(_NameIdRequest):
    pass


class _MountPointMessage(Message):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("mountpoint")
        if not isinstance(self.mountpoint, Path):
            self.mountpoint = Path(self.mountpoint)

    def _alter_json(self, json):
        json = super()._alter_json(json)
        json['mountpoint'] = str(self.mountpoint) 
        return json


class Volume(_MountPointMessage):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("name")
        if hasattr(self, "status"):
            assert isinstance(self.status, dict), "`status` must be a dict"
    
    def _to_dict(self):
        return self._alter_json(self.__dict__)


class VolumeMountResponse(_MountPointMessage):
    pass


class VolumeUnmountRequest(_NameIdRequest):
    pass


class VolumeUnmountResponse(Response):
    pass


class DriverCapabilitiesRequest(Request):
    pass


@dataclass
class Capabilities:
    scope: scopes

    def to_dict(self):
        return {"scope": self.scope.value}


class DriverCapabilitiesResponse(Message):
    def __init__(self, **args):
        if "capabilities" in args:
            if not isinstance(args["capabilities"], Capabilities):
                args["capabilities"] = Capabilities(scopes(args["capabilities"]["scope"]))
        if "scope" in args and not "capabilities" in args:
            args["capabilities"] = Capabilities(scope=scopes(args["scope"]))
            del args["scope"]
        super().__init__(**args)
        self._ensure_has_fields("capabilities")
        assert isinstance(self.capabilities, Capabilities), "`capabilities` must be a dict or Capabilities object"

    def _alter_json(self, json):
        super()._alter_json(json)
        json['capabilities'] = self.capabilities.to_dict()
        return json


class VolumeGetRequest(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("name")


class VolumeGetResponse(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("volume")
        if not isinstance(self.volume, Volume):
            self.volume = Volume(**self.volume)

    def _alter_json(self, json):
        super()._alter_json(json)
        json['volume'] = self.volume._to_dict()
        return json


class VolumeListRequest(Request):
    pass



class VolumeListResponse(Request):
    def __init__(self, **args):
        super().__init__(**args)
        self._ensure_has_fields("volumes")
        assert isinstance(self.volumes, list), "`volumes` must be a list"
        for i in range(len(self.volumes)):
            if not isinstance(self.volumes[i], Volume):
                self.volumes[i] = Volume(**self.volumes[i])

    def _alter_json(self, json):
        super()._alter_json(json)
        json['volumes'] = [volume._to_dict() for volume in self.volumes]
        return json


__all__ = [
    "paths",
    "scopes",
    "Message",
    "Request",
    "Response",
    "VolumeCreateRequest",
    "VolumeCreateResponse",
    "VolumeRemoveRequest",
    "VolumeRemoveResponse",
    "VolumeMountRequest",
    "VolumeMountResponse",
    "VolumeUnmountRequest",
    "VolumeUnmountResponse",
    "DriverCapabilitiesRequest",
    "Capabilities",
    "DriverCapabilitiesResponse",
    "VolumeGetRequest",
    "VolumeGetResponse",
    "VolumeListRequest",
    "VolumeListResponse",
    "Volume",
]
