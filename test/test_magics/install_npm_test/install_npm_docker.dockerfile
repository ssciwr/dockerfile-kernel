# This is the reference dockerfile against which the mymagic_magic.dockerfile is tested

FROM node:current-alpine

WORKDIR /usr/app

RUN npm install express && npm cache clean --force