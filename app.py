import streamlit as st
import sqlite3
import pandas as pd
import requests
import plotly.express as px

# Configuration
st.set_page_config(page_title="AETHER-FRACTAL // GOVERNOR HUD", layout="wide")
GOVERNOR_API = "http://127.0.0.1:8000"

# Styling for Industrial Dashboard
st.markdown("""
    <style>
    .stApp { background: #050505; color: #00FF66; font-family: 'JetBrains Mono', monospace; }
    .metric-card { background: #111; padding: 20px; border: 1px solid #333; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("💠 AETHER-FRACTAL // GOVERNOR CORE")
st.markdown("### Industrial Sovereign Governance Interface")

# --- DATA RETRIEVAL ---
def get_ledger_data():
    conn = sqlite3.connect("governance_ledger.db")
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY ts DESC LIMIT 50", conn)
    conn.close()
    return df

# --- LAYOUT ---
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("LIVE ACTUATION")
    if st.button("TRIGGER GOVERNANCE STATUS"):
        try:
            res = requests.get(f"{GOVERNOR_API}/api/v1/governance/status").json()
            st.json(res)
        except Exception as e:
            st.error(f"ENGINE_OFFLINE: {e}")
            
    st.subheader("FAIL-SAFE OVERRIDE")
    if st.button("MANUAL THROTTLE // EMERGENCY"):
        st.warning("PHYSICAL HARDWARE THROTTLE ACTIVATED")

with col2:
    st.subheader("SYSTEM AUDIT TRAIL")
    df = get_ledger_data()
    if not df.empty:
        fig = px.line(df, x='ts', y='decision', title="Governance Decision Vector")
        fig.update_layout(plot_bgcolor="#050505", paper_bgcolor="#050505", font_color="#00FF66")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(df.head(10), use_container_width=True)
