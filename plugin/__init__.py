import flask
from .protocol import *
import typing


app = flask.Flask(__name__)


def volumes_protocol(input: type, output: type):
    def decorator(f: typing.Callable[[input], output]):
        def wrapper():
            req = input(**flask.request.get_json())
            res = f(req)
            assert isinstance(res, output), f"Expected {output}, got {type(res)}: {res}"
            response = flask.make_response(res._to_json())
            response.headers["Content-Type"] = "application/json"
            return response
        return wrapper
    return decorator


@app.post(paths.VOLUME_CREATE)
@volumes_protocol(VolumeCreateRequest, VolumeCreateResponse)
def on_volume_create(req):
    pass


@app.post(paths.VOLUME_REMOVE)
@volumes_protocol(VolumeRemoveRequest, VolumeRemoveResponse)
def on_volume_remove(req):
    pass


@app.post(paths.VOLUME_MOUNT)
@volumes_protocol(VolumeMountRequest, VolumeMountResponse)
def on_volume_mount(req):
    pass


@app.post(paths.VOLUME_UNMOUNT)
@volumes_protocol(VolumeUnmountRequest, VolumeUnmountResponse)
def on_volume_unmount(req):
    pass


@app.post(paths.VOLUME_GET)
@volumes_protocol(VolumeGetRequest, VolumeGetResponse)
def on_volume_get(req):
    pass


@app.post(paths.VOLUME_LIST)
@volumes_protocol(VolumeListRequest, VolumeListResponse)
def on_volume_list(req):
    pass


@app.post(paths.CAPABILITIES)
@volumes_protocol(DriverCapabilitiesRequest, DriverCapabilitiesResponse)
def on_capabilities(req):
    pass
