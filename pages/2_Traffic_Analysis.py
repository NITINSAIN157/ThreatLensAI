"""
ThreatLens AI - Traffic Analysis & Live Deep Learning Inference
Page 2: Upload flow records, execute PyTorch inference, inspect explainable features, and export results.
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.predict import ThreatLensPredictor

st.set_page_config(page_title="ThreatLens AI - Traffic Analysis", page_icon="🔍", layout="wide")

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

@st.cache_resource
def load_predictor():
    return ThreatLensPredictor(models_dir="models")

st.title("🔍 Network Traffic Analysis & Inference")
st.markdown("Execute real-time **PyTorch Deep Learning** inference on network-flow records with explainable feature attribution.")

# Initialize predictor
try:
    predictor = load_predictor()
except Exception as e:
    st.error(f"Error loading PyTorch model: {e}. Please ensure `models/mlp_model.pt` exists.")
    st.stop()

# Data input options
col_input1, col_input2 = st.columns([2, 1])

with col_input1:
    uploaded_file = st.file_uploader(
        "Upload Network-Flow CSV (CIC-IDS2017 format)",
        type=["csv"],
        help="Upload a CSV containing network connection features (e.g., Flow Duration, Packet counts, Flags)."
    )

with col_input2:
    st.markdown("<br>", unsafe_allow_html=True)
    load_sample = st.button("📁 Load Bundled Test Batch (250 Flows)", use_container_width=True)

df_input = None
if uploaded_file is not None:
    try:
        df_raw = pd.read_csv(uploaded_file)
        total_uploaded = len(df_raw)

        if total_uploaded > 2000:
            st.warning(
                f"⚡ **Large file detected:** {total_uploaded:,} rows uploaded. "
                "Running inference on the full file may take several minutes on CPU. "
                "Select how many rows to analyse below:"
            )
            max_rows = st.select_slider(
                "Rows to analyse (sample from full file)",
                options=[500, 1000, 2000, 5000, 10000, total_uploaded],
                value=1000,
                format_func=lambda x: f"All {x:,} rows" if x == total_uploaded else f"{x:,} rows (~{x//225:.0f} sec)"
            )
            if max_rows < total_uploaded:
                df_input = df_raw.sample(n=max_rows, random_state=42).reset_index(drop=True)
                st.info(f"✂️ Randomly sampled **{max_rows:,}** rows from {total_uploaded:,} for fast inference.")
            else:
                df_input = df_raw
                st.info(f"Running on all {total_uploaded:,} rows — this may take a few minutes.")
        else:
            df_input = df_raw
            st.success(f"Uploaded CSV loaded successfully ({total_uploaded:,} flow records).")

    except Exception as e:
        st.error(f"Failed to read CSV: {e}")
elif load_sample:
    sample_path = "data/raw/cicids2017_test_batch.csv"
    if os.path.exists(sample_path):
        df_input = pd.read_csv(sample_path)
        st.info(f"Loaded bundled benchmark test batch ({len(df_input)} flows).")
    else:
        st.warning("Sample test batch file not found. Please upload a CSV.")

# If data is available, run inference — disable per-row gradient explanation for large batches
if df_input is not None:
    batch_size = len(df_input)
    # Skip gradient saliency for large batches (>2000 rows) to keep it fast
    top_k_exp = 3 if batch_size <= 2000 else 0

    with st.spinner(f"Executing PyTorch Deep Learning inference on {batch_size:,} flows{' (saliency skipped for large batch)' if top_k_exp == 0 else ' & computing feature saliency'}..."):
        results_df = predictor.predict_dataframe(df_input, top_k_explanations=top_k_exp)
        
    st.markdown("---")
    
    # Inference Summary KPIs
    tot_evaluated = len(results_df)
    n_attacks = (results_df["Prediction"] == "ATTACK").sum()
    n_benign = tot_evaluated - n_attacks
    n_critical = (results_df["Risk_Level"] == "CRITICAL").sum()
    avg_score = results_df["Anomaly_Score"].mean()
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Flows Analyzed", f"{tot_evaluated:,}")
    k2.metric("Benign Classified", f"{n_benign:,} ({n_benign/tot_evaluated*100:.1f}%)")
    k3.metric("Anomalies Flagged", f"{n_attacks:,} ({n_attacks/tot_evaluated*100:.1f}%)")
    k4.metric("Critical Alerts", f"{n_critical:,}")
    
    st.markdown("### Classified Flow Telemetry")
    
    # Filter Controls
    f_col1, f_col2 = st.columns([1, 2])
    with f_col1:
        risk_filter = st.selectbox(
            "Filter by Risk Severity",
            options=["ALL", "CRITICAL", "SUSPICIOUS", "ELEVATED", "BENIGN"]
        )
    with f_col2:
        score_thresh = st.slider(
            "Minimum Anomaly Score Threshold",
            min_value=0.0, max_value=1.0, value=0.0, step=0.05
        )
        
    filtered_df = results_df.copy()
    if risk_filter != "ALL":
        filtered_df = filtered_df[filtered_df["Risk_Level"] == risk_filter]
    filtered_df = filtered_df[filtered_df["Anomaly_Score"] >= score_thresh]
    
    # Display columns
    summary_cols = [
        "Prediction", "Risk_Level", "Anomaly_Score",
        "Top_Contributing_Features"
    ]
    # Include Destination Port and Flow Duration if present
    for extra in ["Destination Port", "Flow Duration", "Flow Packets/s", "Total Fwd Packets", "Label"]:
        for col in filtered_df.columns:
            if extra.lower() == col.strip().lower() and col not in summary_cols:
                summary_cols.insert(0, col)
                break
                
    st.dataframe(
        filtered_df[summary_cols],
        width='stretch',
        column_config={
            "Anomaly_Score": st.column_config.ProgressColumn(
                "Anomaly Score", min_value=0.0, max_value=1.0, format="%.3f"
            )
        }
    )
    
    # Export options
    csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Classified Results to CSV",
        data=csv_bytes,
        file_name="threatlens_classified_flows.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # Detailed Flow Drilldown & Explainability
    st.subheader("🔬 Explainable AI: Flow Record Drilldown")
    selected_idx = st.selectbox(
        "Select Flow Index to Inspect Feature Attribution:",
        options=filtered_df.index.tolist()
    )
    
    if selected_idx is not None:
        flow_row = filtered_df.loc[selected_idx]
        
        d_col1, d_col2 = st.columns([1, 2])
        
        with d_col1:
            st.markdown(f"**Classification:** `{flow_row['Prediction']}` ({flow_row['Risk_Level']})")
            score_val = float(flow_row["Anomaly_Score"])
            
            # Anomaly Score Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score_val,
                title={"text": "Anomaly Score"},
                gauge={
                    "axis": {"range": [0, 1]},
                    "bar": {"color": "#da3633" if score_val >= 0.5 else "#238636"},
                    "steps": [
                        {"range": [0, 0.35], "color": "#161b22"},
                        {"range": [0.35, 0.70], "color": "#30363d"},
                        {"range": [0.70, 1.0], "color": "#490202"}
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": predictor.threshold
                    }
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="#161b22",
                font=dict(color="#e6edf3"),
                height=250,
                margin=dict(t=30, b=10, l=20, r=20)
            )
            st.plotly_chart(fig_gauge, width='stretch')
            
        with d_col2:
            st.markdown("#### Top Contributing Features (Gradient Saliency)")
            st.markdown(
                f"<div class='soc-card'><b>Feature Attribution:</b><br>{flow_row['Top_Contributing_Features']}</div>",
                unsafe_allow_html=True
            )
            
            # Security Analyst Triage Context
            dst_port = 80
            for col in flow_row.index:
                if "port" in col.lower():
                    dst_port = int(flow_row[col])
                    break
                    
            if score_val >= predictor.threshold:
                st.warning(
                    f"⚠️ **High-Risk Connection Alert:** Destination Port `{dst_port}` flagged with anomaly score "
                    f"`{score_val:.3f}`. The primary drivers are {flow_row['Top_Contributing_Features']}. "
                    "Recommend immediate inspection of endpoint connection state and firewall rule verification."
                )
            else:
                st.success(
                    f"✅ **Normal Connection Profile:** Traffic to Destination Port `{dst_port}` matches expected baseline characteristics."
                )
