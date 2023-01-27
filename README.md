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
