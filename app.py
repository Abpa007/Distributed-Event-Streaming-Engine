import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page Configuration - Production dark mode layout
st.set_page_config(
    page_title="Enterprise Event Mesh | Global Control Center",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for dark-themed high-density metrics and terminal inspection
st.markdown("""
    <style>
    .metric-card {
        background-color: #111827;
        border: 1px solid #1f2937;
        padding: 14px 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .metric-title { font-size: 11px; color: #9ca3af; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; }
    .metric-value { font-size: 22px; font-weight: 700; color: #38bdf8; }
    .metric-sub { font-size: 11px; color: #6b7280; margin-top: 2px; }
    .console-box {
        background-color: #030712;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 12px;
        font-family: 'Courier New', Courier, monospace;
        font-size: 12px;
        color: #4ade80;
        height: 320px;
        overflow-y: auto;
    }
    .status-pill {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State
if "audit_logs" not in st.session_state:
    st.session_state.audit_logs = [
        {"timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3], "level": "SYSTEM", "message": "Global Cluster Controller initialized."}
    ]
if "total_dispatched" not in st.session_state:
    st.session_state.total_dispatched = 0

# Header Bar
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown("### ⚡ Enterprise Distributed Event Mesh — Control Center")
with h2:
    api_url = st.text_input("Gateway Endpoint", value="http://localhost:8000", label_visibility="collapsed")

st.divider()

# Fetch Backend Telemetry
start_time = time.time()
try:
    health_res = requests.get(f"{api_url}/health", timeout=1.5).json()
    latency_ms = round((time.time() - start_time) * 1000, 2)
    cluster = health_res.get("cluster", {})
    total_conns = cluster.get("total_active_connections", 0)
    rooms = cluster.get("active_rooms", {})
    status_text = "ONLINE (HEALTHY)"
    status_color = "#4ade80"
except Exception:
    latency_ms = 0.0
    total_conns = 0
    rooms = {}
    status_text = "DISCONNECTED"
    status_color = "#f87171"

# --- TOP ROW: 4 HIGH-DENSITY METRIC CARDS ---
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Gateway Health</div>
            <div class="metric-value" style="color: {status_color};">{status_text}</div>
            <div class="metric-sub">FastAPI / AsyncIO Core</div>
        </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Sockets</div>
            <div class="metric-value">{total_conns} Clients</div>
            <div class="metric-sub">Persistent TCP WS Connections</div>
        </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Room Partitions</div>
            <div class="metric-value">{len(rooms)} Channels</div>
            <div class="metric-sub">Pub/Sub Partition Isolation</div>
        </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Mesh Latency (HTTP ping)</div>
            <div class="metric-value" style="color: #c084fc;">{latency_ms} ms</div>
            <div class="metric-sub">Dispatched Events: {st.session_state.total_dispatched}</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# --- MAIN TWO-COLUMN WORKSPACE ---
col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.markdown("#### 📁 Active Channel Partitions & Listeners")
    
    if rooms:
        for room_name, client_count in rooms.items():
            st.info(f"🔑 **Room ID:** `{room_name}` &nbsp;|&nbsp; 📡 **Active Subscribed Listeners:** `{client_count}`")
    else:
        st.warning("No active room partitions. Run `python scripts/simulate_clients.py` to open persistent socket connections.")

    st.markdown("#### 🚀 Webhook Event Dispatcher")
    
    pub_room = st.selectbox("Target Channel Partition", ["telemetry", "financial-ticks", "security-alerts", "custom-room"], key="input_room")
    pub_event = st.text_input("Event Name", value="SYSTEM_LOAD_ALERT", key="input_event")
    pub_severity = st.selectbox("Severity Level", ["INFO", "SUCCESS", "WARNING", "CRITICAL"], key="input_severity")
    
    default_json = json.dumps({"node_id": "worker-01", "cpu_percent": 88.4, "memory_used_mb": 4096}, indent=2)
    pub_payload = st.text_area("Event Data (JSON Payload)", value=default_json, height=120, key="input_payload")
    
    if st.button("Publish Event to Mesh Engine", use_container_width=True):
        try:
            parsed_json = json.loads(pub_payload)
            payload_data = {
                "room": pub_room,
                "event_name": pub_event,
                "severity": pub_severity,
                "payload_data": parsed_json
            }
            res = requests.post(f"{api_url}/api/events/publish", json=payload_data)
            if res.status_code == 200:
                st.session_state.total_dispatched += 1
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                st.success(f"Dispatched '{pub_event}' to room://{pub_room}")
                st.session_state.audit_logs.insert(0, {
                    "timestamp": timestamp,
                    "level": pub_severity,
                    "message": f"Published '{pub_event}' to room://{pub_room} -> {json.dumps(parsed_json)}"
                })
            else:
                st.error(f"Failed: {res.text}")
        except json.JSONDecodeError:
            st.error("Invalid JSON string! Ensure keys and strings use valid double quotes.")
        except Exception as ex:
            st.error(f"Dispatch error: {ex}")

with col_right:
    st.markdown("#### 🖥️ Real-Time Cluster Telemetry Audit Log")
    
    # Formatted log entries
    log_lines = ""
    for log in st.session_state.audit_logs:
        log_lines += f"[{log['timestamp']}] [{log['level']}] {log['message']}\n"
        
    st.markdown(f'<div class="console-box"><pre>{log_lines}</pre></div>', unsafe_allow_html=True)
    
    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 Refresh Telemetry State", use_container_width=True):
            st.rerun()
    with c2:
        if st.button("🧹 Clear Terminal Logs", use_container_width=True):
            st.session_state.audit_logs = []
            st.rerun()
            
            
            
            