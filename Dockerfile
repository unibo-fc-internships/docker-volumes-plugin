FROM node:19

COPY package*.json /project/
COPY index.js /project/

WORKDIR /project

# Install GLUSTERFS
RUN apt-get update -y && \
    apt install glusterfs-server -y && \
    apt install supervisor -y
    #systemctl start glusterd && \
    #systemctl enable glusterd

# Mount shared folder
#RUN mkdir -p /mnt/persistent && \
 #   echo '192.168.13.119:/gv0 /mnt/persistent glusterfs defaults,_netdev,log-level=WARNING,log-file=/var/log/gluster.log 0 0' >> /etc/fstab && \
 #   mount

# Install node modules
#RUN npm install
#ENTRYPOINT ["node", "index.js"]
