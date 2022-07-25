FROM python:3.7

ADD . /app
ADD requirements.txt /app
WORKDIR /app

RUN pip install -r requirements.txt
