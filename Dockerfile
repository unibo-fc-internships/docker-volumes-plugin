FROM python:latest
ENV PLUGIN_NAME volumes-on-paths
COPY *.py /$PLUGIN_NAME/
COPY *.txt /$PLUGIN_NAME/
WORKDIR /$PLUGIN_NAME
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "-m", "flask", "--app", "plugin", "run", "--host=/run/docker/plugins/$PLUGIN_NAME.sock"]
