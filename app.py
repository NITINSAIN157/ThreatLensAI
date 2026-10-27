"""
ThreatLens AI - Explainable Network Intrusion Detection with RAG
Main Security Operations Center (SOC) Application Entry Point
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path

# Set Page Configuration
st.set_page_config(
    page_title="ThreatLens AI - SOC Operations Hub",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Dark SOC Theme Styling
st.markdown("""
<style>
    /* Dark SOC Theme Colors */
    .stApp {
        background-color: #0c1017;
        color: #e6edf3;
    }
    
    /* Header & Titles */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
    }
    
    /* Metric Cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important;
        font-weight: 700;
        color: #58a6ff;
    }
    div[data-testid="stMetricLabel"] {
        color: #8b949e !important;
        font-size: 0.9rem;
    }
    
    /* Card Container */
    .soc-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 18px;
        margin-bottom: 16px;
    }
    
    .badge-critical {
        background-color: rgba(248, 81, 73, 0.2);
        color: #f85149;
        border: 1px solid #f85149;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .badge-benign {
        background-color: rgba(63, 185, 80, 0.2);
        color: #3fb950;
        border: 1px solid #3fb950;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
    
    .badge-info {
        background-color: rgba(88, 166, 255, 0.2);
        color: #58a6ff;
        border: 1px solid #58a6ff;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("ThreatLens AI")
    st.markdown("**Explainable NIDS & RAG Assistant**")
    st.markdown("---")
    
    # System status checks
    model_ready = os.path.exists("models/mlp_model.pt") and os.path.exists("models/preprocessing.pkl")
    vector_ready = os.path.exists("vector_store") and os.path.exists("knowledge_base/documents")
    sample_ready = os.path.exists("data/raw/cicids2017_sample.csv")
    
    st.subheader("System Telemetry")
    if model_ready:
        st.markdown("🟢 **PyTorch Model:** Ready")
    else:
        st.markdown("🔴 **PyTorch Model:** Missing")
        
    if vector_ready:
        st.markdown("🟢 **RAG Vector Store:** Indexed")
    else:
        st.markdown("🟡 **RAG Vector Store:** Pending")
        
    if sample_ready:
        st.markdown("🟢 **CIC-IDS2017 Dataset:** Loaded")
    else:
        st.markdown("🟡 **Dataset:** Not found")
        
    st.markdown("---")
    st.caption("ThreatLens AI Research Prototype v1.0\nBenchmarked on CIC-IDS2017 flow data.")

# Main Page Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("ThreatLens AI — SOC Operations Hub")
    st.markdown(
        "A hybrid cybersecurity operations system combining a **PyTorch Deep Learning Intrusion Detection Model** "
        "with an **Explainable Feature Attribution Engine** and a **Grounded RAG Security Assistant**."
    )
with col2:
    st.markdown("""
    <div style='text-align: right; padding-top: 15px;'>
        <span class='badge-info'>Deep Learning</span>&nbsp;
        <span class='badge-critical'>PyTorch MLP</span>&nbsp;
        <span class='badge-benign'>RAG + Chroma</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Three Pillars of ThreatLens
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("""
    <div class='soc-card'>
        <h3>1. Deep Learning Detection</h3>
        <p style='color: #8b949e; font-size: 0.92rem;'>
            A PyTorch Multi-Layer Perceptron (MLP) trained on the benchmark <b>CIC-IDS2017</b> dataset 
            identifies suspicious network connections using 59 standardized numeric flow features.
        </p>
        <span class='badge-info'>Batch & Single Flow Inference</span>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class='soc-card'>
        <h3>2. Explainable AI Saliency</h3>
        <p style='color: #8b949e; font-size: 0.92rem;'>
            Mathematical gradient-based feature attribution highlights the top flow features 
            (packet rate, SYN flags, duration) that influenced the model to flag a flow.
        </p>
        <span class='badge-critical'>Input * Gradient Attribution</span>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class='soc-card'>
        <h3>3. Grounded RAG Guidance</h3>
        <p style='color: #8b949e; font-size: 0.92rem;'>
            A Retrieval-Augmented Generation assistant grounds triage questions in <b>MITRE ATT&CK</b>, 
            <b>NIST SP 800-61</b>, and incident playbooks with exact technical citations.
        </p>
        <span class='badge-benign'>Vector Search with Citations</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Navigating ThreatLens AI")
st.markdown("""
Use the sidebar navigation tabs to explore each functional component:
- 📊 **[1_Overview](1_Overview)**: High-level SOC telemetry, flow statistics, recent alerts, and architectural workflow.
- 🔍 **[2_Traffic_Analysis](2_Traffic_Analysis)**: Upload network flow CSVs, execute real-time PyTorch inference, inspect flow attributions, and export analysis reports.
- 🤖 **[3_Security_Assistant](3_Security_Assistant)**: Query the RAG knowledge base for grounded adversary tactics, flow diagnostics, and containment guidance.
- 📈 **[4_Model_Evaluation](4_Model_Evaluation)**: Review academic evaluation metrics, baseline comparison against Logistic Regression, ROC/PR curves, confusion matrices, and latency.
""")

# Quick KPI Snapshot
if os.path.exists("models/evaluation_results.json"):
    with open("models/evaluation_results.json", "r") as f:
        eval_data = json.load(f)
        
    mlp = eval_data.get("deep_learning_mlp", {})
    st.markdown("### Pre-Evaluated Model Baseline Metrics")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Test F1-Score", f"{mlp.get('f1_score', 0):.4f}")
    m2.metric("ROC-AUC", f"{mlp.get('roc_auc', 0):.4f}")
    m3.metric("PR-AUC", f"{mlp.get('pr_auc', 0):.4f}")
    m4.metric("CPU Latency", f"{mlp.get('latency', {}).get('single_sample_latency_ms', 0):.2f} ms")
    m5.metric("Decision Threshold", f"{mlp.get('decision_threshold', 0.5):.2f}")
