import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(
    page_title="Enterprise Event Mesh Command Center",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Enterprise Distributed Event Mesh")
st.markdown("Real-Time Asynchronous WebSocket Telemetry & Pub/Sub Routing Engine")

api_url = st.sidebar.text_input("API Gateway URL", value="http://localhost:8000")

# Fetch cluster health
try:
    health_res = requests.get(f"{api_url}/health", timeout=2).json()
    cluster_stats = health_res.get("cluster", {})
    total_conns = cluster_stats.get("total_active_connections", 0)
    active_rooms = cluster_stats.get("active_rooms", {})
except Exception:
    total_conns = 0
    active_rooms = {}

# Top Metrics Row
col1, col2, col3 = st.columns(3)
col1.metric("Total Active WebSocket Sockets", total_conns)
col2.metric("Active Pub/Sub Rooms", len(active_rooms))
col3.metric("Broker Status", "🟢 ONLINE" if total_conns >= 0 else "🔴 OFFLINE")

st.divider()

# Tabs for Organization
tab1, tab2, tab3 = st.tabs(["📡 Live Event Stream & Inspector", "🚀 Event Publisher", "📊 Architecture Overview"])

with tab1:
    st.subheader("Active Room Channels")
    if active_rooms:
        for room_name, count in active_rooms.items():
            st.info(f"Room Channel: **{room_name}** | Connected Listeners: **{count}**")
    else:
        st.warning("No active room connections detected. Start client scripts or connect via WebSockets.")

with tab2:
    st.subheader("Inject Custom Event into Mesh")
    with st.form("publish_form"):
        room = st.selectbox("Target Room Channel", ["telemetry", "financial-ticks", "security-alerts"])
        event_name = st.text_input("Event Name", value="CUSTOM_AUDIT_LOG")
        severity = st.selectbox("Severity Level", ["INFO", "WARNING", "CRITICAL", "SUCCESS"])
        message = st.text_area("JSON Payload Data (Key-Value)", value='{"user": "admin", "action": "override"}')
        
        submitted = st.form_submit_button("Broadcast to Mesh")
        if submitted:
            try:
                parsed_data = json.loads(message)
                payload = {
                    "room": room,
                    "event_name": event_name,
                    "severity": severity,
                    "payload_data": parsed_data
                }
                res = requests.post(f"{api_url}/api/events/publish", json=payload)
                if res.status_code == 200:
                    st.success(f"Successfully broadcasted to {res.json().get('active_listeners', 0)} listeners in room '{room}'!")
                else:
                    st.error(res.text)
            except json.JSONDecodeError:
                st.error("Invalid JSON format in payload data.")

with tab3:
    st.subheader("System Architecture & Design Patterns")
    st.markdown("""
    - **Asynchronous Event Loop (`asyncio`)**: Non-blocking I/O handling thousands of concurrent socket reads/writes.
    - **Room-Based Partitioning**: Dynamic subscription routing separating data streams by channels (`telemetry`, `financial-ticks`, `security-alerts`).
    - **Heartbeat & Zombie Pruning**: Automatic detection and cleanup of dropped socket connections to prevent memory leakage.
    - **Zero-Dependency Core**: Built on pure FastAPI and WebSockets without heavy external broker overhead for maximum execution speed.
    """)