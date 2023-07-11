# Create an example string for the structure of the post that can be used in text generation. Should be a json
# Example:
# post = {
#     "title": "",
#     "price": "",
#     "condition": "",
#     "details": {},
#     "quantity_available": "",
#     "minimum_quantity": "",
#     "location": "",
#     "delivery_options": "",
#     "link": "",
# }
post_structure = """
    post = {
        "title": "",	
        "price": "",		
        "condition": "",			
        "details": {},				
        "quantity_available": "",					
        "minimum_quantity": "",							
        "location": "",									
        "delivery_options": "",									
        "link": "",											
    }	
"""
examples = """
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

use_html_formatting = """
        Der Post soll mit Telegrams HTML Formatierung erstellt werden. 
        Beachte die folgenden Inforamtionen dazu aus der Telegram Dokumentation. 
        Nutze kein HTML das nicht in der Dokumentation steht! 
        Nutze somit auf keinen Fall <br>! Ich wiederhole das nutzen des html <br> ist absolut verboten!
        Verwende stattdessen " " um einen Zeilenumbruch zu erzeugen.
        \n\n
        
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


def create_text(base_instruction, data=None, examples=None, extra_information=None):
    """
    Create a text for the user to complete
    :param base_instruction: The base instruction for the user
    :param data: The data to clean
    :param examples: Examples of correct results
    :param extra_information: Extra information for the user
    :return: The text for the user to complete
    """
    extra_info_text = (
        f"\n\nHier sind noch zusätzliche Informationen die unbedingt beachtet werden müssen: {extra_information}"
        if extra_information
        else ""
    )
    examples_text = (
        f"\n\nHier sind einige Beispiele wie ein richtiges Ergebnis aussehen soll:\n{examples}"
        if examples
        else ""
    )
    data_text = f"\n\nNutze die folgenden Daten dafür:\n{data}" if data else ""

    text = f"""{base_instruction}{data_text}{examples_text}{extra_info_text}\n\n"""

    return text


def extract_details_from_text(text, extra_instructions=""):
    """
    Extracts the details from the text
    :param text: The text to extract the details from
    :return: The details
    """

    instruction = f"Extract the details from the text and return them in the following format as a json:\n\n {post_structure}, {extra_instructions}"

    promt = f"{instruction}\n\n + {text}"

    import openai

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein Marketing Experte der bei ReUse and Sell arbeitet. In diesem Fall bekommst du einen Text mit Informationen für eine Anzeige, die in Telegram veröffentlich werden soll.",
            },
            {"role": "user", "content": promt},
        ],
    )

    return response["choices"][0]["message"]["content"]


def change_text_with_instructions(text, instructions):
    import openai

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein Marketing Experte der bei ReUse and Sell arbeitet. In diesem Fall bekommst du einen Text mit Informationen für eine Anzeige, die in Telegram veröffentlich werden soll. Deine Aufgabe ist den Text so zu verändern, dass er den Anforderungen entspricht.",
            },
            {
                "role": "user",
                "content": f"Passe den Text entsprechend dieser Anweisung an:\n\n {instructions}\n\n + {text}",
            },
        ],
    )

    return response["choices"][0]["message"]["content"]


def change_quantity_available(text, quantity_available):
    """
    Change the quantity available in the text
    :param text: The text to change the quantity available
    :return: The changed text
    """

    base_instruction = f"Behalte den gegebenen Text bei. Verändere nur die verfügbare Menge zu folgendem Wert: {quantity_available}. Gebe nur den so angepassten Post zurück. Gebe keine zusätzlichen Informationen oder Meldungen zurück. Vermeide also sowas wie: Der generierte Post entspricht den Regeln und kann so veröffentlicht werden. Hier ist der korrigierte Post:"

    instruction = create_text(
        base_instruction=base_instruction,
        extra_information=use_html_formatting,
    )

    return change_text_with_instructions(
        text,
        instructions=instruction,
    )


def get_advert_post_for_data(data: dict):
    base_instruction = """
    Erstelle einen Telegram Post. 
    Regelen die immer eingehalten werden müssen für alle Posts:
    Mache:
    Der Post darf MAXIMAL 1024 Ziechen haben!,
    Verwende keine Einleitungstext oder gebe sonsitgen Texte sondern halte dich weitgehend an eine auflistund der Produktdaten.
    Halte dich so nahe wie möglich an die Beispiele und vermeide unnötige Wörter.
    Halte dich an das Ende der anderen Post aus den Beispielen!
    Der Post endet immer mit einem Link zu der Anzeige auf der Webseite. Zeige den Link vollständig an und nicht als href mit etwas wie Link.
    Tutst du dies wird der Link nicht als Link erkannt und kann nicht angeklickt werden.
    Liste immer verfügbare Mengen auf, wenn sie in den Daten angegeben sind.
    Das bedeutet sowohl wie viel verfügbar ist als auch was die Mindestabnahme ist.
    Mach nicht:
    Für weitere Informationen kontaktiere uns gerne über den Link oder direkt per Telegram @ReuseandSell.
    Verändere nicht ♻️❀♻️ReUse and Trade♻️❀♻️ durch etwas anderes wie ⚡️✨⚡️ReUse and Sell⚡️✨⚡️.
    Verändere **ReUse and Trade** nicht zu ReUse and Sell da ReUse and Trade der Firmenname ist.
    Verwende keine Hashtags.
    SCHREIBE DIE ANZEIGE IMMER IN DEUTSCH!!!!!
    
    """

    data_for_text = ""
    # Add all data to promt except the image link
    for key, value in data.items():
        if key != "img_link":
            data_for_text += f"<b>{key}</b>: {value}\n"

    # Now you can use the string html_documentation in your prompt
    extra_information = use_html_formatting

    import openai

    instruction = create_text(
        base_instruction=base_instruction,
        data=data_for_text,
        examples=examples,
        extra_information=extra_information,
    )

    retry_counter = 0
    max_retry = 3
    while retry_counter < max_retry:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Du bist ein Marketing Experte der bei ReUse and Sell arbeitet. In diesem Fall erstellst du eine Anzeige für, die in Telegram veröffentlich wird. Der andere Teilnehmer wird dir die Informationen und Vorlange zum Format des Posts geben.",
                },
                {
                    "role": "user",
                    "content": instruction,
                },
            ],
        )

        advert_post = response["choices"][0]["message"]["content"]

        # check the length of the post and if it is too long create it again
        if len(advert_post) > 1024 or len(advert_post) < 120:
            print("The advert post is too long or short. Try to generate it again")
            retry_counter += 1
            continue
        else:
            # check if post conforms to the rules
            instruction_for_check = """Überprüfe ob der generierte Post den Regeln entspricht. Wenn nein korrigiere die Fehler und gib den Post zurück. Wenn ja gib den Post unverändert zurück.Hier ist der Post:"""
            instruction_for_check += advert_post
            check_instruction = create_text(
                base_instruction=instruction_for_check,
                data=data_for_text,
                examples=examples,
                extra_information=extra_information,
            )

            check_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein Marketing Experte der bei ReUse and Sell arbeitet. In diesem Fall erstellst du eine Anzeige für, die in Telegram veröffentlich wird. Der andere Teilnehmer wird dir die Informationen und Vorlange zum Format des Posts geben.",
                    },
                    {
                        "role": "user",
                        "content": check_instruction,
                    },
                ],
            )

            advert_post = check_response["choices"][0]["message"]["content"]

            return advert_post

    raise ValueError(
        "Unable to generate the advert post within the character limit after 3 tries"
    )
