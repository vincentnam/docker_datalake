FROM python:3.9-alpine

MAINTAINER Li XU

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN apk add --update --no-cache g++ linux-headers &&\
    pip install --upgrade pip && \
    pip install -r requirements.txt
