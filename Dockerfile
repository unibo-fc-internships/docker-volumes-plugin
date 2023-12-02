FROM python:latest
ENV PLUGIN_NAME volumes-on-paths
COPY . /$PLUGIN_NAME/
WORKDIR /$PLUGIN_NAME
RUN pip install -r requirements.txt
RUN mkdir -p /run/docker/plugins
ENTRYPOINT /usr/local/bin/python -m flask --app plugin run --host=unix:///run/docker/plugins/$PLUGIN_NAME.sock
