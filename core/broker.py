from fastapi import WebSocket
from typing import Dict, Set, Any, Optional
import json
import asyncio
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventMeshBroker")

class EnterpriseEventBroker:
    """
    Enterprise-grade WebSocket broker featuring room-based Pub/Sub routing,
    connection health tracking, and concurrent multi-client broadcasting.
    """
    def __init__(self):
        # Maps channel/room name to a set of connected WebSockets
        self.rooms: Dict[str, Set[WebSocket]] = {}
        # Maps WebSocket object to client metadata (ID, joined rooms, connection time)
        self.client_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, initial_room: str = "global"):
        """Accepts connection, registers client metadata, and joins default room."""
        await websocket.accept()
        
        if initial_room not in self.rooms:
            self.rooms[initial_room] = set()
        
        self.rooms[initial_room].add(websocket)
        self.client_metadata[websocket] = {
            "client_id": client_id,
            "rooms": {initial_room},
            "connected_at": datetime.datetime.utcnow().isoformat(),
            "messages_received": 0
        }
        logger.info(f"Client {client_id} connected and joined room: '{initial_room}'.")

    def disconnect(self, websocket: WebSocket):
        """Cleanly removes client from all rooms and purges metadata."""
        meta = self.client_metadata.pop(websocket, None)
        if meta:
            for room in meta.get("rooms", set()):
                if room in self.rooms and websocket in self.rooms[room]:
                    self.rooms[room].remove(websocket)
            logger.info(f"Client {meta.get('client_id')} disconnected.")

    async def join_room(self, websocket: WebSocket, room: str):
        """Moves or subscribes a client to a new channel room."""
        if room not in self.rooms:
            self.rooms[room] = set()
        self.rooms[room].add(websocket)
        if websocket in self.client_metadata:
            self.client_metadata[websocket]["rooms"].add(room)
        logger.info(f"Client subscribed to room: '{room}'")

    async def leave_room(self, websocket: WebSocket, room: str):
        """Unsubscribes a client from a specific channel room."""
        if room in self.rooms and websocket in self.rooms[room]:
            self.rooms[room].remove(websocket)
        if websocket in self.client_metadata:
            self.client_metadata[websocket]["rooms"].discard(room)

    async def broadcast_to_room(self, room: str, event_type: str, payload: Dict[str, Any]):
        """Broadcasts an event exclusively to all clients subscribed to a specific room."""
        if room not in self.rooms or not self.rooms[room]:
            return

        message = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "room": room,
            "event_type": event_type,
            "data": payload
        }
        serialized = json.dumps(message)

        stale_clients = []
        for client in list(self.rooms[room]):
            try:
                await client.send_text(serialized)
                if client in self.client_metadata:
                    self.client_metadata[client]["messages_received"] += 1
            except Exception as e:
                logger.warning(f"Failed to transmit to client: {e}")
                stale_clients.append(client)

        # Prune dead connections
        for dead in stale_clients:
            self.disconnect(dead)

    def get_cluster_stats(self) -> Dict[str, Any]:
        """Returns aggregate cluster telemetry for monitoring dashboards."""
        total_connections = len(self.client_metadata)
        room_breakdown = {room: len(clients) for room, clients in self.rooms.items()}
        return {
            "total_active_connections": total_connections,
            "active_rooms": room_breakdown,
            "uptime_utc": datetime.datetime.utcnow().isoformat()
        }

# Global singleton broker instance
broker = EnterpriseEventBroker()