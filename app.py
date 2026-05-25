import os
import time
import threading
import requests
import streamlit as st
import uvicorn

# Ensure full terminal screen width for industrial-grade data visibility
st.set_page_config(page_title="AETHER-FRACTAL // GOVERNOR CORE", page_icon="💠", layout="wide")

# =====================================================================
# 1. BACKGROUND ENGINE THREAD MANAGER
# =====================================================================
@st.cache_resource
def launch_background_engine():
    """
    Launches the core AETHER-FRACTAL FastAPI engine on a separate,
    isolated system thread to keep inference non-blocking.
    """
    def run_server():
        # Points directly to your renamed engine.py file
        uvicorn.run("engine:app", host="127.0.0.1", port=8000, loop="uvloop", log_level="warning")
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    time.sleep(2)  # Allow kernel boot synchronization lag
    return True

# Initialize the background engine thread
launch_background_engine()

# =====================================================================
# 2. CYBERPUNK TERMINAL THEME STYLING
# =====================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    * { font-family: 'JetBrains+Mono', monospace !important; }
    .reportview-container { background: #0A0A0C; }
    .stMetric { background: #111216; border: 1px solid #1E2028; padding: 15px; border-radius: 4px; box-shadow: 0 2px 10px rgba(0,2,0,0.5); }
    .stMetric label { color: #8F93A2 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
    .stMetric div { color: #00FF66 !important; font-weight: 700 !important; }
    div.stButton > button { background-color: #111216; color: #00FF66; border: 1px solid #00FF66; font-size: 12px; font-weight: bold; border-radius: 2px; width: 100%; transition: all 0.3s; }
    div.stButton > button:hover { background-color: #00FF66; color: #0A0A0C; box-shadow: 0 0 15px rgba(0,255,102,0.6); }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 3. HIGH-DENSITY HUD TERMINAL HEADER
# =====================================================================
st.markdown("<h1 style='color: #FFFFFF; font-size: 26px; margin-bottom: 0px;'>💠 AETHER-FRACTAL // CORE COMMAND RUNTIME</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #4E5266; font-size: 11px; text-transform: uppercase; letter-spacing: 2px;'>Autonomous Edge Actuation & Sovereign Hardware Governance Subsystem</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #1E2028; margin-top: 10px; margin-bottom: 20px;' />", unsafe_allow_html=True)

# =====================================================================
# 4. SYSTEM STATE SIMULATION PANEL (Input Controls)
# =====================================================================
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("<p style='color: #FF3366; font-size: 12px; font-weight: bold;'>⚡ LIVE TELEMETRY SIMULATOR INPUTS</p>", unsafe_allow_html=True)
    
    node_id = st.selectbox("TARGET INSTANCE NODE", ["NODE_ALPHA_01", "NODE_ALPHA_04", "NODE_OMEGA_09"])
    temp = st.slider("SILICON TEMPERATURE (°C)", min_value=40.0, max_value=120.0, value=94.2, step=0.1)
    power = st.slider("POWER DRAW LOAD (kW)", min_value=1.0, max_value=30.0, value=14.8, step=0.1)
    flow = st.slider("COOLANT VELOCITY (LPM)", min_value=0.5, max_value=10.0, value=2.1, step=0.1)
    
    anomaly_msg = st.text_area(
        "CRITICAL ANOMALY EVENT TRIGGER", 
        value="Thermal vector spike exceeding 92C threshold during localized training job load."
    )
    
    trigger_actuation = st.button("DISPATCH TO INFERENCE CASCADE")

# =====================================================================
# 5. INDUSTRIAL PERFORMANCE METRICS & FIREWALL AUDIT TRAIL
# =====================================================================
with col_right:
    if trigger_actuation:
        # Reconstruct the precise data contract payload format
        payload = {
            "telemetry_context": {
                "node_id": node_id,
                "silicon_temperature_celsius": temp,
                "power_draw_kw": power,
                "coolant_flow_rate_lpm": flow
            },
            "query_anomaly": anomaly_msg
        }
        
        try:
            # Query the background FastAPI engine loop over internal network address
            with st.spinner("Processing zero-copy inference pipeline..."):
                response = requests.post("http://127.0.0.1:8000/api/v1/actuate", json=payload)
            
            if response.status_code == 200:
                res_data = response.json()
                command = res_data["command"]
                
                # Render high-speed execution metrics
                m1, m2, m3 = st.columns(3)
                m1.metric(label="GATEWAY STATUS", value=res_data["status"])
                m2.metric(label="LOOP LATENCY", value=f"{res_data['elapsed_ms']} ms")
                m3.metric(label="FIREWALL CLAMP", value="ACTIVE (100%)")
                
                # Structured JSON command dispatch payload viewer
                st.markdown("<p style='color: #00FF66; font-size: 12px; font-weight: bold; margin-top: 20px;'>🛡️ VERIFIED HARDWARE COMMAND OUTBOUND PAYLOAD</p>", unsafe_allow_html=True)
                st.json(command)
                
                # Human readable explanation log
                st.info(f"**GOVERNOR DECISION RATIONALE:** {command['risk_mitigation_reason']}")
                
            else:
                st.error(f"ENGINE CRITICAL SHUTDOWN: Gateway returned status code {response.status_code}")
                st.code(response.text)
                
        except Exception as e:
            st.error(f"AIR-GAP INTERCEPT ENGAGED: Local connection failure to engine kernel. Details: {e}")
    else:
        # Default dashboard idle placeholder state
        m1, m2, m3 = st.columns(3)
        m1.metric(label="GATEWAY STATUS", value="ONLINE")
        m2.metric(label="LOOP LATENCY", value="0.00 ms")
        m3.metric(label="FIREWALL CLAMP", value="READY")
        
        st.markdown("<div style='border: 1px dashed #1E2028; padding: 40px; text-align: center; color: #4E5266; margin-top: 20px; font-size: 12px;'>SYSTEM IDLE // AWAITING STREAM payload TRANSMISSION</div>", unsafe_allow_html=True)
