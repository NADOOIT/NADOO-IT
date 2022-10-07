FROM python:3.10-alpine3.16
LABEL maintainer="nadooit.de"

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt

RUN mkdir /app
COPY app/ /app

RUN apk add --upgrade --no-cache build-base --virtual .tmp gcc libc-dev linux-headers git curl

#RUN curl --create-dirs -o app/.postgresql/root.crt -O https://cockroachlabs.cloud/clusters/250c4344-e9da-4ff8-992a-53ab1204afeb/cert

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static

#OLD RUN adduser -D --disabled-password --no-create-home django
RUN adduser -D --disabled-password django

RUN chown -R django:django app/
RUN chown -R django:django /vol
RUN chmod -R 755 app/
RUN chmod -R 755 /vol/web
WORKDIR /app

EXPOSE 8000

RUN chown -R django:django /app
RUN chown -R django:django /home/django
RUN chmod 755 /home/django
RUN chmod 755 /app
USER django

#RUN curl --create-dirs -o /app/.postgresql/root.crt -O https://cockroachlabs.cloud/clusters/250c4344-e9da-4ff8-992a-53ab1204afeb/cert
RUN curl --create-dirs -o /home/django/.postgresql/root.crt -O https://cockroachlabs.cloud/clusters/250c4344-e9da-4ff8-992a-53ab1204afeb/cert

RUN pip install --upgrade pip && \
       pip install -r /requirements.txt 


USER root

RUN apk del .tmp

USER django



CMD [ "uwsgi","--socket",":8000","--workers","4","--master","--enable-threads","--module","nadooit.wsgi" ]