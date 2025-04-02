FROM python:3.11.7-alpine

WORKDIR /code

COPY requirements/base.txt requirements/base.txt
COPY requirements/production.txt requirements/production.txt


RUN pip3 install -r requirements/production.txt

COPY . /code

RUN mkdir -p /data/logs