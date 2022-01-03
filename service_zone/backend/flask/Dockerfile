FROM python:3.9-slim-bullseye

MAINTAINER Li XU

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN apt update && apt install -y gcc &&\
    pip install --upgrade pip && \
    pip install -r requirements.txt
