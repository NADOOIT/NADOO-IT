from datetime import datetime
from bot_management.plattforms.telegram.bot1.utils import (
    change_quantity_available,
    get_advert_post_for_data,
)
from bot_management.models import *
from bot_management.plattforms.telegram.utils import register_bot
from django.views.decorators.csrf import csrf_exempt
from bot_management.plattforms.telegram.utils import *
from bot_management.plattforms.telegram.api import *
from django.http import HttpResponse
from celery import shared_task


# process_message is called by bot if the request contains a message
# This message is of type Message and then gets processed
# This is handled by a celery task
@shared_task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def process_message(message_id, token: str):
    message = Message.objects.get(message_id=message_id)

    # check if message has text
    print("Message and not HttpResponse")
    if message.text is not None:
        if message.text.startswith("/update"):
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

        elif message.text.startswith("/create"):
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

        else:
            send_message(
                chat_id=message.chat.id,
                text=message.text,
                token=token,
            )


@csrf_exempt
# @register_bot(bot_id="24a8ff21-ab91-4f53-b0c9-3a9b4fcb7b6a")
def bot(request, *args, token=None, **kwargs):
    print(request)

    message = get_message_for_request(request, *args, token=token, **kwargs)

    # If think I have an problem here with the message object
    # Even though I get a message object and it is not a HttpResponse object the if statement is not executed
    if message is not None and not isinstance(message, HttpResponse):
        print("Message and not HttpResponse")
        process_message.delay(message.message_id, token)

    return HttpResponse("OK")
