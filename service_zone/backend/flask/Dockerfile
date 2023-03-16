FROM python:3.11.0-buster

MAINTAINER Li XU

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN apt update && apt install -y gcc libgl1-mesa-glx &&\
    pip install --upgrade pip && \
    pip install -r requirements.txt

RUN apt update \
&& apt -y install gnupg2 curl \
&& curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
&& curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt update \
&& ACCEPT_EULA=Y apt -y install msodbcsql17 \
&& ACCEPT_EULA=Y apt -y install mssql-tools

RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc \
&& . ~/.bashrc

RUN apt update \
&& apt install python3-dev -y\
&& apt install g++ unixodbc-dev -y
