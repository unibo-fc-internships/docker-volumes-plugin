PLUGIN_NAME = francoisjn/nfs-volumes
PLUGIN_NAME_SHORT = nfs-volumes
PLUGIN_TAG ?= latest
OUTPUT_DIR ?= ./.plugin
CONTAINER_NAME = container-francoisjn-nfs-volumes
# https://linux.die.net/man/5/nfs
NFS_MOUNT ?= localhost:/

build: clean config rootfs create
all: build enable
publish: build push

clean:
	@echo "### rm ${OUTPUT_DIR}"
	@rm -rf ${OUTPUT_DIR}

config:
	@echo "### copy config.json to ${OUTPUT_DIR}/"
	@mkdir -p ${OUTPUT_DIR}
	@cp config.json ${OUTPUT_DIR}/

generate_dotenv:
	@echo "### Configure .env file"
	@echo "PLUGIN_NAME=${PLUGIN_NAME}" > .env
	@echo "PLUGIN_NAME_SHORT=${PLUGIN_NAME_SHORT}" >> .env
	@echo "PLUGIN_TAG=${PLUGIN_TAG}" >> .env

rootfs: generate_dotenv
	@echo "### docker build: rootfs image with"
	@docker build --build-arg PLUGIN_NAME=${PLUGIN_NAME} --build-arg PLUGIN_NAME_SHORT=${PLUGIN_NAME_SHORT} -t ${PLUGIN_NAME}:rootfs .
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
	@cat /var/log/${PLUGIN_NAME_SHORT}.log

log_dockerd:
	@echo "### cat logs of docker daemon"
	@journalctl -xeu docker.service | cat

disable:
	@echo "### disable plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin disable ${PLUGIN_NAME}:${PLUGIN_TAG}

push:
	@echo "### push plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin push ${PLUGIN_NAME}:${PLUGIN_TAG}

delete_test:
	@curl -H "Authorization: JWT ${API_TOKEN}" -X DELETE https://hub.docker.com/v2/repositories/${PLUGIN_NAME}/tags/test/

test:
	@echo "### test plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@python -m unittest discover -s tests -p "*.py"