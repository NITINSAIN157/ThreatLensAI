"""
ThreatLens AI - RAG Security Assistant
Page 3: Interactive cybersecurity question answering, grounded incident-response
guidance, and technical citations from MITRE ATT&CK, NIST SP 800-61, and CIC-IDS2017 specs.
"""

import os
import sys
import streamlit as st
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.rag_assistant import ThreatLensSecurityAssistant

st.set_page_config(page_title="ThreatLens AI - RAG Security Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0c1017; color: #e6edf3; }
    h1, h2, h3 { color: #58a6ff !important; }
    .soc-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 14px;
    }
    .citation-card {
        background-color: #0d1117;
        border-left: 3px solid #58a6ff;
        padding: 10px 14px;
        margin-top: 8px;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_assistant():
    return ThreatLensSecurityAssistant()

st.title("🤖 RAG Security Assistant")
st.markdown(
    "Ask operational security questions or investigate flagged alerts. "
    "Guidance is strictly grounded in **MITRE ATT&CK**, **NIST SP 800-61 Rev. 2**, and **CIC-IDS2017 technical documentation**."
)

assistant = load_assistant()

# Check for transferred query from Traffic Analysis
default_query = st.session_state.get("rag_query", "")

# Quick Scenario Templates
st.markdown("##### ⚡ Quick Analyst Scenarios")
q_col1, q_col2, q_col3 = st.columns(3)

with q_col1:
    if st.button("🌊 Unusual Packet Rate & DoS"):
        default_query = "What should I investigate when a network flow shows an unusual packet rate?"
with q_col2:
    if st.button("🔍 SYN Flood & PortScan Indicators"):
        default_query = "What adversary techniques and indicators are associated with high SYN flags and zero backward packets?"
with q_col3:
    if st.button("🔑 Brute Force Triage (Patator)"):
        default_query = "What are the NIST containment procedures for repeated connection attempts on ports 21 and 22?"

# Query Input
query_input = st.text_area(
    "Enter Security Investigation Question:",
    value=default_query,
    height=90,
    placeholder="e.g., How should an analyst respond to a volumetric DoS alert on port 80?"
)

col_btn, col_thresh = st.columns([1, 2])
with col_btn:
    run_query = st.button("🔎 Retrieve & Synthesize Guidance", type="primary", use_container_width=True)

if run_query and query_input.strip():
    with st.spinner("Searching vector index & synthesizing grounded response..."):
        res = assistant.generate_response(query_input.strip(), top_k=4)
        
    st.markdown("---")
    
    # Grounded Answer Container
    st.subheader("📋 Grounded Operational Guidance")
    st.markdown(f"<div class='soc-card'>{res['answer']}</div>", unsafe_allow_html=True)
    st.caption(f"Engine: **{res['source_used']}** | Relevant Passages Retrieved: **{res['retrieved_count']}**")
    
    # Technical Citations Section
    if res.get("citations"):
        st.markdown("### 📚 Source Citations & Technical Evidence")
        for cit in res["citations"]:
            with st.expander(f"{cit['citation_id']} {cit['title']} — Section: {cit['section']} (Relevance Score: {cit['score']:.4f})"):
                st.markdown(f"**Document File:** `{cit['source']}` | **Page:** `{cit['page']}`")
                st.markdown(f"**Document Excerpt:**\n> {cit['excerpt']}")
                
    st.markdown("---")
    st.info(
        "🛡️ **SOC Compliance Reminder:** The RAG assistant provides investigative guidance based on indexed documentation. "
        "Detection model scores quantify statistical anomaly likelihood and must be validated through host and firewall logs."
    )
