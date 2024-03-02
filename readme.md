# Intro

This is the nadooit execution manegment system.

It forms the interface to the system, hosts the website, and provides the API.

## Contributing

1. Fork the package
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)

## Installation and setup

## Development

### Local development setup

1. Install github desktop (<https://desktop.github.com/>)
2. Clone the repository
3. Install docker (<https://www.docker.com/>)
4. Install docker-compose
5. Install newst version of python (<https://www.python.org/downloads/>)
6. Install update pip (pip install --upgrade pip)
   6.1 open cmd and type pip install --upgrade pip

7. use the following command to install the requirements

    docker compose -f docker-compose-dev.yml build
    docker-compose -f docker-compose-dev.yml run --rm app python manage.py makemigrations
    docker-compose -f docker-compose-dev.yml run --rm app python manage.py migrate
    docker-compose -f docker-compose-dev.yml run --rm app python manage.py import_templates
    docker-compose -f docker-compose-dev.yml run --rm app python manage.py createsuperuser
    docker-compose -f docker-compose-dev.yml up

#### Running tests

##### Testing the API

To test the api go to <https://127.0.0.1:8000/api/executions>

give as Content:
{
        "NADOOIT__API_KEY" : "407de0db-1a05-4dbc-982c-7921318c1020",
        "NADOOIT__USER_CODE" : "YFttKo",
        "program_id" : "a5bfdff9-bfc5-4141-829b-656f87ae2282"
}

##### Prefered way to run tests using tox

To run the tests, use the following command:

The following command will can be run either in a virtual environment.

    tox

    add -s to show print statements

##### Running tests with pytest

To run the tests, use the following command:

First activate the virtual environment:

    venv\Scripts\activate

change into the directory:

    cd app

then you can use the following commands to run pytest:

All tests:
removing the -s will hide the print statements
    pytest -s

Tests with a specific name:
    pytest -s -k  "test_get__employee_roles_and_rights__for__employee__with__"

##### Coverage

The coverage report does ignore apps.py

### Adding a new User Role to the system

1. Create a new app
2. Create a new model that is called XcZcManager
  Add the following fields to the model:
  employee = models.OneToOneField(employee, on_delete=models.CASCADE)
  list_of_customers_the_manager_is_responsible_for = models.ManyToManyField(Customer, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
3. Add the following to the app to the list of apps in the settings.py file
4. Create migrations and migrate

## Production

### Pre-requisites

1. git

    See the following link for instructions on installing git on your system: <https://git-scm.com/book/en/v2/Getting-Started-Installing-Git>

2. docker
3. docker-compose

See the following link for instructions on installing docker on your system: <https://docs.docker.com/engine/installation/>

### Installation

#### Server setup

##### Automatic

    Download the setup.sh script from the repository or copy the contents into a new file named setup.sh on your server.
    Make the script executable by running chmod +x setup.sh.
    Run the script with ./setup.sh.
    Follow the prompts to provide the required information for the .env file.
    Note: The automatic setup will clone the repository, create the .env file, and perform the necessary steps for project setup, including building Docker images, running migrations, creating a superuser, and starting the server.
    To do this you need to also add your ssh key to the github account.

##### Manuel

###### Create a new user

        adduser nadooit
        usermod -aG sudo nadooit

###### Install docker

TODO Fill this section

##### Project setup

1. Copy the repository to your servers home directory

    git clone <git@github.com>:NADOOIT/NADOO-IT.git

2. Change into the directory

    cd NADOO-IT

3. create .env file

cp .env.example .env
set the following variables in the .env file for first time setup:

To open the file in nano, type:

sudo nano .env

##### Django

Replace your_secret_key with a new secret key. You can generate one here: <https://miniwebtool.com/django-secret-key-generator/>

DJANGO_SECRET_KEY=your_secret_key

##### Nginx

ACME_DEFAUT_EMAIL=your_email

DOMAIN=your_domain

##### Database

1. to find the following variables, go to <https://cockroachlabs.cloud/>
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

##### Docker

##### Build the docker images

    - docker compose -f docker-compose.deploy.yml build
    - docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh

##### Running migrations

1. The database needs to be migrated before the server can be started. To do this, run the following command:
    - docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate

##### Creating superuser

1. Run the following command to create a superuser
docker compose -f docker-compose.deploy.yml run --rm app python manage.py createsuperuser

### Starting the server

1. Run the following command to start the server
docker compose -f docker-compose.deploy.yml up -d

### Stopping the server

1. Run the following command to stop the server
docker compose -f docker-compose.deploy.yml down

### Updating the server

Run the following command to update the server

    git stash

    git pull

    docker compose -f docker-compose.deploy.yml build
    
    docker compose -f docker-compose.deploy.yml run --rm app python manage.py migrate
    
    docker compose -f docker-compose.deploy.yml run --rm app python manage.py collectstatic --noinput 

    docker compose -f docker-compose.deploy.yml run --rm app python manage.py import_templates

    docker compose -f docker-compose.deploy.yml down

    docker compose -f docker-compose.deploy.yml up -d

## How to Use

### New Customer workflow

#### Create a new customer

go to <https://nadooit.de/admin/nadooit_crm/customer/add/>

fill out the form

#### Create a new employee contract, employee and user as the lead of the customer

go to <https://nadooit.de/admin/nadooit_hr/employeecontract/add/>

#### Create a new api key manager contract for the customer

go to <https://nadooit.de/admin/nadooit_api_key/nadooitapikeymanager/add/>

#### Create a customer manager contract for the customer with the master account

go to <https://nadooit.de/admin/nadooit_hr/customermanagercontract/add/>

#### Create a customer program execution manager contract for the customer with the master account

go to <https://nadooit.de/admin/nadooit_hr/customerprogramexecutionmanagercontract/add/>

#### Create a customer program manager contract for the customer with the master account

go to <https://nadooit.de/admin/nadooit_hr/customerprogrammanagercontract/add/>

#### Add a security key to the main customer user account

first sighn in to the main customer user account. If there is currently no key associated with the account, you will be be able to just sign in without a password.

after you have signed in, go to <https://nadooit.de/mfa/fido2/>

if you have a PC with fido2 support it will ask you if you want to add it. Cancel the process and go to the next step.

It will ask you to insert a security key. Insert the security key and click on the button.

It will ask you to setup a password. Setup a password and click on the button. The default password is 123456.

Follow the instructions on the screen to add the security key.

Test the security key by signing out and signing in again.

### Nadooit Website

The Nadooit Website is the main website for the Nadooit project. It is a infinite scroll website that infoms visitors about the Nadooit project and the Nadooit products.

#### Managment Commands

Because the page is build from sections that are stored in the database, the page can be edited by the admin.
Also all sections are available as templates in the sections_templates folder.

Because the page is build from sections that are stored in the database, it is important to sync the database with the sections_templates folder.

To retrieve all sections from the database and save them as templates in the sections_templates folder, run the following command:

    docker compose -f docker-compose-dev.yml run --rm app python manage.py export_templates

To then retrieve all sections from the sections_templates folder and save them in the database, run the following command:

    docker compose -f docker-compose-dev.yml run --rm app python manage.py import_templates

#### Sections

Sections contain the content of the website. They are stored in the database and can be edited by the admin.

Sections can contain the following elements:

- Text
- Image
- Video
- File downloads

For embedding a video first upload the video. Then in the sections admin page select the video from the dropdown menu.

Then add the following html block to the html at the place where the video should be displayed:

    <div class="video-container">
        {{ video }}
    </div>

For embedding a file download first upload the file. Then in the sections admin page select the file from the dropdown menu.

Then add the following html block to the html at the place where the file download should be displayed:

    <div class="file-container">
        {{ file }}
    </div>

### Bot Management

For details on the bot management app, see [the bot management app README](app/bot_management/README.md).
