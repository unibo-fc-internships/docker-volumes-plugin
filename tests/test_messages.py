import unittest
import plugin.protocol as protocol
import pathlib


class TestVolumeCreateMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertIsInstance(request.opts, dict)
        self.assertEqual(request.opts["custom_option"], "value")
        self.assertEqual(request.to_json(), """{"Name": "test", "Opts": {"CustomOption": "value"}}""")

    def test_request_creation(self):
        request = protocol.VolumeCreateRequest(name="test", opts={"custom_option": "value"})
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "Name": "test",
                "Opts": {
                    "CustomOption": "value"
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
        self.assertEqual(response.to_json(), """{"Err": "error"}""")

    def test_response_parsing(self):
        input = """
            {
                "Err": "error"
            }
            """
        response = protocol.VolumeCreateResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeRemoveMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.to_json(), """{"Name": "test"}""")

    def test_request_creation(self):
        request = protocol.VolumeRemoveRequest(name="test")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "Name": "test"
            }
            """
        request = protocol.VolumeRemoveRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertEqual(response.to_json(), """{"Err": "error"}""")

    def test_response_creation(self):
        response = protocol.VolumeRemoveResponse(err="error")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "Err": "error"
            }
            """
        response = protocol.VolumeRemoveResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeMountMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.id, "b87d7442095999a92b")
        self.assertEqual(request.to_json(), """{"Name": "test", "ID": "b87d7442095999a92b"}""")

    def test_request_creation(self):
        request = protocol.VolumeMountRequest(name="test", id="b87d7442095999a92b")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "Name": "test",
                "ID": "b87d7442095999a92b"
            }
            """
        request = protocol.VolumeMountRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.mountpoint, pathlib.Path("/path/to/mount"))
        self.assertEqual(response.err, "error")
        self.assertEqual(response.to_json(), """{"Mountpoint": "/path/to/mount", "Err": "error"}""")

    def test_response_creation_from_string(self):
        response = protocol.VolumeMountResponse(mountpoint="/path/to/mount", err="error")
        self._response_assertions(response)

    def test_response_creation_from_path(self):
        response = protocol.VolumeMountResponse(mountpoint=pathlib.Path("/path/to/mount"), err="error")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "Mountpoint": "/path/to/mount",
                "Err": "error"
            }
            """
        response = protocol.VolumeMountResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeUnmountMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.id, "b87d7442095999a92b")
        self.assertEqual(request.to_json(), """{"Name": "test", "ID": "b87d7442095999a92b"}""")

    def test_request_creation(self):
        request = protocol.VolumeUnmountRequest(name="test", id="b87d7442095999a92b")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "Name": "test",
                "ID": "b87d7442095999a92b"
            }
            """
        request = protocol.VolumeUnmountRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertEqual(response.to_json(), """{"Err": "error"}""")

    def test_response_creation(self):
        response = protocol.VolumeUnmountResponse(err="error")
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "Err": "error"
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
        self.assertEqual(response.to_json(), """{"Capabilities": {"Scope": "global"}}""")

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
                "Capabilities": {
                    "Scope": "global"
                }
            }
            """
        response = protocol.DriverCapabilitiesResponse.parse_json(input)
        self._response_assertions(response)


class TestVolumeGetMessages(unittest.TestCase):
    def _request_assertions(self, request):
        self.assertEqual(request.name, "test")
        self.assertEqual(request.to_json(), """{"Name": "test"}""")

    def test_request_creation(self):
        request = protocol.VolumeGetRequest(name="test")
        self._request_assertions(request)
    
    def test_request_parsing(self):
        input = """
            {
                "Name": "test"
            }
            """
        request = protocol.VolumeGetRequest.parse_json(input)
        self._request_assertions(request)

    def _response_assertions(self, response):
        self.assertEqual(response.err, "error")
        self.assertIsInstance(response.volume, protocol.Volume)
        self.assertEqual(response.volume.name, "test")
        self.assertEqual(response.volume.mountpoint, pathlib.Path("/path/to/mount"))
        self.assertEqual(response.volume.status, {"custom_option": "value"})
        self.assertEqual(response.to_json(), """{"Volume": {"Name": "test", "Mountpoint": "/path/to/mount", "Status": {"CustomOption": "value"}}, "Err": "error"}""")

    def test_response_creation_from_volume(self):
        response = protocol.VolumeGetResponse(
            volume=protocol.Volume(
                name="test",
                mountpoint=pathlib.Path("/path/to/mount"),
                status={"custom_option": "value"}
            ),
            err="error"
        )
        self._response_assertions(response)

    def test_response_creation_from_dict(self):
        response = protocol.VolumeGetResponse(
            volume={
                "name": "test",
                "mountpoint": "/path/to/mount",
                "status": {"custom_option": "value"}
            },
            err="error"
        )
        self._response_assertions(response)

    def test_response_parsing(self):
        input = """
            {
                "Volume": {
                    "Name": "test",
                    "Mountpoint": "/path/to/mount",
                    "Status": {
                        "CustomOption": "value"
                    }
                },
                "Err": "error"
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
        self.assertEqual(response.to_json(), """{"Volumes": [{"Name": "test1", "Mountpoint": "/path/to/mount1"}, """
                         """{"Name": "test2", "Mountpoint": "/path/to/mount2"}], "Err": "error"}""")

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
                "Volumes": [
                    {
                        "Name": "test1",
                        "Mountpoint": "/path/to/mount1"
                    },
                    {
                        "Name": "test2",
                        "Mountpoint": "/path/to/mount2"
                    }
                ],
                "Err": "error"
            }
            """
        response = protocol.VolumeListResponse.parse_json(input)
        self._response_assertions(response)
