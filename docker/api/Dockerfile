FROM node:16-alpine3.14

# Create app directory
WORKDIR /usr/src/adelphi/api

# Install app dependencies
# A wildcard is used to ensure both package.json AND package-lock.json are copied
# where available (npm@5+)
COPY package*.json ./

RUN npm ci --only=production

# Bundle app source
COPY . .

EXPOSE 8181
CMD [ "npm", "start" ]