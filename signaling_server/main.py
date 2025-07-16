# /signaling_server/main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        print(f"User '{user_id}' connected.")

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            print(f"User '{user_id}' disconnected.")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_user(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
        else:
            print(f"Error: User '{user_id}' not found.")

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_json()
            recipient_id = data.get('recipient_id')
            message_payload = data.get('message')

            if recipient_id and message_payload:
                # Forward the message to the recipient
                # The message includes the original sender's ID
                full_message = {
                    'sender_id': user_id,
                    'message': message_payload
                }
                await manager.send_to_user(json.dumps(full_message), recipient_id)
            else:
                print(f"Invalid message format from {user_id}: {data}")

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"An error occurred for user {user_id}: {e}")
        manager.disconnect(user_id)
