import streamlit as st
from engine.sovereign import run_governance_pulse

# Sovereign Configuration
st.set_page_config(page_title="AETHER-KINETIC // VANTAGE", layout="wide")
st.markdown("<style>.stApp { background: #020202; color: #00FF66; font-family: monospace; }</style>", unsafe_allow_html=True)

st.title("💠 AETHER-KINETIC // VANTAGE")
st.markdown("### Autonomous Sovereign Governance | Kinetic Arbitrage Engine")

# Sovereign Trigger
if st.button("INITIATE SOVEREIGN PULSE"):
    with st.spinner("Reconciling silicon state-space..."):
        result = run_governance_pulse()
        st.json(result)

st.subheader("LIVE NEURAL AUDIT")
st.info("System awaiting telemetry feedback from the Governance Manifold.")
