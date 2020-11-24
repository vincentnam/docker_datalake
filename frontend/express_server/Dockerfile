FROM node:13.12.0-alpine

RUN apk add bash && mkdir /datalake_tmp
#ENV PATH /app/node_modules/.bin:$PATH
WORKDIR /app
#RUN npm init
#RUN npm install react-scripts@3.4.1
COPY ./ ./
#COPY package.json ./
#COPY package-lock.json ./
RUN npm install
#COPY public ./public

CMD ["npm","start"]
#CMD ["bash"]