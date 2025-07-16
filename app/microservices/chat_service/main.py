# chat_service/main.py
import sys
import os
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel

# --- Step 1: Add Project to Python Path ---
# This is a crucial step for making our microservice architecture work.
# It adds the root of the NADOO-IT project to Python's path, allowing us to
# import shared modules like 'nadooit_common' from sibling directories.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_root)

# --- Step 2: Import the Security Dependency ---
# Here, we import our reusable authentication function. This function will be
# 'injected' into our endpoints. FastAPI's dependency injection system will run
# this function for every request to a protected endpoint.
from nadooit_common.security import get_current_active_user

# --- Step 3: Define Data Models with Pydantic ---
# Pydantic models define the shape and data types of your API's inputs
# and outputs. FastAPI uses them to automatically validate incoming request
# data and to serialize outgoing responses. It also uses them to generate
# the interactive API documentation (e.g., at /docs).
class Message(BaseModel):
    recipient_user_code: str
    message_content: str

# --- Step 4: Create the FastAPI Application ---
app = FastAPI(
    title="Chat Service",
    description="A microservice for sending messages between users.",
    version="1.0.0",
)

# --- Step 5: Define API Endpoints ---

# This is the root endpoint. It's protected by our security dependency.
@app.get("/")
def read_root(current_user: dict = Depends(get_current_active_user)):
    """
    A simple welcome endpoint to verify that the service is running and
    the user is authenticated.
    """
    # The `current_user` dictionary is the value returned by `get_current_active_user`.
    # If the dependency fails (e.g., bad API key), the code here will never run.
    # FastAPI will instead return a 403 Forbidden error automatically.
    return {"message": f"Welcome to the Chat Service, authenticated user: {current_user['user_code']}"}

@app.post("/send")
def send_message(message: Message, current_user: dict = Depends(get_current_active_user)):
    """
    Sends a message to another user.

    The user sending the message is identified by the authentication credentials
    in the request headers.
    """
    sender_user_code = current_user['user_code']

    # In a real application, this is where you would add the logic to handle
    # the message. For example:
    # 1. Check if the recipient_user_code exists and is valid.
    # 2. Save the message to a database (e.g., PostgreSQL, MongoDB).
    # 3. Send a real-time notification via WebSockets.
    # 4. Queue a task to send an email or push notification.

    print(f"Message from '{sender_user_code}' to '{message.recipient_user_code}': {message.message_content}")

    return {
        "status": "Message sent successfully",
        "from": sender_user_code,
        "to": message.recipient_user_code,
        "message": message.message_content,
    }
