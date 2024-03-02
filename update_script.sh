#!/bin/bash

USER_HOME=$(eval echo ~$CURRENT_USER)

# navigate to the project directory
cd /home/$SUDO_USER/NADOO-IT

# stash any changes
git stash

# pull the latest changes
git pull

# build the docker images
docker compose -f docker-compose.deploy.yml build

# run migrations
docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate

# collect static files
docker compose -f docker-compose.deploy.yml run --rm app python manage.py collectstatic --noinput 

# import templates
docker compose -f docker-compose.deploy.yml run --rm app python manage.py import_templates

# take down the current docker containers
docker compose -f docker-compose.deploy.yml down

# bring up the new docker containers
docker compose -f docker-compose.deploy.yml up -d
