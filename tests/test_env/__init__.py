import logging
import os
import shlex
import subprocess
import sys
import unittest
import string
from pathlib import Path
from subprocess import CompletedProcess
import yaml
from faker import Faker
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / '.env')

RETRY_COUNT = 3

faker = Faker()

logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


if not os.environ.get('PLUGIN_NAME'):
    raise ValueError('PLUGIN_NAME is not set in .env file : ' + str(os.environ))
if not os.environ.get('PLUGIN_NAME_SHORT'):
    raise ValueError('PLUGIN_NAME_SHORT is not set in .env file : ' + str(os.environ))
if not os.environ.get('PLUGIN_TAG'):
    raise ValueError('PLUGIN_TAG is not set in .env file : ' + str(os.environ))

PLUGIN = os.getenv("PLUGIN_NAME") + ":" + os.getenv("PLUGIN_TAG")

PATH_DOCKER_COMPOSE = Path(__file__).parent / "docker-compose.yml"
SPEC_DOCKER_COMPOSE = yaml.safe_load(PATH_DOCKER_COMPOSE.read_text())


class DockerService:
    class Container:
        def __init__(self, name: string, docker_service: 'DockerService'):
            self.name = name
            self._docker_service = docker_service

        def exec(self, command: string) -> CompletedProcess[bytes]:
            return self._docker_service.exec(command, self.name)

    class Dind(Container):
        ...

    class Storage(Container):
        def __init__(self, name: string, docker_service: 'DockerService', path=Path("/")):
            super().__init__(name, docker_service)
            self.name = name
            self._docker_service = docker_service
            self.path = path

        def __str__(self):
            return self.name + ":" + str(self.path)

    @property
    def dind_names(self):
        return [key for key in SPEC_DOCKER_COMPOSE["services"].keys() if key.startswith("docker")]

    @property
    def dinds(self):
        return [self.Dind(name, self) for name in self.dind_names]

    @property
    def storage_names(self):
        return [key for key in SPEC_DOCKER_COMPOSE["services"].keys() if key.startswith("storage")]

    @property
    def storages(self):
        return [self.Storage(name, self) for name in self.storage_names]

    def call_docker_compose(self, sub_command: string) -> CompletedProcess[bytes]:
        process = subprocess.run(
            ["docker", "compose"] + shlex.split(sub_command),
            capture_output=True,
            cwd=PATH_DOCKER_COMPOSE.parent
        )
        if process.returncode != 0:
            logging.error(process.stderr.decode('UTF-8'))
        return process

    def up(self):
        self.down()
        self.call_docker_compose("up --build --wait -d").check_returncode()

    def down(self):
        self.call_docker_compose("down -v").check_returncode()

    def exec(self, command: string, container: string) -> CompletedProcess[bytes]:
        logging.info(f"Run '{command}' in {container}")

        count_tries = 0
        while count_tries < RETRY_COUNT:
            run = self.call_docker_compose(f"exec {container} {command}")
            count_tries += 1
            if run.returncode != 0 and "Client.Timeout" in str(run.stderr):
                logging.info("Command failed")
            else:
                break

        return run

    def exec_all(self, command: string):
        res = 0
        for docker in self.dinds:
            process = docker.exec(command)
            res = res | process.returncode
        return res

    def install_plugin(self, plugin=None):
        if plugin is None:
            plugin = PLUGIN

        return self.exec_all(f"docker plugin install {plugin} --disable --grant-all-permissions")

    def conf_plugin(self, mounts: string = None, plugin=PLUGIN):
        if mounts is None:
            mounts = "|".join([str(storage) for storage in self.storages])
        return self.exec_all(f"docker plugin set {plugin} NFS_MOUNT='{mounts}'")

    def enable_plugin(self, plugin=PLUGIN):
        return self.exec_all(f"docker plugin enable {plugin}")


docker_service = DockerService()


class BasePluginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logging.info("Start services...")
        docker_service.up()

    @classmethod
    def tearDownClass(cls):
        logging.info("Stop services...")
        docker_service.down()

    def docker_exec(self, command: string, container: string) -> CompletedProcess[bytes]:
        return docker_service.exec(command, container)

    def assert_docker_instance_has_volume(self, dind: DockerService.Dind, volume: string):
        ls = dind.exec("docker volume ls")
        self.assertEqual(0, ls.returncode, f"Failed to list volumes in {dind}")
        self.assertIn(volume, ls.stdout.decode('UTF-8'))

    def assert_docker_instance_has_not_volume(self, dind: DockerService.Dind, volume: string):
        ls = dind.exec("docker volume ls")
        self.assertEqual(0, ls.returncode, f"Failed to list volumes in {dind}")
        self.assertNotIn(volume, ls.stdout.decode('UTF-8'))


class BasePluginInstalledTest(BasePluginTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.info("Install Plugin...")
        assert docker_service.install_plugin() == 0
        assert docker_service.conf_plugin() == 0
        assert docker_service.enable_plugin() == 0


class BaseVolumeCreatedTest(BasePluginInstalledTest):
    def setUp(self):
        super().setUp()
        self.volume = faker.first_name()
        create = docker_service.dinds[0].exec(f"docker volume create -d {PLUGIN} {self.volume}")
        self.assertEqual(create.returncode, 0, f"Failed to create volume {self.volume} : {create.stderr.decode('UTF-8')}")

    def tearDown(self):
        super().tearDown()
        docker_service.dinds[0].exec(f"docker volume rm {self.volume}")


class BaseVolumeMountedTest(BaseVolumeCreatedTest):

    def setUp(self):
        super().setUp()
        self.container_name = faker.first_name()
        for dind in docker_service.dinds:
            dind.exec(f"docker run -d --rm --name {self.container_name} -v {self.volume}:/data alpine tail -f /dev/null").check_returncode()

    def tearDown(self):
        super().tearDown()
        for dind in docker_service.dinds:
            dind.exec(f"docker container stop {self.container_name}").check_returncode()


class InstallTest(BasePluginTest):
    def test_install_plugin(self):
        self.assertEqual(0, docker_service.install_plugin())
        self.assertEqual(0, docker_service.conf_plugin())
        self.assertEqual(0, docker_service.enable_plugin())


class VolumeTest(BaseVolumeCreatedTest):
    def test_all_docker_instances_has_volume(self):
        for dind in docker_service.dinds:
            self.assert_docker_instance_has_volume(dind, self.volume)

    def test_delete_from_creator_node(self):
        docker_service.dinds[0].exec(f"docker volume rm {self.volume}").check_returncode()
        for dind in docker_service.dinds:
            self.assert_docker_instance_has_not_volume(dind, self.volume)

    def test_delete_from_not_creator_node(self):
        docker_service.dinds[1].exec(f"docker volume rm {self.volume}").check_returncode()
        for dind in docker_service.dinds:
            self.assert_docker_instance_has_not_volume(dind, self.volume)

    def test_mount(self):
        container_name = faker.first_name()
        for dind in docker_service.dinds:
            mount = dind.exec(f"docker run -d --rm --name {container_name} -v {self.volume}:/data alpine")
            self.assertEqual(0, mount.returncode, f"Failed to mount volume {self.volume} in {dind}")

    def test_delete_mounted(self):
        container_name = faker.first_name()

        docker_service.dinds[0].exec(f"docker run --rm -d --name {container_name} -v {self.volume}:/data alpine tail -f /dev/null").check_returncode()

        for dind in docker_service.dinds:
            delete = dind.exec(f"docker volume rm {self.volume}")
            self.assertNotEqual(0, delete.returncode)

        docker_service.dinds[0].exec(f"docker container stop {container_name}").check_returncode()


class DataSyncTest(BaseVolumeMountedTest):

    def test_created_file_exists_on_all(self):
        filename = faker.first_name()

        docker_service.dinds[0].exec(f"docker run -v {self.volume}:/data alpine touch /data/{filename}").check_returncode()

        for dind in docker_service.dinds:
            ls = dind.exec(f"docker run -v {self.volume}:/data alpine ls /data")
            self.assertEqual(0, ls.returncode)
            self.assertIn(filename, ls.stdout.decode('UTF-8'))

    def test_write_in_file_and_read_content_everywhere(self):
        filename = faker.first_name()
        content = faker.sentence()

        docker_service.dinds[0].exec(f"docker run -v {self.volume}:/data alpine sh -c 'echo \"{content}\" > /data/{filename}'").check_returncode()

        for dind in docker_service.dinds:
            cat = dind.exec(f"docker run -v {self.volume}:/data alpine cat /data/{filename}")
            self.assertEqual(0, cat.returncode, f"Failed to read file {filename} in {dind}")
            self.assertEqual(cat.stdout.decode('UTF-8').strip(), content, f"Content mismatch in {dind}")

    def test_deletefile(self):
        filename = faker.first_name()

        docker_service.dinds[0].exec(f"docker run -v {self.volume}:/data alpine touch /data/{filename}").check_returncode()

        docker_service.dinds[1].exec(f"docker run -v {self.volume}:/data alpine rm /data/{filename}").check_returncode()

        for dind in docker_service.dinds:
            ls = dind.exec(f"docker run -v {self.volume}:/data alpine ls /data")
            self.assertEqual(0, ls.returncode)
            self.assertNotIn(filename, ls.stdout.decode('UTF-8'))


class DriveSelectorsTest(BasePluginInstalledTest):
    def setUp(self):
        super().setUp()
        logging.info("Clean storages...")
        for storage in docker_service.storages:
            storage.exec(f"rm -rf /data/*").check_returncode()

    def create_volume(self, volume: string, **opts):
        opts_string = " ".join([f"-o {k}={v}" for k, v in opts.items()])
        return docker_service.dinds[0].exec(f"docker volume create -d {PLUGIN} {opts_string} {volume}")

    def remove_volume(self, volume: string):
        return docker_service.dinds[0].exec(f"docker volume rm {volume}")

    def test_default_driver(self):
        self.volume = Faker().first_name()

        create = self.create_volume(self.volume)
        self.assertEqual(create.returncode, 0, f"Failed to create volume {self.volume} : {create.stderr.decode('UTF-8')}")

        self.remove_volume(self.volume).check_returncode()

    def test_selected_drive_missing_param_selector(self):
        self.volume = Faker().first_name()

        self.assertNotEqual(0, self.create_volume(self.volume, drive_selector="selected").returncode)

    def test_selected_drive_selector(self):
        for storage in docker_service.storages:
            self.volume = Faker().first_name()
            self.create_volume(self.volume, drive_selector="selected", drive=f"{storage.name}:{storage.path}").check_returncode()
            ls = docker_service.exec("ls /data", storage.name)
            self.assertIn(self.volume, ls.stdout.decode('UTF-8'))

            self.remove_volume(self.volume).check_returncode()

    def test_lowest_usage_drive_selector(self):
        # create a 5MB file in the first storage to simulate filling
        docker_service.storages[0].exec("dd if=/dev/zero of=/data/filler bs=1M count=5").check_returncode()

        self.volume = Faker().first_name()
        self.create_volume(self.volume, drive_selector="lowest_usage").check_returncode()

        check_storage2 = docker_service.storages[1].exec("ls /data")
        check_storage2.check_returncode()
        self.assertIn(self.volume, check_storage2.stdout.decode('UTF-8'))

        check_storage1 = docker_service.storages[0].exec("ls /data")
        check_storage1.check_returncode()
        self.assertNotIn(self.volume, check_storage1.stdout.decode('UTF-8'))

        docker_service.storages[0].exec("rm /data/filler").check_returncode()
        self.remove_volume(self.volume).check_returncode()

    def test_highest_space_drive_selector(self):
        # create a 5MB file in the first storage to simulate filling
        docker_service.storages[1].exec("dd if=/dev/zero of=/data/filler bs=1M count=5").check_returncode()

        self.volume = Faker().first_name()
        self.create_volume(self.volume, drive_selector="highest_space").check_returncode()

        check_storage2 = docker_service.storages[1].exec("ls /data")
        check_storage2.check_returncode()
        self.assertIn(self.volume, check_storage2.stdout.decode('UTF-8'))

        check_storage1 = docker_service.storages[0].exec("ls /data")
        check_storage1.check_returncode()
        self.assertNotIn(self.volume, check_storage1.stdout.decode('UTF-8'))

        docker_service.storages[1].exec("rm /data/filler").check_returncode()
        self.remove_volume(self.volume).check_returncode()

    def test_lowest_percentage_available_drive_selector(self):
        # create a 5MB file in the first storage to simulate filling
        docker_service.storages[1].exec("dd if=/dev/zero of=/data/filler bs=1M count=5").check_returncode()

        self.volume = Faker().first_name()
        self.create_volume(self.volume, drive_selector="lowest_percentage").check_returncode()

        check_storage1 = docker_service.storages[0].exec("ls /data")
        check_storage1.check_returncode()
        self.assertIn(self.volume, check_storage1.stdout.decode('UTF-8'))

        check_storage2 = docker_service.storages[1].exec("ls /data")
        check_storage2.check_returncode()
        self.assertNotIn(self.volume, check_storage2.stdout.decode('UTF-8'))

        docker_service.storages[1].exec("rm /data/filler").check_returncode()
        self.remove_volume(self.volume).check_returncode()

    def test_unexisting_drive_selector(self):
        self.volume = Faker().first_name()

        create = self.create_volume(self.volume, drive_selector=Faker().first_name())
        self.assertNotEqual(0, create.returncode)


if __name__ == '__main__':
    unittest.main()
