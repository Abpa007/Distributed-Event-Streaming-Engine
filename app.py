import streamlit as st
import requests
import json
import time

# Page Configuration - Dark Enterprise Theme
st.set_page_config(
    page_title="Enterprise Event Mesh Control Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Enterprise Dark Styling
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #c9d1d9; }
    .metric-box {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 20px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-box h2 { color: #58a6ff; margin: 0; font-size: 28px; }
    .metric-box p { color: #8b949e; margin: 5px 0 0 0; font-size: 14px; }
    .terminal-box {
        background-color: #0d1117;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 15px;
        font-family: 'Courier New', Courier, monospace;
        color: #3fb950;
        height: 300px;
        overflow-y: scroll;
    }
    </style>
""", unsafe_allow_html=True)

# Header Section
st.title("⚡ Enterprise Event Mesh | Live Telemetry Gateway")
st.markdown("Distributed WebSocket Pub/Sub Routing & Real-Time Event Broker Monitor")

# Sidebar Controls
st.sidebar.header("🎛️ Gateway Control")
api_url = st.sidebar.text_input("FastAPI Backend URL", value="http://localhost:8000")

st.sidebar.divider()
st.sidebar.subheader("📡 Inject Custom Event")
with st.sidebar.form("inject_form"):
    target_room = st.selectbox("Channel Room", ["telemetry", "financial-ticks", "security-alerts"])
    event_name = st.text_input("Event Code", value="PAYMENT_PROCESSED")
    severity = st.selectbox("Severity", ["INFO", "SUCCESS", "WARNING", "CRITICAL"])
    payload_msg = st.text_input("Payload Message", value='{"user_id": 4092, "amount": 299.99}')
    
    submit_btn = st.form_submit_button("Broadcast to Mesh")
    if submit_btn:
        try:
            payload = {
                "room": target_room,
                "event_name": event_name,
                "severity": severity,
                "payload_data": json.loads(payload_msg)
            }
            res = requests.post(f"{api_url}/api/events/publish", json=payload)
            if res.status_code == 200:
                st.sidebar.success("Event broadcasted successfully!")
            else:
                st.sidebar.error(f"Error: {res.text}")
        except Exception as e:
            st.sidebar.error(f"Failed to connect: {e}")

# Fetch Cluster Health & Metrics
try:
    health = requests.get(f"{api_url}/health", timeout=2).json()
    cluster = health.get("cluster", {})
    total_conns = cluster.get("total_active_connections", 0)
    rooms = cluster.get("active_rooms", {})
    status_text = "HEALTHY"
except Exception:
    total_conns = 0
    rooms = {}
    status_text = "OFFLINE"

# Metrics Grid
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f'<div class="metric-box"><h2>{status_text}</h2><p>Cluster Status</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-box"><h2>{total_conns}</h2><p>Active Sockets</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-box"><h2>{len(rooms)}</h2><p>Active Pub/Sub Rooms</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-box"><h2>AsyncIO</h2><p>Event Mesh Core</p></div>', unsafe_allow_html=True)

st.divider()

# Main Dashboard View
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🏢 Active Room Partitions")
    if rooms:
        for room_name, client_count in rooms.items():
            st.info(f"📁 Room Channel: **`{room_name}`** — **{client_count}** active listener(s)")
    else:
        st.warning("No active channels. Run the simulation script or connect via WebSockets.")

    st.subheader("💡 How to Defend This in an Interview")
    st.markdown("""
    - **Concurrency:** Uses Python `asyncio` event loops instead of blocking threads, handling thousands of concurrent connections.
    - **Pub/Sub Routing:** Clients partition themselves into isolated rooms (`telemetry`, `financial-ticks`, `security-alerts`), avoiding broadcast noise.
    - **Fault Tolerance:** Built-in automatic zombie connection pruning detects dropped sockets and purges them from memory.
    """)

with col_right:
    st.subheader("💻 Cluster Log Stream")
    st.markdown("Live simulated event output from background worker nodes:")
    
    # Simulated live terminal log view
    log_output = f"""[INFO] {time.strftime('%Y-%m-%d %H:%M:%S')} - Broker initialized successfully.
[INFO] Background telemetry worker active on 3 channels.
[INFO] Current cluster active sockets: {total_conns}
[DEBUG] Routing table updated: {json.dumps(rooms)}
[STREAM] Emitting tick packet -> room: telemetry [OK]
[STREAM] Emitting tick packet -> room: financial-ticks [OK]"""
    
    st.markdown(f'<div class="terminal-box"><pre>{log_output}</pre></div>', unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Telemetry State"):
        st.rerun()