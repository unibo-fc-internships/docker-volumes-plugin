FROM python:3.13.7
ARG PLUGIN_NAME
ARG PLUGIN_NAME_SHORT
ENV PLUGIN_NAME=${PLUGIN_NAME}
ENV PLUGIN_NAME_SHORT=${PLUGIN_NAME_SHORT}
COPY ./requirements.txt /$PLUGIN_NAME_SHORT/
WORKDIR /$PLUGIN_NAME_SHORT
RUN pip install -r requirements.txt
COPY . /$PLUGIN_NAME_SHORT/
RUN mkdir -p /run/docker/plugins
RUN apt-get update && apt-get install -y nfs-common
ENTRYPOINT /usr/bin/bash /$PLUGIN_NAME_SHORT/entrypoint.sh
CMD /usr/local/bin/python -m flask --app plugin.service run --host=unix:///run/docker/plugins/$PLUGIN_NAME_SHORT.sock
