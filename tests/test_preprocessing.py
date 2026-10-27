"""
Unit tests for ThreatLens AI data preprocessing and leakage prevention.
"""

import pytest
import numpy as np
import pandas as pd
from src.data_preprocessing import clean_column_names, identify_label_column, encode_labels, clean_features

def test_clean_column_names():
    df = pd.DataFrame({" Flow Duration ": [100], "  Total Fwd Packets": [5]})
    cleaned = clean_column_names(df)
    assert list(cleaned.columns) == ["Flow Duration", "Total Fwd Packets"]

def test_identify_label_column():
    df1 = pd.DataFrame({"Flow Duration": [100], "Label": ["BENIGN"]})
    assert identify_label_column(df1) == "Label"
    
    df2 = pd.DataFrame({"Flow Duration": [100], " class_label ": ["BENIGN"]})
    assert identify_label_column(df2) == " class_label "

def test_encode_labels():
    labels = pd.Series(["BENIGN", "DoS Hulk", "PortScan", "BENIGN", "FTP-Patator"])
    encoded, mapping = encode_labels(labels)
    assert encoded.tolist() == [0, 1, 1, 0, 1]
    assert mapping["BENIGN"] == 0
    assert mapping["ATTACK"] == 1

def test_clean_features_handles_infinities_and_nans():
    df = pd.DataFrame({
        "Flow Duration": [1000.0, np.nan, 3000.0],
        "Flow Packets/s": [50.0, np.inf, -np.inf],
        "Destination IP": ["192.168.1.1", "192.168.1.2", "192.168.1.3"]  # Leaky metadata
    })
    cleaned_df, medians = clean_features(df, is_training=True)
    
    # Check leaky column is dropped
    assert "Destination IP" not in cleaned_df.columns
    # Check no NaNs or Infs remain
    assert not cleaned_df.isna().any().any()
    assert not np.isinf(cleaned_df.values).any()
    # Check medians dictionary contains valid finite values
    assert "Flow Duration" in medians
    assert "Flow Packets/s" in medians
