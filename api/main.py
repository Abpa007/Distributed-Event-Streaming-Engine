from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import asyncio
import logging

from core.broker import broker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EventMeshAPI")

app = FastAPI(
    title="Enterprise Distributed Event Mesh",
    version="1.0.0",
    description="Low-latency asynchronous WebSocket pub/sub routing engine."
)

# Enable CORS for external client applications
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EventPayload(BaseModel):
    room: str
    event_name: str
    severity: str = "INFO"
    payload_data: Dict[str, Any]

@app.on_event("startup")
async def startup_event():
    """Starts the background worker that simulates live enterprise event generation."""
    asyncio.create_task(enterprise_telemetry_generator())
    logger.info("Background enterprise telemetry generator started.")

async def enterprise_telemetry_generator():
    """Background task that pumps live ticks into rooms every 3 seconds."""
    while True:
        await asyncio.sleep(3)
        # Broadcast a simulated telemetry tick
        await broker.broadcast_to_room(
            room="telemetry",
            event_type="NODE_HEALTH_TICK",
            payload={"status": "healthy", "cpu_load": 24.5, "active_nodes": 4}
        )
        # Broadcast a simulated financial tick
        await broker.broadcast_to_room(
            room="financial-ticks",
            event_type="STOCK_PRICE_TICK",
            payload={"symbol": "AAPL", "price": 185.92, "trend": "bullish"}
        )

@app.get("/health")
async def cluster_health():
    """Returns cluster health and active WebSocket connection statistics."""
    return {
        "status": "ONLINE",
        "cluster": broker.get_cluster_stats()
    }

@app.post("/api/events/publish")
async def publish_event(event: EventPayload):
    """REST Webhook endpoint allowing external services to inject events into the mesh."""
    try:
        await broker.broadcast_to_room(
            room=event.room,
            event_type=event.event_name,
            payload={
                "severity": event.severity,
                "data": event.payload_data
            }
        )
        return {"status": "success", "message": f"Event published to room '{event.room}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/stream")
async def websocket_gateway(websocket: WebSocket, client_id: str = "anonymous", room: str = "telemetry"):
    """
    Primary WebSocket gateway endpoint. 
    External clients connect here to maintain a persistent live data stream.
    URL Example: ws://localhost:8000/ws/stream?client_id=trader_01&room=financial-ticks
    """
    await broker.connect(websocket, client_id=client_id, initial_room=room)
    try:
        while True:
            # Keep connection alive and listen for client commands (like room switching or pings)
            data = await websocket.receive_text()
            try:
                message = json.loads(data) if data else {}
                if message.get("action") == "JOIN_ROOM":
                    target_room = message.get("room")
                    if target_room:
                        await broker.join_room(websocket, target_room)
                        await websocket.send_text(f'{{"status": "joined", "room": "{target_room}"}}')
            except Exception:
                pass
    except WebSocketDisconnect:
        broker.disconnect(websocket)
        logger.info(f"Client {client_id} disconnected from gateway.")