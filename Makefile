PLUGIN_NAME = gciatto/volumes-on-paths
PLUGIN_TAG ?= latest
OUTPUT_DIR ?= ./.plugin
CONTAINER_NAME = container-gciatto-volumes-on-paths-latest
# https://linux.die.net/man/5/nfs
NFS_MOUNT ?= my_server:/shared_folder /local_folder udp,hard,ac

all: clean rootfs create enable

clean:
	@echo "### rm ${OUTPUT_DIR}"
	@rm -rf ${OUTPUT_DIR}

config:
	@echo "### copy config.json to ${OUTPUT_DIR}/"
	@mkdir -p ${OUTPUT_DIR}
	@cp config.json ${OUTPUT_DIR}/

rootfs: config
	@echo "### docker build: rootfs image with"
	@docker build -t ${PLUGIN_NAME}:rootfs .
	@echo "### create rootfs directory in ${OUTPUT_DIR}/rootfs"
	@mkdir -p ${OUTPUT_DIR}/rootfs
	@docker create --name ${CONTAINER_NAME} ${PLUGIN_NAME}:rootfs
	@docker export ${CONTAINER_NAME} | tar -x -C ${OUTPUT_DIR}/rootfs
	@docker rm -vf ${CONTAINER_NAME}

create: rootfs
	@echo "### remove existing plugin ${PLUGIN_NAME}:${PLUGIN_TAG} if exists"
	@docker plugin rm -f ${PLUGIN_NAME}:${PLUGIN_TAG} || true
	@echo "### create new plugin ${PLUGIN_NAME}:${PLUGIN_TAG} from ${OUTPUT_DIR}"
	@docker plugin create ${PLUGIN_NAME}:${PLUGIN_TAG} ${OUTPUT_DIR}

set: 
	@echo "### set plugin ${PLUGIN_NAME}:${PLUGIN_TAG} NFS_MOUNT='${NFS_MOUNT}'"
	@docker plugin set ${PLUGIN_NAME}:${PLUGIN_TAG} NFS_MOUNT="${NFS_MOUNT}"

enable:
	@echo "### enable plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin enable ${PLUGIN_NAME}:${PLUGIN_TAG}

log_plugin:
	@echo "### cat logs of plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@cat /var/log/volumes-on-paths.log

log_dockerd:
	@echo "### cat logs of docker daemon"
	@journalctl -xeu docker.service | cat

disable:
	@echo "### disable plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin disable ${PLUGIN_NAME}:${PLUGIN_TAG}

push:
	@echo "### push plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin push ${PLUGIN_NAME}:${PLUGIN_TAG}

#set_usable_paths: create
#    @echo "### setting var USABLE_PATHS=$(path)"
#    @docker plugin set "${PLUGIN_NAME}:${PLUGIN_TAG}" USABLE_PATHS=$(path)
