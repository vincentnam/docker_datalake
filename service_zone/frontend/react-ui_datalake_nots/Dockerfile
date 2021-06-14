FROM node:13.12.0-alpine

RUN apk add bash
#ENV PATH /app/node_modules/.bin:$PATH
WORKDIR /app
RUN npm install react-scripts@3.4.1
COPY package.json ./
COPY package-lock.json ./
RUN npm install --silent --save
COPY public ./public
COPY src ./src

CMD ["npm","start"]
#CMD ["bash"]