""" 
In this file you can define all commands for your bot.
All commands must be defined as a function with the following structure:

def command_name(message, token, *args, **kwargs):

The function must be decorated with the @register_command decorator.
The decorator takes the following arguments:
command_message: The message that triggers the command. This can be a list of strings with "/" as the first character.
"""
from functools import wraps
from bot_management.plattforms.telegram.bot_testbot.utils import *
from bot_management.plattforms.telegram.api import *

command_registry = {}


def register_command(*command_triggers, description=""):
    def decorator(command_func):
        @wraps(command_func)
        def _wrapped_command(message, token, *args, **kwargs):
            return command_func(message, token, *args, **kwargs)

        for trigger in command_triggers:
            command_registry[trigger] = (_wrapped_command, description)
        return _wrapped_command

    return decorator
