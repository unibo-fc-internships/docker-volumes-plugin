set -e
/usr/local/bin/python -m plugin.nfs
exec "$@"
