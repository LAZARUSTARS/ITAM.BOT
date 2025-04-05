FROM python:3.11.7-alpine

WORKDIR /code

COPY requirements/base.txt requirements/base.txt
COPY requirements/dev.txt requirements/dev.txt

RUN pip3 install -r requirements/base.txt
RUN pip3 install -r requirements/dev.txt

COPY . /code

RUN mkdir -p /data/logs