import flask
from ._log import *
from .protocol import *
from .volumes import *
import typing
import uuid


app = flask.Flask(__name__)
drive_selector = FirstDriveSelector()


def _override_drive_selector(selector: DriveSelector):
    global drive_selector
    drive_selector = selector


def volumes_protocol(input: type, output: type):
    def decorator(f: typing.Callable[[input], output]):
        def wrapper():
            req = input(**flask.request.get_json())
            try:
                res = f(req)
                assert isinstance(res, output), f"Expected {output}, got {type(res)}: {res}"
                status = 200
            except Exception as e:
                res = Response(err=str(e))
                status = 500
            response = flask.make_response(res.to_json())
            response.status_code = status
            response.headers["Content-Type"] = "application/json"
            return response
        wrapper.__name__ = f.__name__ + "__wrapped"
        return wrapper
    return decorator


@app.post(paths.VOLUME_CREATE.value)
@volumes_protocol(VolumeCreateRequest, VolumeCreateResponse)
def on_volume_create(req):
    name = f"{req.name}-{str(uuid.uuid4())}"
    drive = drive_selector.select_drive_for_new_volume(name)
    if drive is None:
        raise RuntimeError("No drive available")
    if not create_volume(drive, name):
        raise RuntimeError(f"Impossible to create volume ${req.name}")
    return VolumeCreateResponse(name=name)


@app.post(paths.VOLUME_REMOVE.value)
@volumes_protocol(VolumeRemoveRequest, VolumeRemoveResponse)
def on_volume_remove(req):
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume ${req.name} not found")
    if any(volume_mounts(drive, req.name)):
        raise RuntimeError(f"Volume ${req.name} is mounted")
    if not remove_volume(drive, req.name):
        raise RuntimeError(f"Impossible to remove volume ${req.name}")
    return VolumeRemoveResponse(name=req.name)


@app.post(paths.VOLUME_MOUNT.value)
@volumes_protocol(VolumeMountRequest, VolumeMountResponse)
def on_volume_mount(req):
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume ${req.name} not found")
    if not mount_volume(drive, req.name, req.id):
        raise RuntimeError(f"Impossible to mount volume ${req.name}")
    return VolumeMountResponse(mountpoint=drive / req.name)


@app.post(paths.VOLUME_UNMOUNT.value)
@volumes_protocol(VolumeUnmountRequest, VolumeUnmountResponse)
def on_volume_unmount(req):
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume ${req.name} not found")
    if not unmount_volume(drive, req.name, req.id):
        raise RuntimeError(f"Impossible to unmount volume ${req.name}")
    return VolumeUnmountResponse()


@app.post(paths.VOLUME_GET.value)
@volumes_protocol(VolumeGetRequest, VolumeGetResponse)
def on_volume_get(req):
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume ${req.name} not found")
    mounts = list(volume_mounts(drive, req.name))
    mounts.sort()
    return VolumeGetResponse(
        volume=Volume(
            name=req.name, 
            mountpoint=drive / req.name,
            status={
                "mounted-by": mounts
            }
        )
    )


@app.post(paths.VOLUME_LIST.value)
@volumes_protocol(VolumeListRequest, VolumeListResponse)
def on_volume_list(req):
    volumes = [Volume(name=name, mountpoint=drive / name) for drive, name in drive_selector.all_volumes()]
    return VolumeListResponse(volumes=volumes)


@app.post(paths.CAPABILITIES.value)
@volumes_protocol(DriverCapabilitiesRequest, DriverCapabilitiesResponse)
def on_capabilities(req):
    return DriverCapabilitiesResponse(capabilities=Capabilities(scope=scopes.GLOBAL))
