# /app/nadooit_network/classes/p2p_client.py
import asyncio
import websockets
import json
from typing import Optional, Dict
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCConfiguration, RTCIceServer, RTCDataChannel

class P2PClient:
    def __init__(self, user_id: str, signaling_server_url: str = "ws://localhost:8001", event_handlers: dict = None):
        self.user_id = user_id
        self.signaling_server_url = f"{signaling_server_url}/ws/{self.user_id}"
        self.event_handlers = event_handlers or {}

        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.listener_task: Optional[asyncio.Task] = None
        self.peer_connections: Dict[str, RTCPeerConnection] = {}
        self.data_channels: Dict[str, RTCDataChannel] = {}

    async def connect(self):
        """Establishes a connection to the signaling server and starts listening for messages."""
        try:
            self.websocket = await websockets.connect(self.signaling_server_url)
            self.listener_task = asyncio.create_task(self._listen())
            print(f"P2PClient for user '{self.user_id}' connected to signaling server.")
            on_ready = self.event_handlers.get("on_connection_ready")
            if on_ready:
                await on_ready()
        except Exception as e:
            print(f"Failed to connect to signaling server: {e}")
            on_error = self.event_handlers.get("on_error")
            if on_error:
                await on_error(e)

    async def _listen(self):
        """Listens for incoming messages from the signaling server."""
        try:
            while self.websocket and self.websocket.open:
                message_str = await self.websocket.recv()
                try:
                    data = json.loads(message_str)
                    peer_id = data.get('sender_id')
                    message_content = data.get('message')

                    if not peer_id:
                        continue

                    # For WebRTC signaling, the message content is a dict.
                    if isinstance(message_content, dict):
                        message_type = message_content.get('type')
                        if message_type == 'offer':
                            await self._handle_offer(peer_id, message_content)
                        elif message_type == 'answer':
                            await self._handle_answer(peer_id, message_content)
                        elif message_type == 'candidate':
                            await self._handle_candidate(peer_id, message_content)
                    # For simple text messages, it's a string.
                    else:
                        on_message = self.event_handlers.get("on_message")
                        if on_message:
                            await on_message(peer_id, message_content)

                except (json.JSONDecodeError, Exception):
                    # Silently ignore messages that cannot be parsed
                    pass

        except websockets.exceptions.ConnectionClosed:
            print("Connection to signaling server closed.")
        except Exception as e:
            print(f"An error occurred in the listener: {e}")
            on_error = self.event_handlers.get("on_error")
            if on_error:
                await on_error(e)

    async def _send_signal(self, recipient_id: str, message: dict):
        """Sends a signaling message to another user via the signaling server."""
        if self.websocket and self.websocket.open:
            payload = {
                "recipient_id": recipient_id,
                "message": message
            }
            await self.websocket.send(json.dumps(payload))
        else:
            print("Cannot send signal, WebSocket is not connected.")

    async def send_message(self, recipient_id: str, message_text: str):
        """Public method to send a simple text message."""
        # This will eventually be sent over a data channel
        await self._send_signal(recipient_id, {"type": "text", "content": message_text})

    async def connect_to_peer(self, peer_id: str):
        """Initiates a WebRTC connection to another peer."""
        if peer_id in self.peer_connections:
            print(f"Already connected or connecting to {peer_id}.")
            return

        print(f"Initiating connection to {peer_id}...")
        pc = self._create_peer_connection(peer_id)

        # Create a data channel for the initiating peer
        data_channel = pc.createDataChannel("chat")
        self.data_channels[peer_id] = data_channel

        @data_channel.on("open")
        async def on_open():
            print(f"Data channel with {peer_id} opened.")
            on_datachannel_open = self.event_handlers.get("on_datachannel_open")
            if on_datachannel_open:
                await on_datachannel_open(peer_id)

        @data_channel.on("message")
        def on_message(message):
            print(f"Initiator received message on data channel: {message}")

        # Create and send offer
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)

        await self._send_signal(
            peer_id,
            {
                "type": "offer",
                "sdp": pc.localDescription.sdp,
            },
        )
        print(f"Offer sent to {peer_id}")

    # --- WebRTC Connection Handlers ---
    async def _handle_offer(self, peer_id: str, offer: dict):
        print(f"Received offer from {peer_id}")
        pc = self._create_peer_connection(peer_id)

        await pc.setRemoteDescription(RTCSessionDescription(sdp=offer["sdp"], type="offer"))

        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        await self._send_signal(
            peer_id,
            {
                "type": "answer",
                "sdp": pc.localDescription.sdp,
            },
        )
        print(f"Answer sent to {peer_id}")

    async def _handle_answer(self, peer_id: str, answer: dict):
        print(f"Received answer from {peer_id}")
        pc = self.peer_connections.get(peer_id)
        if pc:
            await pc.setRemoteDescription(RTCSessionDescription(sdp=answer["sdp"], type="answer"))
            print(f"Answer from {peer_id} set.")

    async def _handle_candidate(self, peer_id: str, candidate: dict):
        print(f"Received ICE candidate from {peer_id}")
        pc = self.peer_connections.get(peer_id)
        if pc and candidate and candidate.get('candidate'):
            from aiortc.sdp import candidate_from_sdp
            # Reconstruct the RTCIceCandidate object from the received dictionary
            ice_candidate = candidate_from_sdp(candidate['candidate'])
            ice_candidate.sdpMid = candidate['sdpMid']
            ice_candidate.sdpMLineIndex = candidate['sdpMLineIndex']
            await pc.addIceCandidate(ice_candidate)
            print(f"ICE candidate from {peer_id} added.")

    def _create_peer_connection(self, peer_id: str) -> RTCPeerConnection:
        """Creates and configures a new RTCPeerConnection object."""
        config = RTCConfiguration(iceServers=[
            RTCIceServer(urls=["stun:nadooit.de:3478"])
        ])
        pc = RTCPeerConnection(configuration=config)
        self.peer_connections[peer_id] = pc

        @pc.on("icecandidate")
        async def on_icecandidate(candidate):
            if candidate:
                await self._send_signal(peer_id, {
                    "type": "candidate",
                    "candidate": {
                        "candidate": candidate.candidate,
                        "sdpMid": candidate.sdpMid,
                        "sdpMLineIndex": candidate.sdpMLineIndex,
                    }
                })

        @pc.on("datachannel")
        def on_datachannel(channel):
            self.data_channels[peer_id] = channel
            print(f"Data channel '{channel.label}' created by remote.")

            @channel.on("open")
            async def on_open():
                print(f"Data channel with {peer_id} opened.")
                on_datachannel_open = self.event_handlers.get("on_datachannel_open")
                if on_datachannel_open:
                    await on_datachannel_open(peer_id)

            @channel.on("message")
            def on_message(message):
                on_message_handler = self.event_handlers.get("on_message")
                if on_message_handler:
                    # P2P messages don't have a sender_id in the payload
                    # The sender is the peer_id of the connection
                    asyncio.create_task(on_message_handler(peer_id, message))
        
        return pc

    async def send_p2p_message(self, peer_id: str, message: str):
        """Sends a message to a peer over an established data channel."""
        if peer_id in self.data_channels:
            channel = self.data_channels[peer_id]
            if channel.readyState == "open":
                channel.send(message)
                print(f"Sent P2P message to {peer_id}: {message}")
            else:
                print(f"Cannot send message: data channel with {peer_id} is not open.")
        else:
            print(f"Cannot send message: no data channel found for {peer_id}.")

    async def close(self):
        """Closes all peer connections, the WebSocket connection, and stops the listener task."""
        # Close all RTCPeerConnection objects
        for pc in self.peer_connections.values():
            await pc.close()
        self.peer_connections.clear()
        self.data_channels.clear()

        # Close WebSocket connection
        if self.listener_task:
            self.listener_task.cancel()
        if self.websocket:
            await self.websocket.close()
        print(f"P2PClient for user '{self.user_id}' has been closed.")
