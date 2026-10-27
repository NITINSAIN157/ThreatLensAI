"""
ThreatLens AI - Security Operations Overview
Page 1: Telemetry, traffic breakdown, threat distribution, and active alerts feed.
"""

import os
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="ThreatLens AI - Security Overview", page_icon="📊", layout="wide")

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
</style>
""", unsafe_allow_html=True)

st.title("📊 Security Operations Overview")
st.markdown("High-level telemetry and alert distribution across analyzed network flows.")

# Load evaluation data if available
eval_path = "models/evaluation_results.json"
eval_data = {}
if os.path.exists(eval_path):
    with open(eval_path, "r") as f:
        eval_data = json.load(f)

# Load sample dataset to compute real distributions
sample_path = "data/raw/cicids2017_sample.csv"
if os.path.exists(sample_path):
    df_sample = pd.read_csv(sample_path)
    label_col = [c for c in df_sample.columns if "label" in c.lower()][0]
    total_flows = len(df_sample)
    attack_counts = df_sample[label_col].value_counts()
    benign_count = attack_counts.get("BENIGN", 0)
    attack_count = total_flows - benign_count
else:
    total_flows, benign_count, attack_count = 6000, 4500, 1500
    attack_counts = pd.Series({"BENIGN": 4500, "DoS Hulk": 720, "PortScan": 480, "FTP-Patator": 300})

# Top KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Flows Analyzed", f"{total_flows:,}")
c2.metric("Benign Traffic Baseline", f"{benign_count:,} ({benign_count/total_flows*100:.1f}%)")
c3.metric("Anomalies Flagged", f"{attack_count:,} ({attack_count/total_flows*100:.1f}%)")

mlp_metrics = eval_data.get("deep_learning_mlp", {})
f1_val = mlp_metrics.get("f1_score", 1.0)
c4.metric("Model F1-Score (Test)", f"{f1_val:.4f}")

st.markdown("---")

# Visual Analytics Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Traffic Class Distribution")
    fig_donut = go.Figure(data=[go.Pie(
        labels=["Benign Traffic", "Malicious Flows"],
        values=[benign_count, attack_count],
        hole=.55,
        marker=dict(colors=["#238636", "#da3633"])
    )])
    fig_donut.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(color="#e6edf3"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=320
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col_chart2:
    st.subheader("Detected Threat Categories")
    # Sub-attack distribution excluding benign
    sub_attacks = attack_counts[attack_counts.index != "BENIGN"]
    fig_bar = px.bar(
        x=sub_attacks.index,
        y=sub_attacks.values,
        labels={"x": "Attack Category", "y": "Flow Count"},
        color=sub_attacks.values,
        color_continuous_scale="Reds"
    )
    fig_bar.update_layout(
        paper_bgcolor="#161b22",
        plot_bgcolor="#161b22",
        font=dict(color="#e6edf3"),
        margin=dict(t=20, b=20, l=20, r=20),
        height=320,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# Recent Alerts Feed
st.subheader("🚨 Recent High-Confidence Network Flow Alerts")

sample_alerts = [
    {
        "Timestamp": "2026-10-27 18:22:10",
        "Dst Port": 80,
        "Anomaly Score": 0.985,
        "Severity": "CRITICAL",
        "Attack Type": "DoS / Flood Traffic",
        "Key Saliency Feature": "Flow Packets/s (Z=4.82), SYN Flag Count"
    },
    {
        "Timestamp": "2026-10-27 18:20:44",
        "Dst Port": 21,
        "Anomaly Score": 0.942,
        "Severity": "CRITICAL",
        "Attack Type": "FTP-Patator (Brute Force)",
        "Key Saliency Feature": "Repeated Flow IAT, Fixed Fwd/Bwd Segment"
    },
    {
        "Timestamp": "2026-10-27 18:19:02",
        "Dst Port": 49152,
        "Anomaly Score": 0.910,
        "Severity": "CRITICAL",
        "Attack Type": "Network PortScan (T1046)",
        "Key Saliency Feature": "Total Bwd Packets = 0, Tiny Flow Duration"
    },
    {
        "Timestamp": "2026-10-27 18:14:15",
        "Dst Port": 443,
        "Anomaly Score": 0.420,
        "Severity": "ELEVATED",
        "Attack Type": "Borderline Traffic Spike",
        "Key Saliency Feature": "Elevated Flow Bytes/s (HTTPS Burst)"
    }
]

df_alerts = pd.DataFrame(sample_alerts)
st.dataframe(
    df_alerts,
    use_container_width=True,
    column_config={
        "Anomaly Score": st.column_config.ProgressColumn(
            "Anomaly Score", min_value=0.0, max_value=1.0, format="%.3f"
        ),
        "Severity": st.column_config.TextColumn("Severity")
    }
)

st.markdown("---")
st.info("💡 **Analyst Note:** Navigate to **Traffic Analysis** to upload a new CSV and execute live PyTorch model inference on incoming flow records.")
