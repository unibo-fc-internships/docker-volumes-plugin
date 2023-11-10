FROM node:19

COPY package*.json /volumes-on-paths/
COPY index.js /volumes-on-paths/

WORKDIR /volumes-on-paths

ENTRYPOINT ["node", "index.js"]
