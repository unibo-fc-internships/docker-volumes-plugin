import unittest
import plugin
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
    plugin._override_drive_selector(volumes.FirstDriveSelector(DRIVES))


def tearDownModule():
    shutil.rmtree(ROOT)


class AbstractPluginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = plugin.app.app_context()
        cls.ctx.push()
        cls.client = plugin.app.test_client()

    @classmethod
    def tearDownClass(cls):
        cls.ctx.pop()

    def create_volume(self, name: str, opts: dict = None, variable: str = "volume"):
        resp = self.client.post("/VolumeDriver.Create", json={
            "name": name,
            "opts": opts or {}
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["err"], "")
        self.assertIsInstance(resp.json["name"], str)
        self.assertTrue(resp.json["name"].startswith(name))
        volume = DRIVES[0] / resp.json["name"]
        setattr(self, variable, volume)
        self.assertTrue(volume.exists())
        self.assertTrue(volume.is_dir())

    def delete_volume(self, variable: str = "volume"):
        volume = getattr(self, variable)
        resp = self.client.post("/VolumeDriver.Remove", json={
            "name": volume.name,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["err"], "")
        self.assertFalse(volume.exists())

    def mount_volume(self, container_id: str, volume_variable: str = "volume", info_variable: str = "info"):
        volume = getattr(self, volume_variable)
        info_file = volumes.mount_info_path(DRIVES[0], volume.name, container_id)
        setattr(self, info_variable, info_file)
        self.assertFalse(info_file.exists())
        resp = self.client.post("/VolumeDriver.Mount", json={
            "name": volume.name,
            "id": container_id
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["err"], "")
        self.assertEqual(resp.json["mountpoint"], str(volume))
        self.assertTrue(info_file.exists())

    def unmount_volume(self, container_id: str, volume_variable: str = "volume", info_variable: str = "info", expected_status: int = 200):
        volume = getattr(self, volume_variable)
        info_file = getattr(self, info_variable, None)
        if expected_status == 200:
            self.assertTrue(info_file.exists())
        resp = self.client.post("/VolumeDriver.Unmount", json={
            "name": volume.name,
            "id": container_id
        })
        self.assertEqual(resp.status_code, expected_status)
        if expected_status == 200:
            self.assertEqual(resp.json["err"], "")
            self.assertFalse(info_file.exists())
        else:
            self.assertTrue(volume.name in resp.json["err"])


class TestPluginSingleVolume(AbstractPluginTest):
    def setUp(self):
        self.create_volume("test-volume", {}, "volume")

    def tearDown(self):
        self.delete_volume()

    def test_driver_capabilities(self):
        resp = self.client.post("/VolumeDriver.Capabilities", json={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["capabilities"]["scope"], "global")

    def test_volume_mount_unmount(self):
        self.mount_volume("test-container")
        self.unmount_volume("test-container")

    def test_volume_unmount(self):
        self.unmount_volume("test-container", expected_status=500)

    def test_volume_get(self):
        resp = self.client.post("/VolumeDriver.Get", json={
            "name": self.volume.name
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["err"], "")
        self.assertEqual(resp.json["volume"]["name"], self.volume.name)
        self.assertEqual(resp.json["volume"]["mountpoint"], str(self.volume))
        self.assertEqual(resp.json["volume"]["status"], {"mounted-by": []})

    def test_volume_list(self):
        resp = self.client.post("/VolumeDriver.List", json={})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["err"], "")
        self.assertEqual(len(resp.json["volumes"]), 1)
        self.assertEqual(resp.json["volumes"][0]["name"], self.volume.name)
        self.assertEqual(resp.json["volumes"][0]["mountpoint"], str(self.volume))


class TestPluginSingleVolumeMultipleMounts(AbstractPluginTest):
    def setUp(self):
        self.create_volume("test-volume", {}, "volume")
        self.mount_volume("test-container1", info_variable="info1")
        self.mount_volume("test-container2", info_variable="info2")

    def test_volume_get(self):
        resp = self.client.post("/VolumeDriver.Get", json={
            "name": self.volume.name
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json["err"], "")
        self.assertEqual(resp.json["volume"]["name"], self.volume.name)
        self.assertEqual(resp.json["volume"]["mountpoint"], str(self.volume))
        self.assertEqual(resp.json["volume"]["status"], {"mounted-by": ["test-container1", "test-container2"]})

    def tearDown(self):
        self.unmount_volume("test-container1", info_variable="info1")
        self.unmount_volume("test-container2", info_variable="info2")
        self.delete_volume()


del AbstractPluginTest
