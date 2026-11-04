# ⚡Distributed-Event-Streaming-Engine

A low-latency, asynchronous **Distributed-Event-Streaming-Engine** built with FastAPI and Python `asyncio`. Designed for real-time pub/sub routing, channel partition isolation, and persistent WebSocket connection management at enterprise scale.

---

## 🏗️ System Architecture & Design

Traditional HTTP polling wastes bandwidth and introduces high latency. This engine maintains **persistent, non-blocking TCP WebSocket connections** and routes payloads instantly across isolated channel partitions ("Rooms").

```text
  [ External Webhook / API ] 
            │ (HTTP POST)
            ▼
  ┌───────────────────────────────────┐
  |      FastAPI Gateway Server       |
  |    (api/main.py & core/broker.py) |
  └─────────┬───────────────┬─────────┘
            │               │
  (Broadcast)               (Broadcast)
            ▼               ▼
   Room: #telemetry    Room: #financial-ticks
   ┌─────────────┐    ┌─────────────┐
   │ Client (WS) │    │ Client (WS) │
   └─────────────┘    └─────────────┘
```

---

## 🛠️ Key Technical Features

- **Asynchronous Pub/Sub Core (`core/broker.py`)**: Built entirely on non-blocking `asyncio` primitives to handle concurrent client data streams without thread-locking bottlenecks.
- **Room-Partition Isolation**: Dynamic dictionary mapping (`room -> set of client sockets`) ensuring event isolation so clients only receive data from channels they subscribe to.
- **Zombie Socket & Memory Pruning**: Automatic exception handlers intercept broken/dropped socket connections, purging them instantly from memory and deleting empty rooms to prevent RAM bloat.
- **Dual-Interface Gateway**: 
  - **REST Webhook (`/api/events/publish`)**: Allows external services to inject live events into the mesh.
  - **WebSocket Gateway (`/ws/stream`)**: Maintains persistent subscriber pipelines.
- **Operations Console (`app.py`)**: A production-grade Streamlit dashboard tracking real-time gateway health, active socket counts, latency pings, and cluster audit logs.

---

## 📂 Project Structure

```tree
realtime-event-mesh/
├── api/
│   └── main.py              # FastAPI application, REST webhooks, & WS gateway endpoints
├── core/
│   └── broker.py            # Custom EnterpriseEventBroker handling pub/sub & room routing
├── scripts/
│   └── simulate_clients.py  # Concurrency simulation script for load testing
├── app.py                   # Streamlit Operations & Telemetry Control Center
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## 🚀 Getting Started & Installation

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/your-username/realtime-event-mesh.git
cd realtime-event-mesh
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn websockets streamlit requests httpx pydantic
```

---

## 🕹️ Running the System

You will need **three separate terminal windows** to run the complete event mesh ecosystem:

### Terminal 1: Start the FastAPI Backend Gateway
```bash
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```
*(Runs the WebSocket and REST endpoints at `http://localhost:8000`)*

### Terminal 2: Start the Concurrency Simulator (Clients)
```bash
python scripts/simulate_clients.py
```
*(Spawns persistent virtual clients connecting to the backend channels)*

### Terminal 3: Launch the Operations Control Center
```bash
streamlit run app.py
```
*(Opens the live telemetry dashboard in your browser)*

---


By - Abhay Panchal

Email - abhaypanchal095@gmail.com
