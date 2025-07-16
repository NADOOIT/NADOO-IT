# /app/nadooit_network/functions/p2p_api.py
import asyncio
from typing import Optional
from ..classes.p2p_client import P2PClient

# Manages all active P2P client instances, keyed by user_id.
_active_clients: dict[str, P2PClient] = {}

async def initialize_p2p_listener(user_id: str, event_handlers: dict = None):
    """
    Initializes a P2P client for a given user, connects to the signaling server,
    and starts listening for events.
    """
    if user_id in _active_clients:
        print(f"P2P client for {user_id} is already initialized.")
        return

    client = P2PClient(user_id=user_id, event_handlers=event_handlers or {})
    _active_clients[user_id] = client
    await client.connect()

async def connect_to_user(user_id: str, peer_id: str):
    """
    Initiates a P2P connection from a user to a peer.
    """
    if user_id in _active_clients:
        client = _active_clients[user_id]
        await client.connect_to_peer(peer_id)
    else:
        print(f"Error: P2P client for {user_id} not initialized.")

async def send_message_to_user(user_id: str, recipient_id: str, message: str):
    """
    Sends a text message from a user to a recipient over an established P2P connection.
    """
    if user_id in _active_clients:
        client = _active_clients[user_id]
        await client.send_p2p_message(recipient_id, message)
    else:
        print(f"Error: P2P client for {user_id} not initialized.")

async def close_p2p_connection(user_id: str):
    """
    Closes the P2P connection for a specific user.
    """
    if user_id in _active_clients:
        client = _active_clients.pop(user_id)
        await client.close()
    else:
        print(f"P2P client for {user_id} is not currently running.")

async def close_all_p2p_connections():
    """
    Closes all active P2P connections.
    """
    for user_id in list(_active_clients.keys()):
        await close_p2p_connection(user_id)
