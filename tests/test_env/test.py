# FIXME: this file name is not descriptive

import logging
import subprocess
import sys
import unittest
import os
import string

# FIXME: where is this dependency declared?
# FIXME: I later noticed that there is another requirements.txt file in this directory. This is bad practice.
# Requirements files should be at the root of the project.
# Yet, separating test dependencies from production dependencies is a good practice.
# I'll teach you how to handle these situations.
from faker import Faker
PLUGIN = "gciatto/volumes-on-paths:latest"
NFS_MOUNTS = "storage1:/"

DINDS = [
    'docker1',
    'docker2'
]

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# FIXME: a class only having classmethods is a code smell. This should be a module instead.
# if you need a singleton, use a module-level variable
class DockerService:

    # FIXME: the current design of this class is kinda fragile because it does not explicitly mentions the path to the docker-compose file.
    # I'll teach you how to handle this.

    @classmethod
    def up(cls):
        cls.down()
        assert (os.system("docker compose up --build -w -d") == 0)

    @classmethod
    def down(cls):
        assert (os.system("docker compose down -v") == 0)

    @classmethod
    def exec(cls, command: string, container: string) -> int:
        logging.info(f"Run '{command}' in {container}")
        return os.system(f"docker compose exec {container} {command}")

    @classmethod
    def exec_output(cls, command: string, container: string) -> subprocess.CompletedProcess:
        logging.info(f"Run {command} in {container}")
        return subprocess.run(["docker", "compose", "exec", container] + command.split(), capture_output=True)

    @classmethod
    def exec_all(cls, command: string):
        res = 0
        for container in DINDS:
            res = res | cls.exec(command, container)
        return res

    @classmethod
    def install_plugin(cls, plugin=None):
        if plugin is None:
            plugin = PLUGIN

        return cls.exec_all(f"docker plugin install {plugin} --disable --grant-all-permissions")

    @classmethod
    def conf_plugin(cls, mounts=NFS_MOUNTS, plugin=PLUGIN):
        return cls.exec_all(f"docker plugin set {plugin} NFS_MOUNT={mounts}")

    @classmethod
    def enable_plugin(cls, plugin=PLUGIN):
        return cls.exec_all(f"docker plugin enable {plugin}")


# FIXME: code duplication: all test classes share a portion of the setup and teardown code
# (namely, starting and stopping the DockerService servers). This should be refactored into an abstract base class.
class InstallTest(unittest.TestCase):
    def setUp(self):
        # FIXME: copy-pasted code, the service being started is DockerService, not NFS
        logging.info("Start NFS servers and docker instances...")
        DockerService.up()

    def tearDown(self):
        # FIXME: copy-pasted code, the service being stopped is DockerService, not NFS
        logging.info("Stop NFS server...")
        DockerService.down()

    def test_install_plugin(self):
        self.assertFalse(DockerService.install_plugin())
        self.assertFalse(DockerService.conf_plugin())
        self.assertFalse(DockerService.enable_plugin())


class VolumeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # FIXME: same error as above, due to copy-pasted code. DRY principle is violated.
        logging.info("Start NFS servers and docker instances...")
        DockerService.up()
        logging.info("Install Plugin...")
        DockerService.install_plugin()
        DockerService.conf_plugin()
        DockerService.enable_plugin()

    @classmethod
    def tearDownClass(cls):
        logging.info("Stop NFS server...")
        DockerService.down()

    # FIXME: each test case should tell a story. The story here is not clear due to verbosity.
    # Recall to discuss with me how to refactor this.
    def test_create(self):
        def test_docker_instance_has_volume(docker_instance: string, volume: string):
            ls = DockerService.exec_output("docker volume ls", docker_instance)
            self.assertFalse(ls.returncode, f"Failed to list volumes in {docker_instance}")
            ls_lines = ls.stdout.decode('UTF-8').splitlines()
            self.assertGreaterEqual(len(ls_lines), 2, f"Volume not found in {docker_instance}")
            self.assertEqual(ls_lines[1].split()[1], volume, f"Volume not found in {docker_instance}")

        volume_name = Faker().word()
        self.assertFalse(DockerService.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        for dind in DINDS:
            test_docker_instance_has_volume(dind, volume_name)

        self.assertFalse(DockerService.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_delete(self):
        volume_name = "my_volume"
        self.assertFalse(DockerService.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))
        self.assertFalse(DockerService.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_mount(self):
        volume_name = Faker().word()
        container_name = Faker().word()
        self.assertFalse(DockerService.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(DockerService.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[0]))
        self.assertFalse(DockerService.exec(f"docker container stop {container_name}", DINDS[0]))
        self.assertFalse(DockerService.exec(f"docker container rm {container_name}", DINDS[0]))

        self.assertFalse(DockerService.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_delete_mounted(self):
        volume_name = Faker().word()
        container_name = Faker().word()

        self.assertFalse(DockerService.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(DockerService.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[0]))

        self.assertTrue(DockerService.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_mount_external(self):
        volume_name = Faker().word()
        container_name = Faker().word()
        self.assertFalse(DockerService.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(DockerService.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[1]))

        self.assertFalse(DockerService.exec(f"docker container stop {container_name}", DINDS[1]))
        self.assertFalse(DockerService.exec(f"docker container rm {container_name}", DINDS[1]))

        self.assertFalse(DockerService.exec(f"docker volume rm {volume_name}", DINDS[0]))

    def test_delete_mounted_externally(self):
        volume_name = Faker().word()
        container_name = Faker().word()

        self.assertFalse(DockerService.exec(f"docker volume create -d {PLUGIN} {volume_name}", DINDS[0]))

        self.assertFalse(DockerService.exec(f"docker run -d --name {container_name} -v {volume_name}:/data alpine", DINDS[1]))

        self.assertTrue(DockerService.exec(f"docker volume rm {volume_name}", DINDS[0]))


class DataSyncTest(unittest.TestCase):
    volume_name = Faker().word()

    @classmethod
    def setUpClass(cls):
        logging.info("Start NFS servers and docker instances...")
        DockerService.up()
        logging.info("Install Plugin...")
        DockerService.install_plugin()
        DockerService.conf_plugin()
        DockerService.enable_plugin()
        assert DockerService.exec(f"docker volume create -d {PLUGIN} {cls.volume_name}", DINDS[0]) == 0, "Could not create volume for test"

    @classmethod
    def tearDownClass(cls):
        logging.info("Stop NFS server...")
        assert DockerService.exec(f"docker volume rm {cls.volume_name}", DINDS[0]) == 0, f"Could not remove volume after test"
        DockerService.down()

    def test_createfile(self):
        filename = Faker().word()

        self.assertFalse(DockerService.exec(f"docker run -v {self.volume_name}:/data alpine touch /data/{filename}", DINDS[0]))

        ls = DockerService.exec_output(f"docker run -v {self.volume_name}:/data alpine ls /data", DINDS[1])
        self.assertFalse(ls.returncode)
        self.assertTrue(filename in ls.stdout.decode('UTF-8'))

    def test_writefile(self):
        filename = Faker().word()
        content = Faker().sentence()

        self.assertFalse(DockerService.exec(f"docker run -v {self.volume_name}:/data alpine echo \"{content}\" > /data/{filename}", DINDS[0]))

        cat = DockerService.exec_output(f"docker run -v {self.volume_name}:/data alpine cat /data/{filename}", DINDS[1])
        self.assertFalse(cat.returncode)
        self.assertEqual(cat.stdout.decode('UTF-8'), content)

    def test_deletefile(self):
        filename = Faker().word()

        self.assertFalse(DockerService.exec(f"docker run -v {self.volume_name}:/data alpine touch /data/{filename}", DINDS[0]))

        self.assertFalse(DockerService.exec(f"docker run -v {self.volume_name}:/data alpine rm /data/{filename}", DINDS[1]))

        ls = DockerService.exec_output(f"docker run -v {self.volume_name}:/data alpine ls /data", DINDS[0])
        self.assertFalse(ls.returncode)
        self.assertFalse(filename in ls.stdout.decode('UTF-8'))


if __name__ == '__main__':
    unittest.main()

# TODO: