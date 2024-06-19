FROM python:latest
ENV PLUGIN_NAME volumes-on-paths
COPY ./requirements.txt /$PLUGIN_NAME/
WORKDIR /$PLUGIN_NAME
RUN pip install -r requirements.txt
COPY . /$PLUGIN_NAME/
RUN mkdir -p /run/docker/plugins
RUN apt-get update && apt-get install -y nfs-common
ENTRYPOINT /usr/bin/bash /$PLUGIN_NAME/entrypoint.sh
CMD /usr/local/bin/python -m flask --app plugin.service run --host=unix:///run/docker/plugins/$PLUGIN_NAME.sock
