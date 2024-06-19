# Docker volume plugin to manage ai4health NFS Servers
## Installation

### Installation from repository
1. Clone this repo, jump into the cloned folder, then run:
    ```bash
    make create
    ```

2. You should see the newly installed docker plugin with:
    ```bash
    docker plugin ls
    ```

3. Set the remote NFS folder to be mounted:
    ```bash
    make set NFS_MOUNT='SERVER_IP_OR_NAME:REMOTE_PATH LOCAL_PATH NFS_OPTIONS'
    ```
    - NFS options here: <https://linux.die.net/man/5/nfs>

4. Ensure your Docker Daemon is running in Swarm mode, if not `docker swarm init`

5. Enable the plugin:
    ```bash
    make enable
    ```

6. To inspect the docker daemons logs
    ```bash
    make log_dockerd
    ```

7. To inspect the plugin's logs
    ```bash
    make log_plugin
    ```

### Installation from Dockerhub

TODO

## Usage

TODO

## Debug

TODO

## Useful links
- API to implement a Docker Volume Plugin: https://docs.docker.com/engine/extend/plugins_volume/
- Plugin creation documentation: https://docs.docker.com/engine/extend/plugin_api/
- Creation and installation of Docker plugin: https://docs.docker.com/engine/extend/plugins_services/
- Clear blog article about Docker Volume Plugin: https://www.inovex.de/de/blog/docker-plugins/

## Help for creating NFS and/or GlusterFS clients
- Gluster container: https://github.com/gluster/gluster-containers
- Debian image with systemd: https://github.com/alehaa/docker-debian-systemd

## Other Plugin implementations

- Similar work in Go: https://github.com/quobyte/docker-volume
- Similar work in Go: https://github.com/MatchbookLab/local-persist
- Similar work in JS for S3: https://github.com/chooban/s3-docker-volume-plugin
- Similar work in Go for sshFS: https://github.com/vieux/docker-volume-sshfs
- This project provides managed volume plugins for Docker to connect to CIFS, GlusterFS NFS: https://github.com/trajano/docker-volume-plugins
