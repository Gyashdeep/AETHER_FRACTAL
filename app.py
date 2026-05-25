import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import os
from groq import AsyncGroq

# Setup for QUANTUM-CORE VANTAGE
st.set_page_config(page_title="VANTAGE // GOVERNOR HUD", layout="wide")
st.markdown("<h1 style='color:#00FF66;'>💠 QUANTUM-CORE VANTAGE</h1>", unsafe_allow_html=True)

# Governance Logic: Integrated Engine
async def execute_vantage_protocol():
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        st.error("API_KEY missing in Streamlit Secrets.")
        return None, None
        
    client = AsyncGroq(api_key=api_key)
    telemetry = {"silicon_temp": 55.0, "power_draw_kw": 12.4, "status": "NOMINAL"}
    
    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "ACT AS VANTAGE GOVERNOR. Optimize yield. JSON ONLY."},
            {"role": "user", "content": str(telemetry)}
        ],
        temperature=0.0
    )
    return telemetry, response.choices[0].message.content

# Interface
if st.button("EXECUTE GOVERNANCE PING"):
    with st.spinner("Vantage Governor Calculating..."):
        telemetry, decision = asyncio.run(execute_vantage_protocol())
        
        if decision:
            conn = sqlite3.connect("quantum_ledger.db")
            conn.execute("CREATE TABLE IF NOT EXISTS logs (ts REAL, telemetry TEXT, decision TEXT)")
            conn.execute("INSERT INTO logs VALUES (?, ?, ?)", (pd.Timestamp.now().timestamp(), str(telemetry), decision))
            conn.commit()
            conn.close()
            st.success("Governance Ping Complete")
            st.json(decision)

# Ledger Visualization
st.subheader("SYSTEM AUDIT TRAIL")
try:
    conn = sqlite3.connect("quantum_ledger.db")
    df = pd.read_sql("SELECT * FROM logs ORDER BY ts DESC LIMIT 10", conn)
    st.dataframe(df)
    conn.close()
except:
    st.info("System initializing...")
