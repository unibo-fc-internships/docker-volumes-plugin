import logging
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


def _log_request(req: flask.Request):
    msg = f"Request: {req.method} {req.url}"
    for h, v in req.headers:
        msg += f"\n\t{h}: {v}"
    msg += f"\n\t{req.get_data(as_text=True)}"
    logging.debug(msg)


def _log_response(res: flask.Response):
    msg = f"Response: {res.status_code}"
    for h, v in res.headers:
        msg += f"\n\t{h}: {v}"
    msg += f"\n\t{res.get_data(as_text=True)}"
    logging.debug(msg)


def volumes_protocol(input: type, output: type):
    def decorator(f: typing.Callable[[input], output]):
        def wrapper():
            _log_request(flask.request)
            req = input.parse_json(flask.request.get_data(as_text=True))
            try:
                res = f(req)
                assert isinstance(res, output), f"Expected {output}, got {type(res)}: {res}"
                status = 200
            except Exception as e:
                res = Response(err=str(e.args[0]))
                status = 500
                logging.exception(str(e))
            response = flask.make_response(res.to_json())
            response.status_code = status
            response.headers["Content-Type"] = "application/json"
            _log_response(response)
            return response
        wrapper.__name__ = f.__name__ + "__wrapped"
        return wrapper
    return decorator


@app.post(paths.VOLUME_CREATE.value)
@volumes_protocol(VolumeCreateRequest, VolumeCreateResponse)
def on_volume_create(req):
    logging.info("Request to create volume %s", req.name)
    name = f"{req.name}-{str(uuid.uuid4())}"
    drive = drive_selector.select_drive_for_new_volume(name)
    if drive is None:
        raise RuntimeError("No drive available")
    path = create_volume(drive, name)
    if path is None:
        raise RuntimeError(f"Impossible to create volume {req.name}")
    logging.info("Created volume %s in %s", name, str(path))
    return VolumeCreateResponse(name=name)


@app.post(paths.VOLUME_REMOVE.value)
@volumes_protocol(VolumeRemoveRequest, VolumeRemoveResponse)
def on_volume_remove(req):
    logging.info("Request to remove volume %s", req.name)
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume {req.name} not found")
    if any(volume_mounts(drive, req.name)):
        raise RuntimeError(f"Volume {req.name} is mounted")
    if not remove_volume(drive, req.name):
        raise RuntimeError(f"Impossible to remove volume {req.name}")
    logging.info("Volume %s removed successfully from %s", req.name, str(drive))
    return VolumeRemoveResponse(name=req.name)


@app.post(paths.VOLUME_MOUNT.value)
@volumes_protocol(VolumeMountRequest, VolumeMountResponse)
def on_volume_mount(req):
    logging.info("Request to mount volume %s, form %s", req.name, req.id)
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume {req.name} not found")
    if not mount_volume(drive, req.name, req.id):
        raise RuntimeError(f"Impossible to mount volume {req.name}")
    logging.info("Volume %s mounted by %s", req.name, req.id)
    return VolumeMountResponse(mountpoint=drive / req.name)


@app.post(paths.VOLUME_UNMOUNT.value)
@volumes_protocol(VolumeUnmountRequest, VolumeUnmountResponse)
def on_volume_unmount(req):
    logging.info("Request to unmount volume %s, form %s", req.name, req.id)
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume {req.name} not found")
    if not unmount_volume(drive, req.name, req.id):
        raise RuntimeError(f"Impossible to unmount volume {req.name}")
    logging.info("Volume %s unmounted by %s", req.name, req.id)
    return VolumeUnmountResponse()


@app.post(paths.VOLUME_GET.value)
@volumes_protocol(VolumeGetRequest, VolumeGetResponse)
def on_volume_get(req):
    logging.info("Request to inspect volume %s", req.name)
    drive = drive_selector.find_drive_of_volume(req.name)
    if drive is None:
        raise RuntimeError(f"Volume {req.name} not found")
    mountpoint = str(drive / req.name)
    mounts = list(volume_mounts(drive, req.name))
    mounts.sort()
    logging.info("Volume %s is stored in %s mounted by %s", req.name, mountpoint, mounts)
    return VolumeGetResponse(
        volume=Volume(
            name=req.name, 
            mountpoint=mountpoint,
            status={
                "mounted_by": mounts
            }
        )
    )


@app.post(paths.VOLUME_LIST.value)
@volumes_protocol(VolumeListRequest, VolumeListResponse)
def on_volume_list(req):
    logging.info("Request to list volumes")
    volumes = [Volume(name=name, mountpoint=drive / name) for drive, name in drive_selector.all_volumes()]
    logging.info("Found %d volumes: %s", len(volumes), [v.name for v in volumes])
    return VolumeListResponse(volumes=volumes)


@app.post(paths.CAPABILITIES.value)
@volumes_protocol(DriverCapabilitiesRequest, DriverCapabilitiesResponse)
def on_capabilities(req):
    logging.info("Request for capabilities")
    capabilities = Capabilities(scope=scopes.GLOBAL)
    logging.info("Returning capabilities: %s", str(capabilities.to_dict()))
    return DriverCapabilitiesResponse(capabilities=capabilities)
