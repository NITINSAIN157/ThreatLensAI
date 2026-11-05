# ThreatLens AI — Explainable Deep Learning Network Intrusion Detection

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PyTorch-2.2+-ee4c2c.svg" alt="PyTorch">
  <img src="https://img.shields.io/badge/Dataset-CIC--IDS2017-orange.svg" alt="Dataset">
  <img src="https://img.shields.io/badge/Frontend-Streamlit-ff4b4b.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Tests-Passing%20(100%25)-brightgreen.svg" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
</p>

---

## 📌 Executive Summary

**ThreatLens AI** is an academic-grade Deep Learning project for **Network Intrusion Detection (NIDS)** combined with **Explainable Artificial Intelligence (XAI)**.

Traditional deep learning models in cybersecurity operate as black boxes: they output a probability score indicating that network traffic is malicious, but fail to explain *which* underlying network flow features triggered the detection. 

ThreatLens AI addresses this challenge with two core innovations:
1. 🛡️ **Deep Learning Detection Core**: A PyTorch Multi-Layer Perceptron (MLP) trained on the benchmark **CIC-IDS2017** dataset to classify network flows as benign or malicious, rigorously benchmarked against a Logistic Regression baseline.
2. 🔬 **Explainable AI (XAI) Attribution**: Mathematical gradient saliency attribution ($\text{Attribution}_i = x_i \cdot \frac{\partial \mathcal{L}}{\partial x_i}$) that pinpoints the exact physical connection features (packet rate, SYN flags, connection duration) driving each prediction.
3. 🖥️ **Interactive Security Operations Dashboard**: A multi-page Streamlit SOC tool allowing live CSV batch uploads, real-time PyTorch inference, interactive Plotly confusion matrices, ROC/PR curves, and flow-by-flow drilldowns.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph DataPipeline["1. Data Ingestion & Preprocessing"]
        A[CIC-IDS2017 Flow Data] --> B[Clean NaNs, Infs, Duplicates]
        B --> C[Drop Leaky Identifiers: IP, Timestamp, FlowID]
        C --> D[Stratified Train/Val/Test Split: 70/15/15]
        D --> E[StandardScaler Fitted Strictly on Train]
        E --> F[models/preprocessing.pkl]
    end

    subgraph DeepLearning["2. PyTorch Deep Learning & Baseline"]
        D --> G[PyTorch MLP Architecture]
        D --> H[Logistic Regression Baseline]
        G --> I[Adam + Weighted BCE Loss + Early Stopping]
        I --> J[Validation Threshold Optimization]
        J --> K[models/mlp_model.pt]
        K --> L[Comprehensive Evaluation & Latency Benchmark]
    end

    subgraph Explainability["3. Explainable AI Saliency"]
        K --> M[Input * Gradient Saliency Engine]
        M --> N[Per-Flow Top-Contributing Features]
    end

    subgraph SOCDashboard["4. Streamlit SOC Multi-Page Interface"]
        K & F --> W1[Page 2: Traffic Analysis & Live CSV Inference]
        L --> W2[Page 3: Model Evaluation & Academic Benchmark]
        W1 & W2 --> W0[Page 1: Security Operations Overview]
    end
```

---

## 📊 Dataset: CIC-IDS2017 Benchmark

ThreatLens uses the **CIC-IDS2017** benchmark dataset provided by the [Canadian Institute for Cybersecurity (UNB)](https://www.unb.ca/cic/datasets/ids-2017.html).

### Network Flow Schema
Instead of raw, unmanageable packet captures (PCAPs), the dataset extracts bidirectional flow statistics over connection windows:
| Feature Category | Examples | Diagnostic Relevance |
| :--- | :--- | :--- |
| **Duration & Rates** | `Flow Duration`, `Flow Packets/s`, `Flow Bytes/s` | Volumetric DoS floods and short-duration port scanning probes |
| **Directionality** | `Total Fwd Packets`, `Total Backward Packets` | Unidirectional flows ($Bwd=0$) signify half-open reconnaissance or unanswered requests |
| **Packet Statistics** | `Fwd Packet Length Mean`, `Bwd Packet Length Mean` | Small packet flooding (0-64 bytes) vs. legitimate application data transfers |
| **TCP Flags** | `SYN Flag Count`, `RST Flag Count`, `ACK Flag Count` | TCP handshake anomalies, SYN floods, closed-port resets |
| **Timing Intervals** | `Flow IAT Mean`, `Flow IAT Std`, `Active/Idle` | Automated bot scripting (uniform low variance) vs. human traffic (high variance) |

### Leakage Prevention & Preprocessing
To maintain academic rigor:
- **No Target Leakage**: Identifiers (`Flow ID`, `Source IP`, `Destination IP`, `Timestamp`) are explicitly stripped.
- **Isolated Normalization**: The `StandardScaler` is fitted **strictly on the training split** and persisted in `models/preprocessing.pkl`.
- **Zero-Variance Filtering**: Constant features across the training set are dropped to prevent numerical instability.
- **No Test Peeking**: Optimal decision thresholds are determined strictly on the validation set.

---

## 🧠 Deep Learning Model Architecture

### Neural Network Specification
The classifier is implemented in PyTorch (`src/model.py`) as a supervised Multi-Layer Perceptron (MLP):

$$\hat{y} = \sigma\left(\mathbf{W}_3 \cdot \text{Dropout}\left(\text{ReLU}\left(\text{BN}\left(\mathbf{W}_2 \cdot \text{Dropout}\left(\text{ReLU}\left(\text{BN}\left(\mathbf{W}_1 \mathbf{x} + \mathbf{b}_1\right)\right)\right) + \mathbf{b}_2\right)\right)\right) + b_3\right)$$

- **Input Layer**: $D = 59$ preprocessed numeric flow features.
- **Hidden Layer 1**: 64 neurons, Batch Normalization, ReLU activation, Dropout ($p = 0.2$).
- **Hidden Layer 2**: 32 neurons, Batch Normalization, ReLU activation, Dropout ($p = 0.2$).
- **Output Layer**: 1 linear logit evaluated with numerically stable `BCEWithLogitsLoss`.

### Class Imbalance Handling
Because normal benign connections vastly outnumber attack attempts in realistic traffic, ThreatLens calculates dynamic positive weighting:

$$\mathcal{L} = -\left[ w_{\text{pos}} \cdot y \log \sigma(z) + (1 - y) \log (1 - \sigma(z)) \right], \quad \text{where } w_{\text{pos}} = \frac{N_{\text{benign}}}{N_{\text{attack}}}$$

---

## 📈 Evaluation Results (Held-Out Test Set)

Evaluated on 900 held-out test flow records strictly isolated from model training:

| Evaluation Metric | PyTorch Deep MLP | Logistic Regression Baseline | Note |
| :--- | :---: | :---: | :--- |
| **Precision** | **1.0000** | 1.0000 | Zero false positives on held-out split |
| **Recall** | **1.0000** | 1.0000 | 100% detection of attack categories |
| **F1-Score** | **1.0000** | 1.0000 | Harmonic mean of precision and recall |
| **ROC-AUC** | **1.0000** | 1.0000 | Area under Receiver Operating Characteristic |
| **PR-AUC** | **1.0000** | 1.0000 | Area under Precision-Recall Curve |
| **Single Inference Latency** | **0.51 ms** | 0.26 ms | Real-time CPU throughput (> 1,900 flows/sec) |

> [!NOTE]
> All metrics and confusion matrix coordinates are dynamically benchmarked and stored in `models/evaluation_results.json`.

---

## 🔬 Explainable AI (XAI) Saliency Engine

Rather than displaying an uninformative raw probability score, ThreatLens computes gradient-based input saliency:

$$\text{Attribution}_i = x_i \cdot \frac{\partial \mathcal{L}}{\partial x_i}$$

For every flagged flow, the top contributing features are extracted (e.g., `Flow Packets/s`, `SYN Flag Count`, `Total Bwd Packets = 0`). This allows analysts to immediately understand the root physical connection anomaly.

---

## 📂 Project Structure

```
ThreatLens-AI/
├── app.py                     # Main Streamlit SOC operations hub
├── run_app.bat                # Windows 1-click launcher script
├── requirements.txt           # Project dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Version control exclusions
├── README.md                  # Comprehensive academic & technical guide
├── LICENSE                    # MIT License
├── data/
│   ├── raw/                   # Raw CIC-IDS2017 benchmark CSV files
│   │   ├── cicids2017_sample.csv
│   │   └── cicids2017_test_batch.csv
│   └── processed/             # Cleaned numpy splits (splits.npz)
├── models/
│   ├── mlp_model.pt           # PyTorch trained model weights & metadata
│   ├── preprocessing.pkl      # Scaler, imputer medians, and feature order
│   ├── baseline_logreg.pkl    # Baseline Logistic Regression model
│   ├── model_config.json      # Training configuration & history
│   └── evaluation_results.json# Benchmarked metrics & curve points
├── src/
│   ├── __init__.py
│   ├── model.py               # PyTorch MLP architecture & XAI saliency
│   ├── data_preprocessing.py  # Cleaning, leakage prevention, splitting
│   ├── train_model.py         # PyTorch training loop & baseline fit
│   ├── predict.py             # Inference engine & batch CSV prediction
│   └── evaluate.py            # Academic evaluation suite
├── pages/
│   ├── 1_Overview.py          # SOC telemetry & threat distribution
│   ├── 2_Traffic_Analysis.py  # CSV upload, live inference, and drilldown
│   └── 3_Model_Evaluation.py  # Comparative benchmark & Viva defense
├── scripts/
│   ├── download_dataset.py    # Official CIC-IDS2017 acquisition script
│   ├── generate_sample_data.py# Benchmark subset generator
│   └── create_test_batch.py   # Test batch generator
└── tests/
    ├── __init__.py
    ├── test_preprocessing.py  # Preprocessing & leakage tests
    └── test_prediction.py     # Inference & shape tests
```

---

## 🚀 Quickstart Guide

### 1. Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Automated Tests
Verify that all unit and integration tests pass:
```bash
pytest tests/ -v
```

### 3. Launch the Streamlit SOC Dashboard
```bash
python -m streamlit run app.py
```
*(On Windows, you can also simply double-click `run_app.bat`)*

Open your browser at `http://localhost:8501`.

---


## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
