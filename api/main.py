from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import random
import datetime

from core.broker import manager

app = FastAPI(
    title="Real-Time Event-Driven Streaming Engine",
    description="High-throughput asynchronous event mesh and WebSocket telemetry broadcaster.",
    version="1.0.0"
)

# Enable CORS for external dashboard or client connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class EventPayload(BaseModel):
    event_name: str
    severity: str
    message: str

# Background task to simulate continuous real-time telemetry events
async def background_telemetry_simulator():
    """
    Simulates live system telemetry or stream events every 2 seconds
    and broadcasts them to all connected WebSocket clients.
    """
    event_categories = ["SYSTEM_METRIC", "USER_ACTIVITY", "SECURITY_ALERT", "TRANSACTION_TICK"]
    severities = ["INFO", "WARNING", "CRITICAL", "SUCCESS"]
    
    while True:
        await asyncio.sleep(2.5) # Emit every 2.5 seconds
        
        if len(manager.active_connections) > 0:
            category = random.choice(event_categories)
            simulated_data = {
                "metric_id": random.randint(1000, 9999),
                "category": category,
                "severity": random.choice(severities),
                "value": round(random.uniform(10.0, 99.9), 2),
                "node": f"worker-node-{random.randint(1, 4)}"
            }
            await manager.broadcast(event_type=category, payload=simulated_data)

@app.on_event("startup")
async def startup_event():
    """Starts the background telemetry simulator loop when the FastAPI server boots up."""
    asyncio.create_task(background_telemetry_simulator())

@app.get("/")
def root_probe():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Real-Time Event Mesh Engine",
        "active_websockets": len(manager.active_connections)
    }

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time client event subscriptions.
    Clients connect here to receive live broadcast streams instantly.
    """
    await manager.connect(websocket)
    try:
        # Keep the connection alive and listen for any client messages if needed
        while True:
            data = await websocket.receive_text()
            # Echo back confirmation or handle incoming client commands
            await manager.send_personal_message({"status": "ack", "received": data}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/trigger-event")
async def trigger_custom_event(payload: EventPayload):
    """
    REST endpoint to manually inject an event into the live stream mesh.
    Instantly broadcasts the custom event to all active WebSocket listeners.
    """
    event_data = {
        "event_name": payload.event_name,
        "message": payload.message,
        "source": "REST_API_TRIGGER"
    }
    await manager.broadcast(event_type=payload.severity, payload=event_data)
    return {
        "status": "success",
        "broadcasted_to_clients": len(manager.active_connections),
        "payload": event_data
    }