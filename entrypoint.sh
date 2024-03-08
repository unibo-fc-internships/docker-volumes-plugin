set -e
/usr/local/bin/python -m plugin.nfs
/usr/bin/bash -c "$@"
