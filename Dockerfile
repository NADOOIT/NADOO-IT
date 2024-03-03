#TODO Check for new versions of the base image. If a new version is available, rebuild the image.
FROM python:3.10-slim-buster
LABEL maintainer="nadooit.de"

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /requirements.txt

RUN mkdir /app
COPY app/ /app

# Update the package lists and install dependencies required for mysqlclient
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    gcc \
    libc-dev \
    linux-headers-amd64 \
    ffmpeg \
    default-libmysqlclient-dev \ 
    pkg-config

# Optional: Cleanup the apt cache to reduce image size
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN unset https_proxy

RUN mkdir -p /vol/web/media/original_videos
RUN mkdir -p /vol/web/static
RUN mkdir -p /home/django/.postgresql/

# Update to use adduser with correct options for Debian-based distributions
RUN adduser --disabled-password --gecos "" django

RUN chown -R django:django /app
RUN chown -R django:django /vol
RUN chown -R django:django /home/django

RUN chmod -R 755 /app
RUN chmod -R 755 /vol/web
RUN chmod -R 755 /home/django

# Add these lines for media volume permissions
RUN chown -R django:django /vol/web/media
RUN chmod -R 755 /vol/web/media

WORKDIR /app

EXPOSE 8000

USER django

RUN pip install --upgrade pip
RUN pip install --upgrade cython
RUN pip install -r /requirements.txt 
RUN python manage.py collectstatic --noinput 

USER root
RUN pip install uwsgi

USER django

CMD [ "uwsgi", "--socket", ":9090", "--workers", "4", "--master", "--enable-threads", "--module", "nadooit.wsgi" ]
