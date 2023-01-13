FROM node:19

COPY package*.json /project/
COPY index.js /project/

WORKDIR /project

RUN npm install

ENTRYPOINT ["node", "index.js"]
