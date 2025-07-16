# /signaling_server/main.py
import json
import os
from typing import Dict

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

# --- Authentication Helper ---
async def authenticate_user(user_code: str, api_key: str) -> bool:
    """Authenticates a user against the NADOO-IT authentication service."""
    auth_service_url = os.environ.get("NADOO_AUTH_URL", "http://localhost:8000")
    auth_endpoint = f"{auth_service_url}/api/users/check"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                auth_endpoint,
                headers={"NADOOIT-API-KEY": api_key},
                json={
                    "NADOOIT__USER_CODE": user_code,
                    "NADOOIT__USER_CODE_TO_CHECK": user_code,
                },
                timeout=10.0,
            )
        return response.status_code == 200
    except httpx.RequestError as e:
        print(f"Error connecting to auth service: {e}")
        return False

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    def add_authenticated_user(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id] = websocket
        print(f"User '{user_id}' authenticated and connection is active.")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User '{user_id}' disconnected.")

    async def send_to_user(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
        else:
            print(f"Error: User '{user_id}' not found or not authenticated.")

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    user_id = None
    try:
        # --- Authentication Step ---
        auth_data = await websocket.receive_json()
        auth_type = auth_data.get("type")
        
        if auth_type == "auth":
            user_code = auth_data.get("user_code")
            api_key = auth_data.get("api_key")

            if user_code and api_key and await authenticate_user(user_code, api_key):
                user_id = user_code
                manager.add_authenticated_user(user_id, websocket)
                await websocket.send_json({"type": "auth_success"})
            else:
                await websocket.send_json({"type": "auth_failure", "message": "Invalid credentials"})
                await websocket.close()
                return
        else:
            await websocket.send_json({"type": "auth_failure", "message": "Authentication required"})
            await websocket.close()
            return

        # --- Message Handling Loop (only runs after successful auth) ---
        while True:
            data = await websocket.receive_json()
            recipient_id = data.get('recipient_id')
            message_payload = data.get('message')

            if recipient_id and message_payload:
                full_message = {
                    'sender_id': user_id,
                    'message': message_payload
                }
                await manager.send_to_user(json.dumps(full_message), recipient_id)
            else:
                print(f"Invalid message format from {user_id}: {data}")

    except WebSocketDisconnect:
        if user_id:
            manager.disconnect(user_id)
    except Exception as e:
        print(f"An error occurred for user {user_id or 'unauthenticated'}: {e}")
        if user_id:
            manager.disconnect(user_id)
