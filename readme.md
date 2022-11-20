# Intro

This is the nadooit execution manegment system.

It forms the interface to the system, hosts the website, and provides the API.

# Features

## List of planned packages

- [ ] django-extensions
- [ ] django-filter

## List of implemented features

- [x] User management
- [x] Time tracking
- [x] API
- [x] Docker
- [x] SSL
- [x] django-crispy-forms
- [x] django-bootstrap5
- [x] mfa using fido2 keys
- [x] htmx

## List of TODOs

### Pages and features for the website (frontend)

- [ ] Page for Nadooit_Workflow for adding new Processess
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

### Pages and features for the admin (backend)

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
- [ ] Multi-organization

### TODOs

- [ ] Move all pages to Nadooit-OS

### nadooit_subscriptions

This app is responsible for the subscription management.
It is used to manage the subscription of the clients.
It is used to create subscriptions for the clients.

- [ ] Add subscription management
- [ ] Add subscription management to the admin
- [ ] Add subscription management to the API

### nadooit_os

#### nadooit_os TODOs

##### Pages and features for the nadooit_os (frontend)

###### Programexecution Page

- [x] Add navbar to the table that shows the program executions
- [x] In the navbar there are  buttons for quick filters: Last20, This month, last month, this year, today
- [ ] Add a sorting to the diffrent columns of the table, sort by: date, time, program, status
- [ ] Add a row to the table that shows the program executions that shows the total time saved, total price for all executions
- [x] Turn executionlist into a component that can be used in other pages
- [ ] When the button to revoke the execution is clicked, the execution is revoked and the status is changed to revoked but the button is still there and the status is not updated

TODO: Check if when an execution is created at 0:00-0:59 it is counted as the previous day since the database is in UTC time while the users create the execution in their local time.

If I want to add filters I need to change it so that the tabel is a seperate view more like a rest api where I can say something like /executions/year/month/day and it returns me the table depending on what data was given for the route.
At the moment all data is retrieved from the backend and then pushed into the template and displayed.
This could result in huge table later and should be reworked

##### Bugfixes

- [x] Fix the bug that the if the manager goes to the overview page he is not shown all customers

### nadooit_images

This is an app for managing images.
It provides a model for images and a view for displaying them.
It generates thumbnails for images and provides a view for displaying them.
It lets you upload images and provides a view for displaying them.
It lets you delete images and provides a view for displaying them.
It creates easy to use urls for displaying images for use in templates and other places.

#### Usage

#### Installation

#### Configuration

#### API

#### nadooit_images TODOs

- [ ] Add app
- [ ] Add model for images
- [ ] Add view for displaying images
- [ ] Add thumbnail generation
- [ ] Add view for displaying thumbnails
- [ ] Add upload functionality
- [ ] Add view for displaying uploaded images
- [ ] Add delete functionality
- [ ] Add easy to use urls for displaying images
- [ ] Add easy to use urls for displaying thumbnails
- [ ] Add protection against directory traversal
- [ ] Add protection against path traversal
- [ ] Add protection against path injection
- [ ] Add protection against path manipulation
- [ ] Add way so that images can be shared between users but not publicly
- [ ] Add way to protect images with a password

### nadooit_api_key

#### Possible security issues

- [ ] Currently a API Key Manager has rights for all its customers. But it each customer should have sperate settings for the manager.

#### nadooit_api_key TODOs

##### List of features for the individual user

- [ ] Add option for User to create API Key for themselfs

##### List of features for Managers

- [ ] Add option for API Key Manager to create API Keys for diffrent users
- [ ] Add option for API Key Manager to revoke API Keys for a diffrent user

### nadooit_hr

#### nadooit_hr TODOs

- [x] Add page for currently logged in user to add a new user to a customer as an employee (if he has the rights)
- [x] Add functionalty to overview that the logged in user to can remove an employee from a customer (if he has the rights)
- [ ] Add a new role for the employee to see all employees and their roles of a customer (if he has the rights)
- [ ] Add a new role for the employee to revoke roles of all employees of a customer (if he has the rights)
- [ ] Add a new role for the employee to add roles to all employees of a customer (if he has the rights)
- [x] Create a list of all employees of a customer (if he has the rights)
  - [ ] Create a list of all employees of a customer with their roles and rights (if he has the rights)
- [ ] Add a page for the users profile to see all his roles and rights for all customers he is an employee with
  - [ ] This page can be accessed by the user and other users.
  - [ ] As a manager you can see all roles and rights of all employees of a customer (if you have the rights)
  - [ ] As a manager you can revoke roles and rights of all employees of a customer (if you have the rights)
-[ ] Add the deactivation date to the reactivation button
- [ ] Add a button to deactivate an employee	
- [ ] Add a button to reactivate an employee
- [ ] Add a button to delete an employee
- [ ] Add a button to add an employee
- [ ] Add a button to edit an employee
- [ ] Add a button to view an employee


### nadooit_program_ownership_system

#### nadooit_program_ownership_system TODOs

- [ ] Add page for seeing the program shares
- [ ] Add page for selling program shares
- [ ] Add page for buying program shares

### nadooit_workflow

#### nadooit_workflow TODOs

- [ ] Add option to add a new process
- [ ] Add option to add a new task
- [ ] Add option to add a new task type
- [ ] Add option to add a new task status  
- [ ] Add option to add a new task priority  
- [ ] Add option to add a new task category
- [ ] Add option to add a new task label
- [ ] Add option to add a new task tag  
- [ ] Add option to add a new task comment
- [ ] Add option to add a new task attachment  
- [ ] Add option to add a new task time tracking
- [ ] Add option to add a new task reminder
- [ ] Add option to add a new task checklist
- [ ] Add option to add a new task checklist item
- [ ] Add option to add a new task checklist item comment
- [ ] Add option to add a new task checklist item attachment
- [ ] Add option to add a new task checklist item time tracking
- [ ] Add option to add a new task checklist item reminder
- [ ] Add option to add a new task checklist item reminder comment
- [ ] Add option to add a new task checklist item reminder attachment
- [ ] Add option to add a new task checklist item reminder time tracking

#### Testing

- [ ] Add tests for nadooit_api_key
- [ ] Add tests for nadooit_api_execution_system
- [ ] Add tests for nadooit_auth
- [ ] Add tests for nadooit_crm
- [ ] Add tests for nadooit_delivery
- [ ] Add tests for nadooit_funnel
- [ ] Add tests for nadooit_hr
- [ ] Add tests for nadooit_key
- [ ] Add tests for nadooit_network
- [ ] Add tests for nadooit_os
- [ ] Add tests for nadooit_program
- [ ] Add tests for nadooit_program_ownership_system
- [ ] Add tests for nadooit_questions_and_answers
- [ ] Add tests for nadooit_time_account
- [ ] Add tests for nadooit_website
- [ ] Add tests for nadooit_workflow
- [ ] Add tests for nadooit_payment

#### Documentation

- [ ] Add documentation for nadooit_api_key
- [ ] Add documentation for nadooit_api_execution_system  
- [ ] Add documentation for nadooit_auth
- [ ] Add documentation for nadooit_crm
- [ ] Add documentation for nadooit_delivery
- [ ] Add documentation for nadooit_funnel
- [ ] Add documentation for nadooit_hr
- [ ] Add documentation for nadooit_key
- [ ] Add documentation for nadooit_network
- [ ] Add documentation for nadooit_os
- [ ] Add documentation for nadooit_program
- [ ] Add documentation for nadooit_program_ownership_system
- [ ] Add documentation for nadooit_questions_and_answers
- [ ] Add documentation for nadooit_time_account

#### Refactoring

#### Bugs

## Contributing

1. Fork it (
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

    docker compose -f docker-compose.yml build
    docker-compose -f docker-compose.yml run --rm app python manage.py makemigrations
    docker-compose -f docker-compose.yml run --rm app python manage.py migrate
    docker-compose -f docker-compose.yml run --rm app python manage.py createsuperuser
    docker-compose -f docker-compose.yml up

#### Running tests

To test the api go to https://127.0.0.1:8000/api/executions

give as Content: 
{
        "NADOOIT__API_KEY" : "98b10977-812d-430e-a89b-83bcf4101af3",
        "NADOOIT__USER_CODE" : "ePo2L7",
        "program_id" : "07c3a406-bd1b-43c2-b6a1-7fceb4389323"
}

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

##### Create a new user

        adduser nadooit
        usermod -aG sudo nadooit

##### Install docker

TODO Fill this section

#### Project setup

1. Copy the repository to your servers home directory

git clone git@github.com:NADOOITChristophBa/nadooit_managmentsystem.git

2. Change into the directory

cd nadooit_managmentsystem

3. create .env file

cp .env.example .env
set the following variables in the .env file for first time setup:

To open the file in nano, type:

sudo nano .env

#### Django

Replace your_secret_key with a new secret key. You can generate one here: <https://miniwebtool.com/django-secret-key-generator/>

DJANGO_SECRET_KEY=your_secret_key

#### Nginx

ACME_DEFAUT_EMAIL=your_email

DOMAIN=your_domain

#### Database

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

#### Docker

4. Build the docker images
    - docker compose -f docker-compose.deploy.yml build
    - docker compose -f docker-compose.deploy.yml run --rm certbot /opt/certify-init.sh

#### Creating superuser

1. Run the following command to create a superuser
docker compose -f docker-compose.deploy.yml run --rm app python manage.py createsuperuser

#### Starting the server

1. Run the following command to start the server
docker compose -f docker-compose.deploy.yml up -d

#### Stopping the server

1. Run the following command to stop the server
docker compose -f docker-compose.deploy.yml down

#### Updating the server

1. Run the following command to update the server
git pull
docker compose -f docker-compose.deploy.yml build
docker compose -f docker-compose.deploy.yml down
docker compose -f docker-compose.deploy.yml up -d
