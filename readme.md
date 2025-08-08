# Intro

This is the nadooit execution manegment system.

It forms the interface to the system, hosts the website, and provides the API.

## Documentation

- Project docs index: [docs/README.md](docs/README.md)
- Running (Dev & Prod): [docs/running.md](docs/running.md)
- Installation on IONOS VPS: [docs/installation-ionos-vps.md](docs/installation-ionos-vps.md)
- Architecture overview: [docs/architecture.md](docs/architecture.md)
- Project structure and components: [docs/project-structure.md](docs/project-structure.md)
- Apps and services catalog: [docs/apps-and-services.md](docs/apps-and-services.md)
- Database backends: [docs/database.md](docs/database.md)
- Configuration (env vars): [docs/configuration.md](docs/configuration.md)
- Operations (backups, updates, logs): [docs/operations.md](docs/operations.md)
- Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- API reference: [docs/api.md](docs/api.md)
- Website system (sections, videos, files): [docs/website-system.md](docs/website-system.md)

Database default: SQLite. CockroachDB is optional (enable via env) and will get a migration script when we scale.

## Contributing

1. Fork the package
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)

## Installation and setup

## Development

For up-to-date development instructions, see:
- Running (Dev & Prod): [docs/running.md](docs/running.md)
- Installation on IONOS VPS (optional): [docs/installation-ionos-vps.md](docs/installation-ionos-vps.md)

## Production

For production deployment, follow:
- Installation on IONOS VPS (Dev & Production): [docs/installation-ionos-vps.md](docs/installation-ionos-vps.md)
- Running (Dev & Prod): [docs/running.md](docs/running.md)

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

Note: The canonical documentation for the website system (sections, video/file hosting) is in [docs/website-system.md](docs/website-system.md).

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
