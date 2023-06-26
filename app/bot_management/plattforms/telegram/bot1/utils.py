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


def change_quantity_available(text, quantity_available):
    """
    Change the quantity available in the text
    :param text: The text to change the quantity available
    :return: The changed text
    """

    return extract_details_from_text(
        text,
        extra_instructions=f"Change the quantity available in the text to {quantity_available}",
    )


# base_instruction
# clean data as json
# examples of correct results
# extra information (documentation)


def create_text(base_instruction, data, examples, extra_information):
    """
    Create a text for the user to complete
    :param base_instruction: The base instruction for the user
    :param data: The data to clean
    :param examples: Examples of correct results
    :param extra_information: Extra information for the user
    :return: The text for the user to complete
    """
    return f"""{base_instruction}\n\nData:\n{data}\n\nExamples:\n{examples}\n\n{extra_information}"""


def create_post(data):
    base_instruction = "Erstelle einen Telegram Post. Nutze dazu die folgenden Daten:"

    data_for_text = ""
    # Add all data to promt except the image link
    for key, value in data.items():
        if key != "img_link":
            data_for_text += f"<b>{key}</b>: {value}\n"
