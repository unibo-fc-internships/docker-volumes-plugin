PLUGIN_NAME = gciatto/volumes-on-paths
PLUGIN_TAG ?= latest
OUTPUT_DIR ?= ./.plugin
CONTAINER_NAME = container-gciatto-volumes-on-paths-latest

all: clean rootfs create

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

create:
	@echo "### remove existing plugin ${PLUGIN_NAME}:${PLUGIN_TAG} if exists"
	@docker plugin rm -f ${PLUGIN_NAME}:${PLUGIN_TAG} || true
	@echo "### create new plugin ${PLUGIN_NAME}:${PLUGIN_TAG} from ${OUTPUT_DIR}"
	@docker plugin create ${PLUGIN_NAME}:${PLUGIN_TAG} ${OUTPUT_DIR}

enable:
	@echo "### enable plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin enable ${PLUGIN_NAME}:${PLUGIN_TAG}

disable:
	@echo "### disable plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin disable ${PLUGIN_NAME}:${PLUGIN_TAG}

push:  clean rootfs create enable
	@echo "### push plugin ${PLUGIN_NAME}:${PLUGIN_TAG}"
	@docker plugin push ${PLUGIN_NAME}:${PLUGIN_TAG}
