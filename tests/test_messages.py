import unittest
import plugin.protocol as protocol
import pathlib


class TestVolumeCreateMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertIsInstance(request.opts, dict)
        self.assertEqual(request.opts["custom-option"], "value")
        self.assertEqual(request.to_json(), """{"name": "test", "opts": {"custom-option": "value"}}""")

    def test_request_creation(self):
        request = protocol.VolumeCreateRequest(name="test", opts={"custom-option": "value"})
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "name": "test",
                "opts": {
                    "custom-option": "value"
                }
            }
            """
        request = protocol.VolumeCreateRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")

    def test_response_creation(self):
        response = protocol.VolumeCreateResponse(err="error")
        self._response_assertions(response)
        self.assertEqual(response.to_json(), """{"err": "error"}""")

    def test_response_parsing(self):
        input = """
            {
                "err": "error"
            }
            """
        response = protocol.VolumeCreateResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeRemoveMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.to_json(), """{"name": "test"}""")

    def test_request_creation(self):
        request = protocol.VolumeRemoveRequest(name="test")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "name": "test"
            }
            """
        request = protocol.VolumeRemoveRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertEqual(response.to_json(), """{"err": "error"}""")

    def test_response_creation(self):
        response = protocol.VolumeRemoveResponse(err="error")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "err": "error"
            }
            """
        response = protocol.VolumeRemoveResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeMountMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.id, "b87d7442095999a92b")
        self.assertEqual(request.to_json(), """{"name": "test", "id": "b87d7442095999a92b"}""")

    def test_request_creation(self):
        request = protocol.VolumeMountRequest(name="test", id="b87d7442095999a92b")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "name": "test",
                "id": "b87d7442095999a92b"
            }
            """
        request = protocol.VolumeMountRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.mountpoint, pathlib.Path("/path/to/mount"))
        self.assertEqual(response.err, "error")
        self.assertEqual(response.to_json(), """{"mountpoint": "/path/to/mount", "err": "error"}""")

    def test_response_creation_from_string(self):
        response = protocol.VolumeMountResponse(mountpoint="/path/to/mount", err="error")
        self._response_assertions(response)

    def test_response_creation_from_path(self):
        response = protocol.VolumeMountResponse(mountpoint=pathlib.Path("/path/to/mount"), err="error")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "mountpoint": "/path/to/mount",
                "err": "error"
            }
            """
        response = protocol.VolumeMountResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeUnmountMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.id, "b87d7442095999a92b")
        self.assertEqual(request.to_json(), """{"name": "test", "id": "b87d7442095999a92b"}""")

    def test_request_creation(self):
        request = protocol.VolumeUnmountRequest(name="test", id="b87d7442095999a92b")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "name": "test",
                "id": "b87d7442095999a92b"
            }
            """
        request = protocol.VolumeUnmountRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertEqual(response.to_json(), """{"err": "error"}""")

    def test_response_creation(self):
        response = protocol.VolumeUnmountResponse(err="error")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "err": "error"
            }
            """
        response = protocol.VolumeUnmountResponse.parse_json(input)
        self._response_assertions(response)


class TestDriverCapabilitiesMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.__dict__, {})
        self.assertEqual(request.to_json(), """{}""")

    def test_request_creation(self):
        request = protocol.DriverCapabilitiesRequest()
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = "{}"
        request = protocol.DriverCapabilitiesRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertIsInstance(response.capabilities, protocol.Capabilities)
        self.assertEqual(response.capabilities.scope, protocol.scopes.GLOBAL)
        self.assertEqual(response.to_json(), """{"capabilities": {"scope": "global"}}""")

    def test_response_creation_from_capabilities(self):
        response = protocol.DriverCapabilitiesResponse(
            capabilities=protocol.Capabilities(scope=protocol.scopes.GLOBAL)
        )
        self._response_assertions(response)

    def test_response_creation_from_dict(self):
        response = protocol.DriverCapabilitiesResponse(
            capabilities={"scope": "global"}
        )
        self._response_assertions(response)

    def test_response_creation_from_string(self):
        response = protocol.DriverCapabilitiesResponse(scope="global")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "capabilities": {
                    "scope": "global"
                }
            }
            """
        response = protocol.DriverCapabilitiesResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeGetMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.to_json(), """{"name": "test"}""")

    def test_request_creation(self):
        request = protocol.VolumeGetRequest(name="test")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "name": "test"
            }
            """
        request = protocol.VolumeGetRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertIsInstance(response.volume, protocol.Volume)
        self.assertEqual(response.volume.name, "test")
        self.assertEqual(response.volume.mountpoint, pathlib.Path("/path/to/mount"))
        self.assertEqual(response.volume.status, {"custom-option": "value"})
        self.assertEqual(response.to_json(), """{"volume": {"name": "test", "mountpoint": "/path/to/mount", "status": {"custom-option": "value"}}, "err": "error"}""")

    def test_response_creation_from_volume(self):
        response = protocol.VolumeGetResponse(
            volume=protocol.Volume(
                name="test",
                mountpoint=pathlib.Path("/path/to/mount"),
                status={"custom-option": "value"}
            ),
            err="error"
        )
        self._response_assertions(response)

    def test_response_creation_from_dict(self):
        response = protocol.VolumeGetResponse(
            volume={
                "name": "test",
                "mountpoint": "/path/to/mount",
                "status": {"custom-option": "value"}
            },
            err="error"
        )
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "volume": {
                    "name": "test",
                    "mountpoint": "/path/to/mount",
                    "status": {
                        "custom-option": "value"
                    }
                },
                "err": "error"
            }
            """
        response = protocol.VolumeGetResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeListMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.__dict__, {})
        self.assertEqual(request.to_json(), """{}""")

    def test_request_creation(self):
        request = protocol.VolumeListRequest()
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = "{}"
        request = protocol.VolumeListRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertIsInstance(response.volumes, list)
        i = 1
        for volume in response.volumes:
            self.assertIsInstance(volume, protocol.Volume)
            self.assertEqual(volume.name, f"test{i}")
            self.assertEqual(volume.mountpoint, pathlib.Path(f"/path/to/mount{i}"))
            i += 1
        self.assertEqual(response.to_json(), """{"volumes": [{"name": "test1", "mountpoint": "/path/to/mount1"}, """
                         """{"name": "test2", "mountpoint": "/path/to/mount2"}], "err": "error"}""")

    def test_response_creation_from_volume(self):
        response = protocol.VolumeListResponse(
            volumes=[
                protocol.Volume(
                    name="test1",
                    mountpoint=pathlib.Path("/path/to/mount1")
                ),
                protocol.Volume(
                    name="test2",
                    mountpoint=pathlib.Path("/path/to/mount2")
                ),
            ],
            err="error"
        )
        self._response_assertions(response)

    def test_response_creation_from_dict(self):
        response = protocol.VolumeListResponse(
            volumes=[
                {
                    "name": "test1",
                    "mountpoint": "/path/to/mount1"
                },
                {
                    "name": "test2",
                    "mountpoint": "/path/to/mount2"
                },
            ],
            err="error"
        )
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "volumes": [
                    {
                        "name": "test1",
                        "mountpoint": "/path/to/mount1"
                    },
                    {
                        "name": "test2",
                        "mountpoint": "/path/to/mount2"
                    }
                ],
                "err": "error"
            }
            """
        response = protocol.VolumeListResponse.parse_json(input)
        self._response_assertions(response)
