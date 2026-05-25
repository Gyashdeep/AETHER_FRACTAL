import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import os
import psutil
from groq import AsyncGroq

# CONFIGURATION // QUANTUM-CORE VANTAGE
st.set_page_config(page_title="VANTAGE // KINETIC ARBITRAGE", layout="wide")
st.markdown("""
    <style>
    .stApp { background: #050505; color: #00FF66; font-family: 'JetBrains Mono', monospace; }
    </style>
""", unsafe_allow_html=True)

st.title("💠 QUANTUM-CORE // VANTAGE")
st.markdown("### Autonomous Kinetic Arbitrage & Sovereign Silicon Governance")

# --- SOVEREIGN GOVERNANCE ENGINE ---
async def execute_sovereign_logic():
    # 1. Hardware Telemetry
    telemetry = {
        "cpu_load": psutil.cpu_percent(),
        "mem_load": psutil.virtual_memory().percent,
        "ts": pd.Timestamp.now().isoformat()
    }
    
    # 2. Autonomous Decision Logic
    client = AsyncGroq(api_key=st.secrets.get("GROQ_API_KEY"))
    prompt = f"ACT AS QUANTUM-CORE VANTAGE. Analyze {telemetry}. Output ONLY JSON: {{'decision': 'BOOST/THROTTLE', 'rationale': '...', 'yield_pct': '...'}}"
    
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": prompt}],
        temperature=0.0
    )
    
    decision = response.choices[0].message.content
    
    # 3. Persistent Ledger
    conn = sqlite3.connect("quantum_ledger.db")
    conn.execute("CREATE TABLE IF NOT EXISTS logs (ts REAL, telemetry TEXT, decision TEXT)")
    conn.execute("INSERT INTO logs VALUES (?, ?, ?)", (pd.Timestamp.now().timestamp(), str(telemetry), decision))
    conn.commit()
    conn.close()
    return decision

# --- INTERFACE ---
if st.button("INITIATE KINETIC ARBITRAGE"):
    with st.spinner("Vantage Governor calculating optimal silicon state..."):
        decision = asyncio.run(execute_sovereign_logic())
        st.json(decision)

st.subheader("SYSTEM AUDIT TRAIL")
try:
    conn = sqlite3.connect("quantum_ledger.db")
    df = pd.read_sql("SELECT * FROM logs ORDER BY ts DESC", conn)
    st.dataframe(df, use_container_width=True)
    conn.close()
except:
    st.info("System awaiting first Sovereign Ping.")
