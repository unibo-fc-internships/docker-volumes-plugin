# Manual test
## Build 
```sh
docker image build . -t plugin_test
```
## one drive
```sh
docker run -it --rm -e NFS_MOUNT='127.0.0.1:/my_data /data rw,blabla' plugin_test
```
## two drives
```sh
docker run -it --rm -e NFS_MOUNT_1='127.0.0.1:/my_data /data rw,blabla' -e NFS_MOUNT_2='127.0.0.1:/my_data /data rw,blabla'  plugin_test
```
# what 

## on startup
- mounts all NFS drives on the FS
    - following given config (NFS_MOUNT)

## Create(volume_name)
- finds the drive on which the volume exists
- creates a dir locally

## Remove
- check if volume exists and is not mounted
- then removes it

## Mount
- creates a lock file in volume

## UnMount
- removes lock file in volume

# NFS
## expose
- install `nfs-utils` package
- add dir to share to `/etc/exports`, example:  
```
/srv/nfs            192.168.1.0/24(rw,sync,crossmnt,fsid=0)
/srv/nfs/Music      192.168.1.0/24(rw,sync)
```
> `/srv/nfs` is the best place for shared directories
- enable NFS server service
```sh
systemctl enable --now nfs-server.service
```

## mount 
- enable NFS client service
```sh
systemctl enable --now nfs-client.target
```
- mount remote directory manually
```sh
sudo mount -t nfs 137.204.71.19:/home/francois/Documents/ /mnt/
```
AKA <remote_IP>:<remote_dir_path> <local_dir_path>

> ⚠️ local_dir_path must be an existing directory

- OR in fstab
```
server01:/nfs/music   /data/nfs/music  nfs auto,x-systemd.automount,x-systemd.device-timeout=10,timeo=14,x-systemd.idle-timeout=1min 0 0
```