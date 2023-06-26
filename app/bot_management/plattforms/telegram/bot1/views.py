from datetime import datetime
from bot_management.plattforms.telegram.bot1.utils import (
    extract_details_from_text,
    change_quantity_available,
)
from bot_management.plattforms.telegram.utils import get_message_for_request
from bot_management.core.wisper import transcribe_audio_file
from bot_management.plattforms.telegram.api import get_file
from bot_management.models import BotPlatform, Message, Voice, VoiceFile, User, Chat
from bot_management.plattforms.telegram.api import get_file_info
from bot_management.plattforms.telegram.utils import register_bot_route
from django.views.decorators.csrf import csrf_exempt
from bot_management.plattforms.telegram.api import (
    send_message,
    edit_message,
    send_photo,
)
import re
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.core.files.base import ContentFile


import time
import os


@register_bot_route("24a8ff21-ab91-4f53-b0c9-3a9b4fcb7b6a")
@csrf_exempt
def handle_message(request, *args, token=None, **kwargs):
    print(request)

    message = get_message_for_request(request, *args, token=token, **kwargs)

    print("Got message:")
    print(message)
    # If think I have an problem here with the message object
    # Even though I get a message object and it is not a HttpResponse object the if statement is not executed

    if message is not None and not isinstance(message, HttpResponse):
        # check if message has text

        print("Message and not HttpResponse")
        if message.text is not None:
            print("Message has text")
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

                edited_message = edit_message(
                    chat_id=last_message.chat.id,
                    message_id=last_message.message_id,
                    text="Hab die nachricht geändert",
                    token=token,
                )

                edited_message = edit_message(
                    chat_id=edited_message.chat.id,
                    message_id=edited_message.message_id,
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

                promt = (
                    "Erstelle einen Telegram Post. Nutze dazu die folgenden Daten:\n\n"
                )
                # Add all data to promt except the image link
                for key, value in data_for_item.items():
                    if key != "img_link":
                        promt += f"<b>{key}</b>: {value}\n"

                promt += "\n\n"

                html_documentation = """
                HTML style:
                To use this mode, pass HTML in the parse_mode field. The following tags are currently supported:
                <b>bold</b>, <strong>bold</strong>
                <i>italic</i>, <em>italic</em>
                <u>underline</u>, <ins>underline</ins>
                <s>strikethrough</s>, <strike>strikethrough</strike>, <del>strikethrough</del>
                <span class="tg-spoiler">spoiler</span>, <tg-spoiler>spoiler</tg-spoiler>
                <b>bold <i>italic bold <s>italic bold strikethrough <span class="tg-spoiler">italic bold strikethrough spoiler</span></s> <u>underline italic bold</u></i> bold</b>
                <a href="http://www.example.com/">inline URL</a>
                <a href="tg://user?id=123456789">inline mention of a user</a>
                <tg-emoji emoji-id="5368324170671202286">👍</tg-emoji>
                <code>inline fixed-width code</code>
                <pre>pre-formatted fixed-width code block</pre>
                <pre><code class="language-python">pre-formatted fixed-width code block written in the Python programming language</code></pre>

                Please note:
                Only the tags mentioned above are currently supported.
                All <, > and & symbols that are not a part of a tag or an HTML entity must be replaced with the corresponding HTML entities (< with &lt;, > with &gt; and & with &amp;).
                All numerical HTML entities are supported.
                The API currently supports only the following named HTML entities: &lt;, &gt;, &amp; and &quot;.
                Use nested pre and code tags, to define programming language for pre entity.
                Programming language can't be specified for standalone code tags.
                A valid emoji must be used as the content of the tg-emoji tag. The emoji will be shown instead of the custom emoji in places where a custom emoji cannot be displayed (e.g., system notifications) or if the message is forwarded by a non-premium user. It is recommended to use the emoji from the emoji field of the custom emoji sticker.
                Custom emoji entities can only be used by bots that purchased additional usernames on Fragment.
                """

                # Now you can use the string html_documentation in your prompt
                promt = (
                    promt
                    + """
                    Der Post soll mit HTML erstellt werden. 
                    Beachte die folgenden Inforamtionen dazu aus der Telegram Dokumentation. 
                    Nutze kein HTML das nicht in der Dokumentation steht! 
                    Nutze somit auf keinen Fall <br>! Ich wiederhole das nutzen des html <br> ist absolut verboten!
                    Verwende stattdessen " " um einen Zeilenumbruch zu erzeugen.
                    \n\n"""
                    + html_documentation
                )

                example = """
                Panasonic FP-7113 Drucker
                
                Preis: 60,- € pro Stück, inkl. MwSt.

                Details: 
                Zählerstand: 232776 
                Gerät war zuletzt bei einer Anwaltskanzlei in Benutzung. 
                
                Verfügbare Gesamtmenge: 1St. 
                Mindestabnahmemenge: 1St 
                Zustand: gebraucht 
                
                
                Standort: Paderborn 
                Lieferoption: Nur Abholung
                ♻️❀♻️ReUse and Trade♻️❀♻️
                https://www.kleinanzeigen.de/s-anzeige/panasonic-fp-7113-drucker/2467410999-225-2164
                
                und weiteres Beispiel:
                Beschreibung: Bedientheke, Tresen, Theke, Empfangstresen, inkl. Stühle, zzgl. Tresor 
                
                Preis: 9.500,00 €, zzgl. MwSt.  
                Preisart: VHB 
                
                Zustand: gebraucht / Der Tresen ist bereits demontiert. 
                
                </div>Details: 
                - hochwertige Individualanfertigung 
                
                - nur 2,5 Jahre alt 
                
                - Breite: ca. 5 m 
                
                - Material: Eiche hell (Nachbildung) und schwarz lackierte MDF 
                
                - minimale Gebrauchsspuren an zwei kleinen Stellen (weitere Bilder gerne auf Anfrage) 
                
                - inkl. 2 passende Stühle 
                
                - Neupreis: 16.000 € 
                
                Tresor "cashmaster TT" - auf Anfrage 
                Verfügbare Menge: 1 
                Zwischenverkauf vorbehalten.
                
                Standort: Münsterland 
                Lieferoptionen: Abholung Der Tresen ist bereits demontiert.

                ♻️❀♻️ReUse and Trade♻️❀♻️
                https://www.reuseandtrade.de/artikeldetails/Tresen-Theke-Empfangstresen-inkl-Stuehle-zzgl-Tresor.aspx
                """

                promt = (
                    promt
                    + "\n\n"
                    + """
                    Beispiele wie ein Post aussehen soll. Halte dich bei der Struktur soweit wie möglich an das Beispiel.
                    Erstelle passende Text blöcke die durch Freizeilen voneinander getrennt sind. Vermeide zu lange Textblöcke.
                    Es sollten nie mehr als 3 Textblöcke sein. 
                    Highlighte Kernzahlen wie Preis und Stückzahlen durch fetdruck(bold).
                    Vermeide dopplungen von Informationen.
                    Füge am Ende des Posts immer den Link zu ReUse and Trade ein.
                    Vermeide übermäsige alle Emojis bis auf die für den ReUse and Trade block unten.
                    Das hier soll eine Anzeige sein und kein Emoji Fest.
                    Auch halte dich an das Layout des Beispiels und verwende mehr ein
                    
                    - Preis: 60,- € pro Stück, inkl. MwSt.
                    - Eigenschaft: Wert
                    - Eigenschaft: Wert
                    - ...
                    
                    Format anstelle von Fließtext.
                    
                    Vermeide sowas wie das hier: "🐝🎉 Willkommen bei ReUse and Trade 🎉🐝" die Nutzer befinden sich bereits in der Telegram Gruppe und wissen bescheid.
                    
                    Die Zielgruppe sind Händler und keine Privatpersonen. 
                    
                    Zeige den Link immer als "ReUse and Trade" an und nicht den Link text selber. Verwende dazu href. 
                    Verwende am Ende unbedingt ♻️❀♻️ReUse and Trade♻️❀♻️ :\n\n"""
                    + example
                )

                promt = promt + "\n\n" + "MAXIMAL 1024 Ziechen!!!!!!!!! \n\n"

                print(promt)

                print("got to here")
                """ Option Textcompletion
                import openai

                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=promt,
                    max_tokens=1100,
                )

                text = response.choices[0].text.strip()
                """

                # Option Chatbot

                import openai

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein Marketing Experte der bei ReUse and Sell arbeitet. In diesem Fall erstellst du eine Anzeige für, die in Telegram veröffentlich wird. Der andere Teilnehmer wird dir die Informationen und Vorlange zum Format des Posts geben.",
                        },
                        {"role": "user", "content": promt},
                    ],
                )

                print(response)

                text = response["choices"][0]["message"]["content"]

                print("This is the text: ")

                print(text)

                print("got to here 2")

                new_message = send_photo(
                    chat_id=message.chat.id,
                    photo=data_for_item["img_link"],
                    token=token,
                    caption=text,
                    parse_mode="HTML",
                )
                # HTTPResponse 400
                retrys = 3
                if new_message is HttpResponse:
                    while retrys > 0 and new_message is HttpResponse:
                        new_message = send_photo(
                            chat_id=message.chat.id,
                            photo=data_for_item["img_link"],
                            token=token,
                            caption=text,
                            parse_mode="HTML",
                        )
                        retrys = retrys - 1

                time.sleep(5)

                new_data = change_quantity_available(text, "2016")

                send_message(
                    chat_id=message.chat.id,
                    text=new_data,
                    token=token,
                )


            

                """ 
                edit_message(
                    chat_id=message.chat.id,
                    token=token,
                    message_id=new_message["message_id"],
                )
                 """
            else:
                send_message(
                    chat_id=message.chat.id,
                    text=message.text,
                    token=token,
                )
    print("GOT HERE ...")
    return HttpResponse("OK")
