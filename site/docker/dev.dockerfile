# Use this dockerfile again when we need the node server
FROM node:8.9

WORKDIR /root/

#RUN npm install --only=production

CMD [ "npm", "run", "dev:ui" ]
