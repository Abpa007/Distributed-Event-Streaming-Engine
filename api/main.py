from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import random
import uuid

from core.broker import broker

app = FastAPI(
    title="Enterprise Distributed Event Mesh API",
    description="High-throughput WebSocket messaging broker with room-based pub/sub routing.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CustomEvent(BaseModel):
    room: str
    event_name: str
    severity: str  # INFO, WARNING, CRITICAL, SUCCESS
    payload_data: dict

# Background task simulating multi-channel enterprise telemetry
async def enterprise_telemetry_generator():
    rooms = ["telemetry", "financial-ticks", "security-alerts"]
    severities = ["INFO", "WARNING", "SUCCESS", "CRITICAL"]
    
    while True:
        await asyncio.sleep(2.0)
        if broker.client_metadata:
            target_room = random.choice(rooms)
            event_type = f"SYS_{target_room.upper()}_TICK"
            
            payload = {
                "transaction_id": str(uuid.uuid4())[:8],
                "metric_value": round(random.uniform(50.0, 500.0), 2),
                "node_id": f"edge-worker-{random.randint(1, 6)}",
                "status": "nominal" if target_room != "security-alerts" else "flagged"
            }
            await broker.broadcast_to_room(target_room, event_type, payload)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(enterprise_telemetry_generator())

@app.get("/health")
def cluster_health():
    """Returns cluster state, active room distributions, and connection counts."""
    return {
        "status": "healthy",
        "cluster": broker.get_cluster_stats()
    }

@app.websocket("/ws/stream")
async def websocket_gateway(websocket: WebSocket, client_id: str = Query(..., description="Unique client session identifier"), room: str = Query("telemetry", description="Initial room to subscribe")):
    """
    Enterprise WebSocket Endpoint with room partitioning and heartbeat management.
    """
    await broker.connect(websocket, client_id, initial_room=room)
    try:
        while True:
            raw_data = await websocket.receive_text()
            # Handle client commands (e.g., room switching or heartbeats)
            try:
                data = json.loads(raw_data)
                action = data.get("action")
                target_room = data.get("room")
                
                if action == "JOIN" and target_room:
                    await broker.join_room(websocket, target_room)
                    await websocket.send_text(json.dumps({"status": "success", "message": f"Joined room {target_room}"}))
                elif action == "LEAVE" and target_room:
                    await broker.leave_room(websocket, target_room)
                    await websocket.send_text(json.dumps({"status": "success", "message": f"Left room {target_room}"}))
                elif action == "PING":
                    await websocket.send_text(json.dumps({"status": "PONG", "timestamp": data.get("timestamp")}))
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        broker.disconnect(websocket)

@app.post("/api/events/publish")
async def publish_event(event: CustomEvent):
    """
    REST webhook to inject custom events directly into a specific room mesh.
    """
    await broker.broadcast_to_room(event.room, event.event_name, event.payload_data)
    return {
        "status": "dispatched",
        "target_room": event.room,
        "active_listeners": len(broker.rooms.get(event.room, set()))
    }