import streamlit as st
import psutil
import json
import asyncio
from groq import AsyncGroq
import time

# --- SOVEREIGN CONFIGURATION ---
st.set_page_config(page_title="AETHER-KINETIC // VANTAGE", layout="wide")
st.markdown("""<style>.stApp { background: #020202; color: #00FF66; font-family: monospace; }</style>""", unsafe_allow_html=True)

# --- GOVERNANCE MANIFOLD (HARDENED) ---
async def execute_sovereign_edict():
    telemetry = {
        "cpu_load": psutil.cpu_percent(interval=0.1),
        "mem_load": psutil.virtual_memory().percent,
        "status": "OPERATIONAL_NODE"
    }
    
    client = AsyncGroq(api_key=st.secrets["GROQ_API_KEY"])
    
    prompt = """
    ACT AS AETHER-KINETIC GOVERNANCE. 
    Analyze telemetry and output ONLY raw, parseable JSON. 
    Format: {"decision": "BOOST/THROTTLE", "yield": "0.00%", "rationale": "..."}
    """
    
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": str(telemetry)}
        ],
        temperature=0.0
    )
    
    raw = response.choices[0].message.content.strip()
    clean = raw.replace('```json', '').replace('```', '').strip()
    return json.loads(clean)

# --- UI GATEWAY ---
st.title("💠 AETHER-KINETIC // VANTAGE")
st.markdown("### Autonomous Sovereign Governance | Kinetic Arbitrage Engine")

# Auto-Governance Heartbeat Logic
if "auto_governance" not in st.session_state:
    st.session_state.auto_governance = False

if st.sidebar.button("ACTIVATE AUTONOMOUS HEARTBEAT"):
    st.session_state.auto_governance = True
    st.rerun()

if st.session_state.auto_governance:
    st.sidebar.warning("HEARTBEAT: ACTIVE // KINETIC ARBITRAGE ENGAGED")
    try:
        result = asyncio.run(execute_sovereign_edict())
        st.json(result)
        time.sleep(5) # 5-second sovereign reconciliation cycle
        st.rerun()
    except Exception as e:
        st.error(f"GOVERNANCE DRIFT: {str(e)}")
        st.session_state.auto_governance = False

st.subheader("SYSTEM AUDIT TRAIL")
st.info("System awaiting pulse initialization...")
