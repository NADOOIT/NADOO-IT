from typing import Dict, Callable
import os
import importlib
from bot_management.plattforms.telegram.exceptions import (
    InvalidMessageDataError,
    BotPlatformNotFoundError,
)
from django.http import HttpResponse
from bot_management.plattforms.telegram.utils import (
    get_bot_info_from_id,
    get_message_for_request,
)
from bot_management.models import *
from bot_management.plattforms.telegram.api import send_message
from celery import shared_task
from django.db.models import Q
from celery import shared_task


def create_all_bots(parent_package):
    process_message_funcs = {}

    for bot_folder in os.listdir(os.path.dirname(os.path.realpath(__file__))):
        # Ensuring bot_folder is a directory and starts with 'bot_'
        if bot_folder.startswith("bot_") and os.path.isdir(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), bot_folder)
        ):
            bot_name = bot_folder[4:]  # removing 'bot_' prefix
            try:
                commands_module = importlib.import_module(
                    f"{parent_package}.{bot_folder}.commands"
                )
                command_registry = commands_module.command_registry
                process_message_funcs[bot_name] = command_registry
            except Exception as e:
                print(f"Error importing {bot_folder}.commands: {e}")

    return process_message_funcs


# Create process_message function for all bots
all_bots = create_all_bots("bot_management.plattforms.telegram")


def bot(request, bot_register_id, token=None, *args, **kwargs):
    print(request)

    try:
        data = request.data
        print(f"Data in get_message_for_request: {data}")

        if "message" in data:
            try:
                message = get_message_for_request(request, token, *args, **kwargs)

                if message is not None and not isinstance(message, HttpResponse):
                    print("Message and not HttpResponse")
                    bot_name, platform = get_bot_info_from_id(bot_register_id)

                    print(f"Bot name: {bot_name}")
                    print(f"Platform: {platform}")
                    print(all_bots)

                    process_message.delay(message.message_id, token, bot_name)

            except BotPlatformNotFoundError:
                return HttpResponse("Invalid token.", status=400)
            except InvalidMessageDataError:
                return HttpResponse("Invalid data. No 'message' found.", status=400)

    except Exception as e:
        print(e)

    return HttpResponse("OK")


# This is an async function that processes the message
@shared_task
def process_message(message_id, token: str, bot_name):
    # Getting command_registry for bot_name
    command_registry = all_bots[bot_name]

    # Change Back message = Message.objects.get(message_id=message_id)

    message = None

    # Check if message has text and if it's a command
    if message.text is not None and message.text.startswith("/"):
        # Split the command and the arguments
        command, args = (
            message.text.split(" ", 1) if " " in message.text else (message.text, "")
        )

        """ 
        # If user is in a conversation
        if message.conversation_state:
            # If the command sent by user is same as the one in conversation
            if message.conversation_state.command == command:
                # Ask if user wants to continue conversation
                # TODO: Implement the way to ask user and handle the response
            else:
                # If different command is sent, ask if user wants to pause the current conversation
                # TODO: Implement the way to ask user and handle the response

        paused_conversations = Message.objects.filter(
            Q(conversation_state__status='paused') & Q(conversation_state__command=command)
        )
        # If there are paused conversations for this command
        if paused_conversations:
            # Ask user if they want to continue one of these conversations
            # TODO: Implement the way to ask user and handle the response
        """

        # Check if command exists in the registry and run it
        if command in command_registry:
            command_func, _ = command_registry[
                command
            ]  # We don't need the description here, so we just ignore it
            command_func(message, token, args)

        # If command is not registered, you can send a default message or do nothing
        else:
            send_message(
                chat_id=message.chat.id,
                text=f"Unknown command: {command}",
                token=token,
            )

    # If message is not a command, you can send a default message or do nothing
    if message.text is not None and not message.text.startswith("/"):
        send_message(
            chat_id=message.chat.id,
            text=f"Unknown message: {message.text}",
            token=token,
        )
