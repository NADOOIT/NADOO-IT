""" 
In this file you can define all commands for your bot.
All commands must be defined as a function with the following structure:

def command_name(message, token, *args, **kwargs):

The function must be decorated with the @register_command decorator.
The decorator takes the following arguments:
command_message: The message that triggers the command. This can be a list of strings with "/" as the first character.
"""
from functools import wraps

from functools import wraps
from bot_management.plattforms.telegram.bot1.utils import *
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


@register_command(
    "/update",
    description="With this command, the user can update an existing article. The user will be asked for the new title and description.",
)
def update_command(message, token, *args, **kwargs):
    send_message(
        chat_id=message.chat.id,
        text=(
            "<b>Neuen Artikel anlegen.</b> "
            "Antworten Sie bitte <u>jeweils</u> auf die folgenden Fragen. "
            "Nutzen Sie hierzu <code>Text</code> oder <em>Sprachnachrichten</em>."
        ),
        token=token,
        parse_mode="HTML",
    )

    send_message(
        chat_id=message.chat.id,
        text="Wie lautet der Titel?",
        token=token,
    )

    last_message = send_message(
        chat_id=message.chat.id,
        text="Wie lautet die Beschreibung?",
        token=token,
    )

    edited_message = edit_message_text(
        message=last_message,
        text="Hab die nachricht geändert",
        token=token,
    )

    edited_message = edit_message_text(
        message=last_message,
        text="Hab die nachricht nochmal geändert",
        token=token,
    )


@register_command(
    "/create",
    description="With this command, the user can create a new advert. The user will be guided through the process of creating an advert.",
)
def create_command(message, token, *args, **kwargs):
    data_for_item = {
        "description": "Fahrradglocke, Fahrradklingel, Metall, mit Blumenmuster",
        "price": 0.83,
        "condition": "Restposten (Neuware)",
        "quantity_available": 14184,
        "minimum_quantity": 1008,
        "location": "Rheinland",
        "details": """   
                - Artikel: Fahrradglocke 
                
                - Zustand: Neuware 
                
                - Modell: Blumenmuster mit Lenkerhalterung (s. Bilder) 
                
                - Material: Metall 
                
                - Durchmesser: 8 cm 
                
                - Höhe: 5 cm (ohne Halterung) """,
        "delivery_options": "Versand durch Spedition - Kosten individuell nach PLZ und Aufwand",
        "link": "https://www.reuseandtrade.de/artikeldetails/Fahrradglocke--Fahrradklingel-metall-mit-Blumenmuster-ab-48-St.aspx",
        "img_link": "https://www.reuseandtrade.de/ReUseAndTrade/CustomUpload/374O357O340O370O356O369O350O337O356O340O370O356O352O365O355O339O369O352O355O356O/IMG_8694.jpg",
    }

    text = get_advert_post_for_data(data_for_item)

    new_message = send_photo(
        chat_id=message.chat.id,
        photo=data_for_item["img_link"],
        token=token,
        caption=text,
        parse_mode="HTML",
    )

    print(new_message)

    caption = PhotoMessage.objects.filter(message=new_message).first().caption

    # HTTPResponse 400
    retrys = 3
    if new_message is HttpResponse:
        while retrys > 0 and new_message is HttpResponse:
            new_message = send_photo(
                chat_id=message.chat.id,
                photo=data_for_item["img_link"],
                token=token,
                caption=get_advert_post_for_data(data_for_item),
                parse_mode="HTML",
            )
            retrys = retrys - 1

    new_data = change_quantity_available(caption, "2016")

    print("EDITING MESSAGE")

    print(new_data)

    edit_message_caption(
        message=new_message,
        token=token,
        caption=new_data,
        parse_mode="HTML",
    )
