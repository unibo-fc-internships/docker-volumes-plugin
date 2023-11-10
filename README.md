# Docker volume plugin to manage ai4health NFS Servers
## Installation

### Installation from repository
```bash
git clone git@github.com:almaai-unibo/ascend-npu-image.git
cd ascend-npu-image/
make all
```

You should see the newly installed docker plugin with
```bash
docker plugin ls
```

In order to enable the plugin you can run
```bash
make enable
```

### Installation from Dockerhub
TODO

## Usage
TODO

## Debug
After plugin's installation, you can debug its APIs using the following command
```bash
curl -H "Content-Type: application/json" -XPOST -d '{}' --unix-socket /var/run/docker/plugins/90b599f9f62e16da031ebd37f7d0b0c19cc655886a65b97cbb27d34d3044fe84/plugin.sock http://localhost/<route>
```
Where route is one of the rest API configured on the plugin.

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
