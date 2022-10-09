FROM python:3.10-alpine3.16
LABEL maintainer="nadooit.de"

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt

RUN mkdir /app
COPY ./app /app

WORKDIR /app

EXPOSE 8000

RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers git curl
RUN curl --create-dirs -o app/.postgresql/root.crt -O https://cockroachlabs.cloud/clusters/250c4344-e9da-4ff8-992a-53ab1204afeb/cert

RUN pip install --upgrade pip && \
       pip install -r /requirements.txt && \
       adduser --disabled-password --no-create-home app
RUN apk del .tmp

USER app