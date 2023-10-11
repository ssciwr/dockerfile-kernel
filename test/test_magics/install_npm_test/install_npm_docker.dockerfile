FROM node:current-alpine

WORKDIR /usr/app

RUN npm install express && npm cache clean --force