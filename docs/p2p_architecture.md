# NADOO-IT P2P Communication Architecture

This document provides a detailed overview of the peer-to-peer (P2P) communication infrastructure integrated into the NADOO-IT platform. This system enables direct, secure, and low-latency communication between clients, forming the foundation for a new class of real-time, interactive features.

## 1. System Overview

The P2P architecture is designed to facilitate direct communication channels between users, bypassing the central server for data exchange after an initial handshake. This is achieved using WebRTC technology, orchestrated by a custom signaling server and supported by a STUN/TURN server for NAT traversal.

### Key Components:

1.  **Signaling Server:** A lightweight, standalone server built with FastAPI and WebSockets. Its sole responsibility is to relay metadata (offers, answers, and ICE candidates) between clients to help them establish a direct connection. It does not handle any user data beyond this initial handshake.

2.  **STUN/TURN Server:** A Coturn server (`stun:nadooit.de:3478`) is deployed to help clients discover their public IP addresses and navigate through network address translators (NATs) and firewalls. This is crucial for establishing P2P connections in real-world network environments.

3.  **P2P Client Library (`aiortc`):** The core of the client-side implementation. This library, built on top of `aiortc`, manages the entire WebRTC lifecycle. It handles the creation of peer connections, manages the signaling state machine, and provides an interface for sending and receiving data over secure data channels.

4.  **High-Level Public API:** To make this powerful technology accessible to developers, a simple, high-level API is provided. This API abstracts away the complexities of WebRTC, allowing developers to integrate P2P functionality with just a few function calls.

## 2. How It Works: The Connection Flow

1.  **Initialization:** Two clients, Alice and Bob, each initialize a P2P listener using `initialize_p2p_listener(user_id, event_handlers)`. This connects them to the signaling server via a WebSocket.

2.  **Connection Initiation:** Alice decides to connect to Bob and calls `connect_to_user('Alice', 'Bob')`.

3.  **Offer Generation:** Alice's client generates a WebRTC "offer" (a session description) and sends it to the signaling server, addressed to Bob.

4.  **Signaling:** The signaling server receives the offer and relays it to Bob's client.

5.  **Answer Generation:** Bob's client receives the offer, generates an "answer," and sends it back to Alice via the signaling server.

6.  **ICE Candidate Exchange:** Concurrently, both clients gather network path information (ICE candidates) with the help of the STUN server and exchange them through the signaling server. This allows them to find the best path for a direct connection.

7.  **P2P Connection Established:** Once the offer/answer exchange is complete and a suitable network path is found, a direct, encrypted P2P connection is established between Alice and Bob.

8.  **Direct Communication:** Alice can now call `send_message_to_user('Alice', 'Bob', 'Hello!')`. The message is sent directly to Bob over the secure WebRTC data channel, with minimal latency.

## 3. Using the P2P API

The API is designed to be simple and event-driven.

### Core Functions:

-   `initialize_p2p_listener(user_id: str, event_handlers: dict)`: Initializes the client for a specific user and connects to the signaling server. It takes a dictionary of event handlers.
-   `connect_to_user(user_id: str, peer_id: str)`: Initiates a P2P connection from `user_id` to `peer_id`.
-   `send_message_to_user(user_id: str, recipient_id: str, message: str)`: Sends a message from `user_id` to `recipient_id` over an established data channel.
-   `close_all_p2p_connections()`: Closes all active connections.

### Event Handlers:

You can provide `async` functions to handle various events:

-   `on_connection_ready`: Fired when the client is successfully connected to the signaling server.
-   `on_datachannel_open(peer_id: str)`: Fired when a direct data channel to a peer is successfully opened and ready for messaging.
-   `on_message(sender_id: str, message: str)`: Fired when a message is received from a peer over a data channel.

### Example Usage (in NADOO Launchpad):

```python
import asyncio
from nadooit_network.functions import p2p_api

async def main():
    # Define event handlers
    async def on_ready():
        print("Listener is ready! Waiting for connections.")

    async def on_channel_open(peer_id):
        print(f"Data channel with {peer_id} is open!")
        # Send a welcome message
        await p2p_api.send_message_to_user('my_user_id', peer_id, 'Hi there!')

    async def on_incoming_message(sender_id, message):
        print(f"Received message from {sender_id}: {message}")

    # Initialize the listener
    await p2p_api.initialize_p2p_listener(
        user_id='my_user_id',
        event_handlers={
            'on_connection_ready': on_ready,
            'on_datachannel_open': on_channel_open,
            'on_message': on_incoming_message
        }
    )

    # In a real application, you would wait for another user
    # to connect to you, or initiate a connection yourself.
    # For example:
    # await p2p_api.connect_to_user('my_user_id', 'another_user_id')

    # Keep the listener running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```
