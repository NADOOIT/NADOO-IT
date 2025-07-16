# /scripts/test_p2p_signaling.py
import asyncio
import sys
import os

# Add the project root to the Python path to allow imports from the 'app' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nadooit_network.functions.p2p_api import (
    initialize_p2p_listener,
    connect_to_user,
    send_message_to_user,
    close_all_p2p_connections
)

async def main():
    # --- Define Event Handlers ---
    alice_ready = asyncio.Event()
    bob_ready = asyncio.Event()

    async def on_alice_ready():
        print("--> Alice's P2P listener is ready.")
        alice_ready.set()

    async def on_bob_ready():
        print("--> Bob's P2P listener is ready.")
        bob_ready.set()

    async def on_alice_channel_open(peer_id):
        print(f"--> Alice's data channel with {peer_id} is open. Sending message.")
        await send_message_to_user('Alice', peer_id, 'Hello from Alice!')

    async def on_bob_message(sender_id, message):
        print(f"--> Bob received message from {sender_id}: {message}")

    # --- Initialize Listeners Concurrently ---
    print("--- Initializing Listeners ---")
    alice_task = asyncio.create_task(initialize_p2p_listener(
        user_id='Alice',
        event_handlers={
            'on_connection_ready': on_alice_ready,
            'on_datachannel_open': on_alice_channel_open,
        }
    ))

    bob_task = asyncio.create_task(initialize_p2p_listener(
        user_id='Bob',
        event_handlers={
            'on_connection_ready': on_bob_ready,
            'on_message': on_bob_message
        }
    ))

    # Wait for both clients to be ready
    await asyncio.gather(alice_ready.wait(), bob_ready.wait())
    print("--- Both listeners are ready. ---")

    # --- Initiate P2P Connection ---
    print("--> Alice connecting to Bob...")
    await connect_to_user(user_id='Alice', peer_id='Bob')

    # Let the test run
    print("\n--- Running P2P API test for 15 seconds... ---")
    await asyncio.sleep(15)

    # Clean up tasks
    alice_task.cancel()
    bob_task.cancel()

    # --- Tearing down clients ---
    print("\n--- Tearing down P2P connections ---")
    await close_all_p2p_connections()

if __name__ == "__main__":
    asyncio.run(main())
