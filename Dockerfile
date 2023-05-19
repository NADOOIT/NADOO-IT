# ---- Base Node ----
FROM node:14 AS base
WORKDIR /app
COPY package*.json ./
RUN npm install && npm cache clean --force
COPY . .

# ---- Base Python ----
FROM python:3.10-slim-buster
LABEL maintainer="nadooit.de"

ENV PYTHONUNBUFFERED 1

# ---- Install system dependencies ----
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    gcc \
    libc-dev \
    linux-headers-amd64 \
    ffmpeg

RUN mkdir -p /vol/web/media/original_videos
RUN mkdir -p /vol/web/static
RUN mkdir -p /home/django/.postgresql/

# Add these lines
RUN chown -R django:django /vol/web/media
RUN chmod -R 755 /vol/web/media

WORKDIR /app

EXPOSE 8000

# ---- Copy Node dependencies ----
COPY --from=base /app .

# ---- Install Python dependencies ----
COPY requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install --upgrade cython
RUN pip install -r /requirements.txt 
RUN python manage.py collectstatic --noinput 

CMD [ "uwsgi","--socket",":9090","--workers","4","--master","--enable-threads","--module","nadooit.wsgi" ]
