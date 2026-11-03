from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio
import datetime

class ConnectionManager:
    """
    Manages active WebSocket connections and provides high-throughput
    event broadcasting across connected client dashboards.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new incoming WebSocket connection and registers it."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 Client connected. Total active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Removes a disconnected client from the active pool."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"❌ Client disconnected. Total active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Sends a JSON payload to a specific connected client."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            print(f"Error sending personal message: {e}")

    async def broadcast(self, event_type: str, payload: Dict[str, Any]):
        """
        Broadcasts an event message simultaneously to all connected WebSocket clients
        with an ISO timestamp and event classification.
        """
        if not self.active_connections:
            return

        message = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "event_type": event_type,
            "data": payload
        }
        
        serialized_data = json.dumps(message)
        
        # Concurrent dispatch to all active sockets
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(serialized_data)
            except Exception as e:
                print(f"Failed to send to client, marking for cleanup: {e}")
                disconnected.append(connection)

        # Clean up stale connections
        for dead_conn in disconnected:
            self.disconnect(dead_conn)

# Global singleton event broker instance
manager = ConnectionManager()