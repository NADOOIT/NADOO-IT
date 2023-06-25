from django.shortcuts import render

# Create your views here.
# This view is used to retrun a chatwindow for the user to interact with the bot.
""" This is what I want to work on now: 
Implement New Chatbot Functionality on Main Webpage #269

 Create Session-Based Chat Initiation - Implementation of a new chat session based on the user's session ID.
 Chat View Creation and Updates - Develop a view for chat and ensure it updates every second using HTMX.
 Telegram Integration - Link the chat function to the five predefined Telegram chatrooms, and implement a mechanism to inform the user if all rooms are occupied.
 Voice Message Functionality - Enable sending of voice messages as responses from Telegram to the chat.
 Chat Interaction Tracking - Build a system to track and record all chat interactions.
 Automated Response System - Implement an automated response system using embeddings to match and send previously used responses to repeated questions.
 Session Termination - Develop functionality to automatically remove chat on user's session end.
 New Chat Notification - Add a feature to notify the start of a new conversation in the chat.
 Automated Message Selection - Build a mechanism for reviewing and confirming old answers to be sent to users and to set certain responses for automatic use.
"""


# This is the view that is called when the user clicks on the chat button on the main page.
# This view resieves the request alongside the session_id
def chat(request, session_id):
    # check if the session_id is valid
    # if not return an error message
    if not session_id:
        return render(request, "error.html", {"error": "Session ID is not valid"})

    # check if request is done with htmx
    # if not return an error message
    if not request.htmx:
        return render(request, "error.html", {"error": "Request is not valid"})

    # a conversation is a chat between a user and a bot/agent.
    # Because on the other side of the chat can be a bot or an agent, we call it a conversation.
    # on the side of the agent there a multiple goup chats open that contain conversation after conversation.
    # every time a new conversation is started it is checked if there is a free group chat available.
    # if yes the conversation is added to the group chat and the user is informed that the conversation has started.
    # then the visitor can start chatting with the agent.
    # if all group chats are occupied the user is informed that all agents are currently busy
    # and that he has to wait but can already write his message and talk to a bot.
    # if the bot is not able to answer the question the user can choose to wait for an agent.

    # check if the session_id is currently in a conversation with a bot/agent
    # if yes send the user the chat with the current messages belonging to the session_id
    # if not create a new conversation
    # if currently all agents are busy inform the user that he has to wait
    # if the bot is not able to answer the question the user can choose to wait for an agent.
    # if the bot is able to answer the question the user can choose to wait for an agent as well.
    # if the user chooses to wait for an agent,
    # the bot will inform the user that he has to wait and that he can already write his message.
    # the user also has the option to leave a email address so that the agent can contact him later.
    # if the visitor chooses this option he will be asked to leave his email address and consent to the privacy policy.

    return render(request, "chat.html", {"session_id": session_id, "messages": []})
