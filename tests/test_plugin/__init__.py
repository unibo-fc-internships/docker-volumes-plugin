# FIXME: this file name is not descriptive

import logging
import subprocess
import sys
import unittest
import yaml
import string
from pathlib import Path


from faker import Faker
PLUGIN = "gciatto/volumes-on-paths:latest"
NFS_MOUNTS = "storage1:/"


logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


PATH_DOCKER_COMPOSE = Path(__file__).parent / "docker-compose.yml"
SPEC_DOCKER_COMPOSE = yaml.safe_load(PATH_DOCKER_COMPOSE.read_text())


class DockerService:

    class Dind:
        def __init__(self, name: string, docker_service: 'DockerService'):
            self.name = name
            self._docker_service = docker_service

        def exec(self, command: string) -> int:
            return self._docker_service.exec(command, self.name)

    @property
    def dind_names(self):
        return [key for key in SPEC_DOCKER_COMPOSE["services"].keys() if key.startswith("docker")]
    
    @property
    def dinds(self):
        return [self.Dind(name, self) for name in self.dind_names]

    def call_docker_compose(self, sub_command: string) -> int:
        process = subprocess.run(
            ["docker", "compose"] + sub_command.split(), 
            capture_output=True, 
            cwd=PATH_DOCKER_COMPOSE.parent
        )
        return process

    def up(self):
        self.down()
        self.call_docker_compose("up --build -w -d").check_returncode()

    def down(self):
        self.call_docker_compose("down -v").check_returncode()

    def exec(self, command: string, container: string) -> int:
        logging.info(f"Run '{command}' in {container}")
        return self.call_docker_compose(f"exec {container} {command}")

    def exec_all(self, command: string):
        res = 0
        for container in self.dind_names:
            res = res | self.exec(command, container)
        return res

    def install_plugin(self, plugin=None):
        if plugin is None:
            plugin = PLUGIN

        return self.exec_all(f"docker plugin install {plugin} --disable --grant-all-permissions")

    def conf_plugin(self, mounts=NFS_MOUNTS, plugin=PLUGIN):
        return self.exec_all(f"docker plugin set {plugin} NFS_MOUNT={mounts}")

    def enable_plugin(self, plugin=PLUGIN):
        return self.exec_all(f"docker plugin enable {plugin}")
    

docker_service = DockerService()


class BasePluginTest(unittest.TestCase):
    def docker_exec(self, command: string, container: string) -> int:
        return docker_service.exec(command, container)
    
    def assert_docker_instance_has_volume(self, dind: DockerService.Dind, volume: string):
        ls = dind.exec("docker volume ls")
        self.assertEqual(0, ls.returncode, f"Failed to list volumes in {dind.name}")
        ls_text = ls.stdout.decode('UTF-8')
        self.assertGreaterEqual(len(ls_text), 2, f"Volume not found in {dind.name}")
        self.assertIn(volume, ls_text, f"Volume not found in {dind.name}")

    def assert_docker_instance_has_not_volume(self, dind: DockerService.Dind, volume: string):
        ls = dind.exec("docker volume ls")
        self.assertEqual(0, ls.returncode, f"Failed to list volumes in {dind.name}")
        ls_text = ls.stdout.decode('UTF-8')
        self.assertNotIn(volume, ls_text, f"Volume found in {dind.name}, while it should not be there")
    

class BasePluginTestWithSetup(BasePluginTest):
    def setUp(self):
        logging.info("Starting Docker service...")
        docker_service.up()

    def tearDown(self):
        logging.info("Stopping Docker service...")
        docker_service.down()


class BasePluginTestWithSetupClass(BasePluginTest):
    @classmethod
    def setUpClass(cls):
        logging.info("Starting Docker service...")
        docker_service.up()

    @classmethod
    def tearDownClass(cls):
        logging.info("Stopping Docker service...")
        docker_service.down()


class InstallTest(BasePluginTestWithSetup):
    def test_install_plugin(self):
        self.assertFalse(docker_service.install_plugin())
        self.assertFalse(docker_service.conf_plugin())
        self.assertFalse(docker_service.enable_plugin())


class VolumeTest(BasePluginTestWithSetupClass):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.info("Install Plugin...")
        docker_service.install_plugin()
        docker_service.conf_plugin()
        docker_service.enable_plugin()
        

    def setUp(self):
        self.volume_name = Faker().first_name()
        volume_creation = docker_service.dinds[0].exec(f"docker volume create -d {PLUGIN} {self.volume_name}")
        volume_creation.check_returncode()

    def tearDown(self):
        self.volume_name = Faker().first_name()
        docker_service.dinds[0].exec(f"docker volume rm {self.volume_name}")
        
    def test_creating_on_one_node_actually_creates_the_volume_on_all_nodes(self):
        for dind in docker_service.dinds:
            self.assert_docker_instance_has_volume(dind, self.volume_name)

    def test_delete_from_the_same_node_where_the_volume_has_been_created(self):
        volume_deletion = docker_service.dinds[0].exec(f"docker volume rm {self.volume_name}")
        self.assertEqual(0, volume_deletion.returncode)
        for dind in docker_service.dinds:
            self.assert_docker_instance_has_not_volume(dind, self.volume_name)

    def test_mount(self):
        volume_name = Faker().word()
        container_name = Faker().word()
        self.assertFalse(docker_service.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(docker_service.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[0]))
        self.assertFalse(docker_service.exec(f"docker container stop {container_name}", DINDS[0]))
        self.assertFalse(docker_service.exec(f"docker container rm {container_name}", DINDS[0]))

        self.assertFalse(docker_service.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_delete_mounted(self):
        volume_name = Faker().word()
        container_name = Faker().word()

        self.assertFalse(docker_service.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(docker_service.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[0]))

        self.assertTrue(docker_service.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_mount_external(self):
        volume_name = Faker().word()
        container_name = Faker().word()
        self.assertFalse(docker_service.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(docker_service.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[1]))

        self.assertFalse(docker_service.exec(f"docker container stop {container_name}", DINDS[1]))
        self.assertFalse(docker_service.exec(f"docker container rm {container_name}", DINDS[1]))

        self.assertFalse(docker_service.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_delete_mounted_externally(self):
        volume_name = Faker().word()
        container_name = Faker().word()

        self.assertFalse(docker_service.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(docker_service.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[1]))

        self.assertTrue(docker_service.exec(f"docker volume rm {volume_name}", DINDS[0]))


class DataSyncTest(unittest.TestCase):
    volume_name = Faker().word()

    @classmethod
    def setUpClass(cls):
        logging.info("Start NFS servers and docker instances...")
        docker_service.up()
        logging.info("Install Plugin...")
        docker_service.install_plugin()
        docker_service.conf_plugin()
        docker_service.enable_plugin()
        assert docker_service.exec(f"docker volume create -d {PLUGIN} {cls.volume_name}", DINDS[0]) == 0, "Could not create volume for test"

    @classmethod
    def tearDownClass(cls):
        logging.info("Stop NFS server...")
        assert docker_service.exec(f"docker volume rm {cls.volume_name}", DINDS[0]) == 0, f"Could not remove volume after test"
        docker_service.down()

    def test_createfile(self):
        filename = Faker().word()

        self.assertFalse(docker_service.exec(f"docker run -v {self.volume_name}:/data alpine touch /data/{filename}", DINDS[0]))

        ls = docker_service.exec_output(f"docker run -v {self.volume_name}:/data alpine ls /data", DINDS[1])
        self.assertFalse(ls.returncode)
        self.assertTrue(filename in ls.stdout.decode('UTF-8'))

    def test_writefile(self):
        filename = Faker().word()
        content = Faker().sentence()

        self.assertFalse(docker_service.exec(f"docker run -v {self.volume_name}:/data alpine echo \"{content}\" > /data/{filename}", DINDS[0]))

        cat = docker_service.exec_output(f"docker run -v {self.volume_name}:/data alpine cat /data/{filename}", DINDS[1])
        self.assertFalse(cat.returncode)
        self.assertEqual(cat.stdout.decode('UTF-8'), content)

    def test_deletefile(self):
        filename = Faker().word()

        self.assertFalse(docker_service.exec(f"docker run -v {self.volume_name}:/data alpine touch /data/{filename}", DINDS[0]))

        self.assertFalse(docker_service.exec(f"docker run -v {self.volume_name}:/data alpine rm /data/{filename}", DINDS[1]))

        ls = docker_service.exec_output(f"docker run -v {self.volume_name}:/data alpine ls /data", DINDS[0])
        self.assertFalse(ls.returncode)
        self.assertFalse(filename in ls.stdout.decode('UTF-8'))


if __name__ == '__main__':
    unittest.main()

# TODO: