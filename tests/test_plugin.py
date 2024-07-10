import unittest
import plugin.service as service
import plugin.volumes as volumes
import pathlib
import tempfile
import shutil


ROOT = pathlib.Path(tempfile.mkdtemp(prefix="test-docker-volumes-root-"))
DRIVES = [ROOT / f"drive{i}" for i in range(3)]


def setUpModule():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir()
    for drive in DRIVES:
        drive.mkdir()
    service.override_drive_selector(volumes.FirstDriveSelector(DRIVES))


def tearDownModule():
    shutil.rmtree(ROOT)


class AbstractPluginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = service.app.app_context()
        cls.ctx.push()
        cls.client = service.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()

    def create_volume(self, name: str, opts: dict = None, variable: str = "volume"):
        resp = self.client.post("/VolumeDriver.Create", json={
            "Name": name,
            "Opts": opts or {}
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        self.assertIsInstance(resp.json["Name"], str)
        self.assertEqual(name, resp.json["Name"])
        resp = self.client.post("/VolumeDriver.Get", json={"Name": name})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        mountpoint = str(resp.json["Volume"]["Mountpoint"])
        self.assertTrue(mountpoint.startswith(str(DRIVES[0])))
        self.assertTrue(name in mountpoint)
        self.assertTrue(mountpoint.endswith("/_data"))
        volume = name, pathlib.Path(mountpoint)
        setattr(self, variable, volume)
        self.assertTrue(volume[1].exists())
        self.assertTrue(volume[1].is_dir())

    def delete_volume(self, variable: str = "volume"):
        volume = getattr(self, variable)
        resp = self.client.post("/VolumeDriver.Remove", json={
            "Name": volume[0],
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        self.assertFalse(volume[1].exists())

    def mount_volume(self, container_id: str, volume_variable: str = "volume", info_variable: str = "info"):
        volume = getattr(self, volume_variable)
        info_file = volumes.VolumeDescriptor.find_one_with_name(DRIVES[0], volume[0]).lock_file(container_id)
        setattr(self, info_variable, info_file)
        self.assertFalse(info_file.exists())
        resp = self.client.post("/VolumeDriver.Mount", json={
            "Name": volume[0],
            "ID": container_id
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        self.assertEqual(resp.json["Mountpoint"], str(volume[1]))
        self.assertTrue(info_file.exists())

    def unmount_volume(self, container_id: str, volume_variable: str = "volume", info_variable: str = "info", expected_status: int = 200):
        volume = getattr(self, volume_variable)
        info_file = getattr(self, info_variable, None)
        if expected_status == 200:
            self.assertTrue(info_file.exists())
        resp = self.client.post("/VolumeDriver.Unmount", json={
            "Name": volume[0],
            "ID": container_id
        })
        self.assertEqual(resp.status_code, expected_status)
        if expected_status == 200:
            self.assertEqual(resp.json["Err"], "")
            self.assertFalse(info_file.exists())
        else:
            self.assertTrue(volume[0] in resp.json["Err"])


class TestPluginSingleVolume(AbstractPluginTest):
    def setUp(self):
        self.create_volume("test-volume", {}, "volume")

    def tearDown(self):
        self.delete_volume()

    def test_driver_capabilities(self):
        resp = self.client.post("/VolumeDriver.Capabilities", json={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Capabilities"]["Scope"], "global")

    def test_volume_mount_unmount(self):
        self.mount_volume("test-container")
        self.unmount_volume("test-container")

    def test_volume_unmount(self):
        self.unmount_volume("test-container", expected_status=500)

    def test_volume_get(self):
        resp = self.client.post("/VolumeDriver.Get", json={
            "Name": self.volume[0]
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        self.assertEqual(resp.json["Volume"]["Name"], self.volume[0])
        self.assertEqual(resp.json["Volume"]["Mountpoint"], str(self.volume[1]))
        self.assertEqual(resp.json["Volume"]["Status"], {"MountedBy": []})

    def test_volume_list(self):
        resp = self.client.post("/VolumeDriver.List", json={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        self.assertEqual(len(resp.json["Volumes"]), 1)
        self.assertEqual(resp.json["Volumes"][0]["Name"], self.volume[0])
        self.assertEqual(resp.json["Volumes"][0]["Mountpoint"], str(self.volume[1]))


class TestPluginSingleVolumeMultipleMounts(AbstractPluginTest):
    def setUp(self):
        self.create_volume("test-volume", {}, "volume")
        self.mount_volume("test-container1", info_variable="info1")
        self.mount_volume("test-container2", info_variable="info2")

    def test_volume_get(self):
        resp = self.client.post("/VolumeDriver.Get", json={
            "Name": self.volume[0]
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["Err"], "")
        self.assertEqual(resp.json["Volume"]["Name"], self.volume[0])
        self.assertEqual(resp.json["Volume"]["Mountpoint"], str(self.volume[1]))
        self.assertEqual(resp.json["Volume"]["Status"], {"MountedBy": ["test-container1", "test-container2"]})

    def tearDown(self):
        self.unmount_volume("test-container1", info_variable="info1")
        self.unmount_volume("test-container2", info_variable="info2")
        self.delete_volume()


del AbstractPluginTest
