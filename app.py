"""
ThreatLens AI - Explainable Deep Learning Network Intrusion Detection
Main Security Operations Center (SOC) Application Entry Point
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path

# Set Page Configuration
st.set_page_config(
    page_title="ThreatLens AI - Deep Learning NIDS",
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
    st.markdown("**Explainable Deep Learning NIDS**")
    st.markdown("---")
    
    # System status checks
    model_ready = os.path.exists("models/mlp_model.pt") and os.path.exists("models/preprocessing.pkl")
    baseline_ready = os.path.exists("models/baseline_logreg.pkl")
    sample_ready = os.path.exists("data/raw/cicids2017_sample.csv")
    
    st.subheader("System Telemetry")
    if model_ready:
        st.markdown("🟢 **PyTorch Model:** Ready")
    else:
        st.markdown("🔴 **PyTorch Model:** Missing")
        
    if baseline_ready:
        st.markdown("🟢 **Baseline Model:** Evaluated")
    else:
        st.markdown("🟡 **Baseline Model:** Pending")
        
    if sample_ready:
        st.markdown("🟢 **CIC-IDS2017 Dataset:** Loaded")
    else:
        st.markdown("🟡 **Dataset:** Not found")
        
    st.markdown("---")
    st.caption("ThreatLens AI Deep Learning Project\nBenchmarked on CIC-IDS2017 flow data.")

# Main Page Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("ThreatLens AI — SOC Operations Hub")
    st.markdown(
        "An advanced deep learning cybersecurity system combining a **PyTorch Multi-Layer Perceptron (MLP)** "
        "with an **Explainable Feature Attribution Engine** and rigorous benchmark evaluation on **CIC-IDS2017**."
    )
with col2:
    st.markdown("""
    <div style='text-align: right; padding-top: 15px;'>
        <span class='badge-info'>Deep Learning</span>&nbsp;
        <span class='badge-critical'>PyTorch MLP</span>&nbsp;
        <span class='badge-benign'>XAI Saliency</span>
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
        <span class='badge-info'>PyTorch Neural Network</span>
    </div>
    """, unsafe_allow_html=True)

with col_b:
    st.markdown("""
    <div class='soc-card'>
        <h3>2. Explainable AI Saliency</h3>
        <p style='color: #8b949e; font-size: 0.92rem;'>
            Mathematical gradient-based feature attribution highlights the top flow features 
            (packet rate, SYN flags, duration) that influenced the neural network to flag a flow.
        </p>
        <span class='badge-critical'>Input * Gradient Attribution</span>
    </div>
    """, unsafe_allow_html=True)

with col_c:
    st.markdown("""
    <div class='soc-card'>
        <h3>3. Rigorous Evaluation</h3>
        <p style='color: #8b949e; font-size: 0.92rem;'>
            Benchmarked against a Logistic Regression baseline on held-out test data. 
            Reports Precision, Recall, F1-Score, ROC-AUC, PR-AUC, and sub-millisecond CPU latency.
        </p>
        <span class='badge-benign'>Held-out Test Metrics</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Navigating ThreatLens AI")
st.markdown("""
Use the sidebar navigation tabs to explore each functional component:
- 📊 **[1_Overview](1_Overview)**: High-level SOC telemetry, flow statistics, recent alerts, and architectural workflow.
- 🔍 **[2_Traffic_Analysis](2_Traffic_Analysis)**: Upload network flow CSVs, execute real-time PyTorch inference, inspect flow attributions, and export analysis reports.
- 📈 **[3_Model_Evaluation](3_Model_Evaluation)**: Review academic evaluation metrics, baseline comparison against Logistic Regression, ROC/PR curves, confusion matrices, and latency benchmarks.
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
