import os
import time
import requests
import streamlit as st

# Set page config once at the absolute top
st.set_page_config(page_title="AETHER-FRACTAL // GOVERNOR CORE", page_icon="💠", layout="wide")

# =====================================================================
# 1. CYBERPUNK HUD TERMINAL STYLING
# =====================================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght=400;700&display=swap');
    * { font-family: 'JetBrains+Mono', monospace !important; }
    .stApp { background: #0A0A0C !important; }
    .stMetric { background: #111216; border: 1px solid #1E2028; padding: 15px; border-radius: 4px; }
    .stMetric label { color: #8F93A2 !important; font-size: 11px !important; text-transform: uppercase; letter-spacing: 1px; }
    .stMetric div { color: #00FF66 !important; font-weight: 700 !important; }
    div.stButton > button { background-color: #111216; color: #00FF66; border: 1px solid #00FF66; font-weight: bold; width: 100%; transition: all 0.3s; }
    div.stButton > button:hover { background-color: #00FF66; color: #0A0A0C; box-shadow: 0 0 15px rgba(0,255,102,0.6); }
    </style>
""", unsafe_allow_html=True)

# =====================================================================
# 2. RUNTIME DASHBOARD HEADER
# =====================================================================
st.markdown("<h1 style='color: #FFFFFF; font-size: 26px; margin-bottom: 0px;'>💠 AETHER-FRACTAL // CORE HUD</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #4E5266; font-size: 11px; text-transform: uppercase; letter-spacing: 2px;'>Autonomous Edge Actuation & Sovereign Hardware Governance Subsystem</p>", unsafe_allow_html=True)
st.markdown("<hr style='border-color: #1E2028; margin-top: 10px; margin-bottom: 20px;' />", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 2])

# =====================================================================
# 3. LEFT PANEL: LIVE TELEMETRY SIMULATOR
# =====================================================================
with col_left:
    st.markdown("<p style='color: #FF3366; font-size: 12px; font-weight: bold;'>⚡ LIVE TELEMETRY SIMULATOR</p>", unsafe_allow_html=True)
    
    node_id = st.selectbox("TARGET INSTANCE NODE", ["NODE_ALPHA_01", "NODE_ALPHA_04", "NODE_OMEGA_09"])
    temp = st.slider("SILICON TEMP (°C)", min_value=40.0, max_value=120.0, value=94.2, step=0.1)
    power = st.slider("POWER DRAW (kW)", min_value=1.0, max_value=30.0, value=14.8, step=0.1)
    flow = st.slider("COOLANT FLOW (LPM)", min_value=0.5, max_value=10.0, value=2.1, step=0.1)
    
    anomaly_msg = st.text_area(
        "CRITICAL ANOMALY EVENT TRIGGER", 
        value="Thermal vector spike exceeding 92C threshold during localized training job load."
    )
    
    trigger_actuation = st.button("DISPATCH COMMAND")

# =====================================================================
# 4. RIGHT PANEL: DETERMINISTIC FRONTEND LOGIC
# =====================================================================
with col_right:
    if trigger_actuation:
        payload = {
            "telemetry_context": {
                "node_id": node_id,
                "silicon_temperature_celsius": temp,
                "power_draw_kw": power,
                "coolant_flow_rate_lpm": flow
            },
            "query_anomaly": anomaly_msg
        }
        
        command = None
        elapsed = 0.0
        status_msg = "UNKNOWN"
        
        # --- DUAL EXECUTION ROUTER ---
        try:
            # MODE A: Local API Connection Path
            response = requests.post("http://127.0.0.1:8000/api/v1/actuate", json=payload, timeout=1.0)
            if response.status_code == 200:
                res_data = response.json()
                command = res_data["command"]
                elapsed = res_data["elapsed_ms"]
                status_msg = res_data["status"]
            else:
                st.error(f"ENGINE CRITICAL ERROR: Gateway returned status code {response.status_code}")
                
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # MODE B: Cloud Container Deployment Gateway Path
            try:
                import main  
                from groq import AsyncGroq
                import asyncio
                
                api_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
                
                if not api_key:
                    st.error("AIR-GAP CRITICAL INTERVENTION: GROQ_API_KEY missing from Streamlit Secrets.")
                else:
                    client = AsyncGroq(api_key=api_key)
                    start_time = time.perf_counter()
                    
                    command = asyncio.run(main.run_resilient_cascade(
                        client=client, 
                        telemetry=payload["telemetry_context"], 
                        anomaly=payload["query_anomaly"]
                    ))
                    
                    elapsed = round((time.perf_counter() - start_time) * 1000, 2)
                    status_msg = "SUCCESS (CLOUD DIRECT VIA MAIN.PY)"
            except Exception as cloud_err:
                st.error(f"RUNTIME PANIC: Failed direct module execution. Details: {cloud_err}")

        if command:
            m1, m2, m3 = st.columns(3)
            m1.metric(label="GATEWAY PIPELINE", value=status_msg)
            m2.metric(label="LOOP LATENCY", value=f"{elapsed} ms")
            m3.metric(label="FIREWALL CLAMP", value="ACTIVE (100%)")
            
            st.markdown("<p style='color: #00FF66; font-size: 12px; font-weight: bold; margin-top: 20px;'>🛡️ VERIFIED HARDWARE COMMAND OUTBOUND PAYLOAD</p>", unsafe_allow_html=True)
            st.json(command)
            st.info(f"**GOVERNOR DECISION RATIONALE:** {command['risk_mitigation_reason']}")
            
    else:
        m1, m2, m3 = st.columns(3)
        m1.metric(label="GATEWAY STATUS", value="ONLINE")
        m2.metric(label="LOOP LATENCY", value="0.00 ms")
        m3.metric(label="FIREWALL CLAMP", value="READY")
        st.markdown("<div style='border: 1px dashed #1E2028; padding: 40px; text-align: center; color: #4E5266; margin-top: 20px; font-size: 12px;'>SYSTEM IDLE // AWAITING STREAM PAYLOAD TRANSMISSION</div>", unsafe_allow_html=True)
