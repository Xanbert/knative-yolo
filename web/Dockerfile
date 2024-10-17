FROM node:10

WORKDIR /usr/src/comp4651

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 4000

CMD [ "npm", "run", "server" ]