import streamlit as st
import requests
import json
import time
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="Real-Time Event Mesh & WebSocket Stream",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e2f;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        border: 1px solid #2d2d44;
    }
    .stAlert {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Real-Time Event-Driven Streaming Engine")
st.markdown("High-throughput asynchronous WebSocket event mesh and telemetry broadcast control center.")

# Sidebar Configuration & Controls
st.sidebar.header("🎛️ Control Panel")
api_url = st.sidebar.text_input("FastAPI Gateway URL", value="http://localhost:8000")

st.sidebar.divider()
st.sidebar.subheader("🚀 Trigger Custom Event")
event_name = st.sidebar.text_input("Event Name", value="USER_CHECKOUT")
severity = st.sidebar.selectbox("Severity / Channel", ["INFO", "SUCCESS", "WARNING", "CRITICAL"])
message = st.sidebar.text_area("Event Payload Message", value="User ID #8841 completed checkout for $149.99")

if st.sidebar.button("Broadcast Event to Mesh", type="primary"):
    try:
        payload = {
            "event_name": event_name,
            "severity": severity,
            "message": message
        }
        response = requests.post(f"{api_url}/trigger-event", json=payload)
        if response.status_code == 200:
            res_data = response.json()
            st.sidebar.success(f"Broadcasted to {res_data['broadcasted_to_clients']} active clients!")
        else:
            st.sidebar.error(f"Failed to trigger: {response.text}")
    except Exception as e:
        st.sidebar.error(f"Connection error: {e}")

# Main Dashboard Layout
col1, col2, col3 = st.columns(3)

# Health Check Query
try:
    health_res = requests.get(f"{api_url}/", timeout=2).json()
    status = health_res.get("status", "offline")
    active_connections = health_res.get("active_websockets", 0)
except Exception:
    status = "offline (Start FastAPI server)"
    active_connections = 0

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <h3>System Status</h3>
            <h2>{'🟢 ONLINE' if 'online' in status else '🔴 OFFLINE'}</h2>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Active WebSocket Connections</h3>
            <h2>{active_connections}</h2>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <h3>Engine Architecture</h3>
            <h2>Async FastAPI / WS</h2>
        </div>
    """, unsafe_allow_html=True)

st.divider()

st.subheader("📡 Live Telemetry Event Stream Feed")
st.markdown("To view live simulated background events streaming through WebSockets, run your FastAPI server in a separate terminal and watch the live ticker below, or check your console logs.")

# Instructions box for running the project
st.info("""
**How to run your backend server:**
1. Open a second PowerShell terminal in your project directory.
2. Activate your virtual environment: `venv\\Scripts\\activate`
3. Run the FastAPI server with Uvicorn: `uvicorn api.main:app --reload`
4. Keep this Streamlit dashboard open to monitor live broadcasts!
""")

# Session state simulation feed for demo presentation if server is running
if "event_history" not in st.session_state:
    st.session_state.event_history = []

# Refresh button
if st.button("🔄 Refresh System Metrics"):
    st.rerun()