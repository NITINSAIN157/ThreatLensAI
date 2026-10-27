"""
Unit tests for ThreatLens AI PyTorch inference and explainability.
"""

import pytest
import numpy as np
import pandas as pd
import torch
from src.predict import ThreatLensPredictor

@pytest.fixture(scope="module")
def predictor():
    return ThreatLensPredictor(models_dir="models")

def test_predictor_initialization(predictor):
    assert predictor.model is not None
    assert predictor.scaler is not None
    assert len(predictor.feature_names) > 0
    assert 0.0 <= predictor.threshold <= 1.0

def test_predictor_batch_inference(predictor):
    # Load test batch sample
    df_sample = pd.read_csv("data/raw/cicids2017_test_batch.csv").head(10)
    results = predictor.predict_dataframe(df_sample)
    
    assert "Anomaly_Score" in results.columns
    assert "Prediction" in results.columns
    assert "Risk_Level" in results.columns
    assert "Top_Contributing_Features" in results.columns
    
    # Check probability bounds
    scores = results["Anomaly_Score"].values
    assert (scores >= 0.0).all() and (scores <= 1.0).all()
    assert set(results["Prediction"].unique()).issubset({"BENIGN", "ATTACK"})

def test_inference_with_missing_columns(predictor):
    # Simulates user uploading CSV with missing non-essential columns
    df_partial = pd.DataFrame({
        "Flow Duration": [500000.0, 100.0],
        "Total Fwd Packets": [10, 2],
        "Flow Packets/s": [20.0, 20000.0]
    })
    results = predictor.predict_dataframe(df_partial)
    assert len(results) == 2
    assert "Anomaly_Score" in results.columns
