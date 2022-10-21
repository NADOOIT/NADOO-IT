This is the nadooit execution manegment system.

It forms the interface to the system, hosts the website, and provides the API.

## Pre-requisites
**git**

See the following link for instructions on installing git on your system: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git

**docker (with docker-compose)**

See the following link for instructions on installing docker on your system: https://docs.docker.com/engine/installation/


## Installation
1. Copy the repository to your servers home directory

git clone git@github.com:NADOOITChristophBa/nadooit_managmentsystem.git

2. Change into the directory

cd nadooit_managmentsystem

3. create .env file

cp .env.example .env
set the following variables in the .env file for first time setup:

To open the file in nano, type:

sudo nano .env

### Django
Replace your_secret_key with a new secret key. You can generate one here: https://miniwebtool.com/django-secret-key-generator/

DJANGO_SECRET_KEY=your_secret_key

### Nginx

ACME_DEFAUT_EMAIL=your_email

DOMAIN=your_domain

### Database

1. to find the following variables, go to https://cockroachlabs.cloud/
2. login or create an account
3. create a new cluster
4. set SQL user  to a username of your choice
5. click on generate user and password
6. copy the generated password and replace your_cockroach_db_password in the .env file
7. select the dopdown menu for Database and click on create database, name it as you like
8. Download the CA Cert
    - Select the operating system of your server
    - Copy curl command
    - Paste the command into your terminal

9. select option/language select Parameters only and replace the following variables in the .env file
    - your_cockroach_db_user = Username
    - your_cockroach_db_name = Database
    - your_cockroach_db_host = Host
    - your_cockroach_db_port = Port
    - your_cockroach_db_options = Options

COCKROACH_DB_HOST=your_cockroach_db_host

COCKROACH_DB_NAME=your_cockroach_db_name

COCKROACH_DB_PORT=your_cockroach_db_port

COCKROACH_DB_USER=your_cockroach_db_user

COCKROACH_DB_PASSWORD=your_cockroach_db_password

COCKROACH_DB_OPTIONS=your_cockroach_db_options

### Docker
4. Build the docker images
    - docker compose -f docker-compose.deploy.yml build
    - docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh


### Creating superuser
1. Run the following command to create a superuser
docker compose -f docker-compose.deploy.yml run --rm web python manage.py createsuperuser

### Starting the server
1. Run the following command to start the server
docker compose -f docker-compose.deploy.yml up -d

### Stopping the server
1. Run the following command to stop the server
docker compose -f docker-compose.deploy.yml down

### Updating the server
1. Run the following command to update the server
git pull
docker compose -f docker-compose.deploy.yml build
docker compose -f docker-compose.deploy.yml down
docker compose -f docker-compose.deploy.yml up -d


## Features

### List of implemented features
- [x] User management
- [x] Time tracking
- [x] API
- [x] Docker
- [x] SSL

### List of planned features
#### Pages and features for the website (frontend)
- [ ] Page for clients to see their time tracking
- [ ] Page for clients to see their invoices
- [ ] Page for clients to see their projects
- [ ] Page for clients to see their tasks
- [ ] Page for clients to see their users
- [ ] Page for clients to see their documents
- [ ] Page for clients to see their messages
- [ ] Page for clients to see their settings
- [ ] Page for clients to see their notifications
- [ ] Page for clients to see their calendar
- [ ] Page for clients to see their reports
- [ ] Page for clients to see their statistics
- [ ] Page for clients to see their tickets
- [ ] Page for clients to see their knowledge base
- [ ] Page for clients to see their announcements

#### Pages and features for the admin (backend)
- [ ] Project management
- [ ] Task management
- [ ] Invoice management
- [ ] File management
- [ ] Calendar
- [ ] Chat
- [ ] Email
- [ ] Notifications
- [ ] Settings
- [ ] Backup
- [ ] Restore
- [ ] Update
- [ ] Upgrade
- [ ] Downgrade
- [ ] Multi-tenancy
- [ ] Multi-language
- [ ] Multi-currency
- [ ] Multi-timezone
- [ ] Multi-country
- [ ] Multi-locale


## Local development
docker-compose -f docker-compose.yml run --rm app python manage.py makemigrations
docker-compose -f docker-compose.yml run --rm app python manage.py migrate