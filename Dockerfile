FROM python:3.10-slim-buster
LABEL maintainer="nadooit.de"

RUN apt-get update && apt-get install -y git

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt
COPY app/ /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    gcc \
    libc-dev \
    linux-headers-amd64 && \
    unset https_proxy && \
    mkdir -p /vol/web/static/media && \
    mkdir -p /vol/web/static/static && \
    mkdir -p /home/django/.postgresql/ && \
    adduser --disabled-password --gecos '' django && \
    chown -R django:django app/ && \
    chown -R django:django /vol && \
    chmod -R 755 app/ && \
    chmod -R 755 /vol/web && \
    apt-get purge -y --auto-remove \
    build-essential \
    curl \
    git \
    gcc \
    libc-dev \
    linux-headers-amd64

WORKDIR /app
EXPOSE 8000

RUN chown -R django:django /app && \
    chown -R django:django /home/django && \
    chmod 755 /home/django && \
    chmod 755 /app

USER django

RUN pip install --upgrade pip --no-cache-dir && \
    pip install --upgrade cython --no-cache-dir && \
    pip install -r /requirements.txt --no-cache-dir && \
    python manage.py collectstatic --noinput

USER root

RUN pip install uwsgi --no-cache-dir

USER django

CMD ["uwsgi", "--socket", ":9090", "--workers", "4", "--master", "--enable-threads", "--module", "nadooit.wsgi"]
