set -e
/usr/local/bin/python -m plugin.nfs

#handle_docker_event(){
#  docker events --filter "name=francoisjn/nfs-volumes" --filter "event=disable" | while read event
#  do
#    echo "Event: $event" >> /var/lib/docker/x-drives/137.204.71.10__NFS_share/entrypoint.log
#  done
#}
#
#handle_docker_event &

exec "$@"
