# Bot Management App

## Overview

This Django app allows for efficient management of bots across various platforms such as Telegram, eBay, WhatsApp, and more. The app handles the creation, deletion, and updating of bots, allowing a seamless user experience.

## Requirements

- Django
- Python
- Libraries for platform-specific bot integrations (Python-telegram-bot, facebook-sdk, etc.)

## Installation

1. Install Django and Python.
2. Clone this repository to your local machine.
3. Navigate to the directory where the project was cloned.
4. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

5. Set up your settings file. This includes setting up your database connection, your secret key, and the installed apps. Make sure to include `'bot_management'` in your installed apps.

## Usage

This app primarily functions through Django management commands. Here are some useful ones:

- `createbot`: This command is used to create a new bot. It takes the bot name and platforms as arguments.

    ```sh
    python manage.py createbot BotName -p telegram;whatsapp;facebook
    ```

    This command will prompt you for the necessary access tokens for each platform.

- `deletebot`: This command is used to delete an existing bot.

    ```sh
    python manage.py deletebot BotName
    ```

- `updatebot`: This command is used to update the details of a bot.

    ```sh
    python manage.py updatebot BotName
    ```

Each bot has its own `controller.py`, `commands.py`, `message_handlers.py`, `middleware.py`, and `templates` directory for managing the behavior of the bot.

When a message arrives from a platform, the system routes it to the appropriate bot based on the URL structure, which follows this pattern: `/<platform>/<bot_name>/bot_id`.

## Development

During development it is nessary to use ngrok to expose the local server to the internet. This is because the bot platforms require a URL to send messages to. To do this, follow these steps:

1. Install ngrok.
2. Run the following command:

    ```sh
    ngrok http https://127.0.0.1:8000/
    ```

3. Add the ngrok URL to the ALLOWED_HOSTS in the settings file.

## Documentation

For further details, check out the documentation [here](link_to_documentation).

## Contribution

Contributions are always welcome. Feel free to open an issue or submit a pull request.
