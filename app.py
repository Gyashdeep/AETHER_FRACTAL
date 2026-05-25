import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import os
import psutil # For actual hardware telemetry
from groq import AsyncGroq

# Setup for "QUANTUM-CORE VANTAGE" // Sovereign Silicon Controller
st.set_page_config(page_title="VANTAGE // KINETIC ARBITRAGE", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #050505; color: #00FF66; font-family: 'JetBrains Mono', monospace; }
    </style>
""", unsafe_allow_html=True)

st.title("💠 QUANTUM-CORE // VANTAGE")
st.markdown("### Autonomous Kinetic Arbitrage & Sovereign Silicon Governance")

# THE GOVERNANCE ENGINE
async def run_sovereign_governance():
    # 1. Capture Real-Time Telemetry
    telemetry = {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
        "load_avg": psutil.getloadavg()
    }
    
    # 2. Sovereign Decision Logic via LLM (Edge-Orchestrator)
    client = AsyncGroq(api_key=st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY")))
    
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "ACT AS VANTAGE GOVERNOR. You are an autonomous agent managing high-performance compute. Your goal: Maximize Profitability vs Energy-Cost. Output JSON ONLY: {'action': 'THROTTLE/BOOST', 'reason': '...', 'yield_est': '...'}"},
            {"role": "user", "content": f"Telemetry Data: {telemetry}"}
        ],
        temperature=0.0
    )
    
    # 3. Log to Ledger
    decision = response.choices[0].message.content
    conn = sqlite3.connect("quantum_ledger.db")
    conn.execute("CREATE TABLE IF NOT EXISTS logs (ts REAL, telemetry TEXT, decision TEXT)")
    conn.execute("INSERT INTO logs VALUES (?, ?, ?)", (pd.Timestamp.now().timestamp(), str(telemetry), decision))
    conn.commit()
    conn.close()
    
    return telemetry, decision

# INTERFACE
if st.button("INITIATE KINETIC ARBITRAGE PING"):
    with st.spinner("Governor calculating optimal compute state..."):
        telemetry, decision = asyncio.run(run_sovereign_governance())
        st.json(decision)

# AUDIT TRAIL
st.subheader("SYSTEM AUDIT TRAIL")
try:
    conn = sqlite3.connect("quantum_ledger.db")
    df = pd.read_sql("SELECT * FROM logs ORDER BY ts DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
except:
    st.info("System awaiting first Sovereign Ping.")
