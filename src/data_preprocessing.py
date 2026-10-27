"""
ThreatLens AI - Data Preprocessing Pipeline
Handles cleaning, leakage prevention, standardization, stratified splitting,
and artifact serialization for the CIC-IDS2017 network flow dataset.
"""

import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, Any, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Columns that represent metadata or identifiers that cause target leakage
LEAKY_COLUMNS = [
    "flow id", "source ip", "src ip", "destination ip", "dst ip",
    "timestamp", "simillarhttp"
]

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Strips leading and trailing whitespace from column names."""
    df = df.copy()
    df.columns = [col.strip() for col in df.columns]
    return df

def identify_label_column(df: pd.DataFrame) -> str:
    """Identifies the target label column regardless of casing."""
    for col in df.columns:
        if col.strip().lower() == "label":
            return col
    for col in df.columns:
        if "label" in col.strip().lower():
            return col
    raise ValueError("No 'Label' column found in dataset.")

def encode_labels(labels: pd.Series) -> Tuple[pd.Series, Dict[str, int]]:
    """
    Encodes network flow labels into binary classification:
    0: Benign
    1: Attack / Malicious activity
    """
    is_benign = labels.astype(str).str.strip().str.upper() == "BENIGN"
    binary_labels = (~is_benign).astype(int)
    mapping = {"BENIGN": 0, "ATTACK": 1}
    return binary_labels, mapping

def clean_features(df: pd.DataFrame, is_training: bool = True, 
                   imputer_medians: Dict[str, float] = None,
                   expected_features: List[str] = None) -> Tuple[pd.DataFrame, Dict[str, float]]:
    """
    Cleans infinite values, replaces NaNs with column medians, and removes leaky metadata.
    """
    df = df.copy()
    
    # 1. Drop leaky metadata columns if present
    cols_to_drop = [c for c in df.columns if c.lower() in LEAKY_COLUMNS]
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        
    # 2. Convert all remaining feature columns to numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # 3. Replace inf and -inf with NaN
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # 4. Impute missing values with medians
    if is_training:
        medians = df.median().to_dict()
        # Fallback for any column that was completely NaN
        for col, val in medians.items():
            if np.isnan(val):
                medians[col] = 0.0
        df = df.fillna(medians)
        return df, medians
    else:
        if imputer_medians is None:
            raise ValueError("imputer_medians must be provided during inference cleaning.")
        # Align features to expected features if specified
        if expected_features is not None:
            for feat in expected_features:
                if feat not in df.columns:
                    df[feat] = imputer_medians.get(feat, 0.0)
            df = df[expected_features]
            
        df = df.fillna(imputer_medians)
        # Final safety check for any remaining NaN
        df = df.fillna(0.0)
        return df, imputer_medians

def preprocess_and_split(
    csv_path: str,
    output_dir: str = "models",
    processed_data_dir: str = "data/processed",
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42
) -> Dict[str, Any]:
    """
    Loads raw CSV, cleans features, fits StandardScaler on train set only,
    generates stratified splits, and saves preprocessing artifacts.
    """
    print(f"Loading raw network flow data from: {csv_path}...")
    df = pd.read_csv(csv_path)
    df = clean_column_names(df)
    
    label_col = identify_label_column(df)
    y_raw = df[label_col]
    y_binary, label_mapping = encode_labels(y_raw)
    
    # Separate features
    X_raw = df.drop(columns=[label_col])
    
    # Initial train/temp split (Stratified)
    total_temp_size = test_size + val_size
    X_train_raw, X_temp_raw, y_train, y_temp = train_test_split(
        X_raw, y_binary, test_size=total_temp_size, random_state=random_state, stratify=y_binary
    )
    
    # Split temp into val and test sets (Stratified)
    val_ratio = val_size / total_temp_size
    X_val_raw, X_test_raw, y_val, y_test = train_test_split(
        X_temp_raw, y_temp, test_size=(1.0 - val_ratio), random_state=random_state, stratify=y_temp
    )
    
    # Clean training features and calculate medians
    X_train_cleaned, imputer_medians = clean_features(X_train_raw, is_training=True)
    
    # Drop constant (zero variance) features on training data
    variances = X_train_cleaned.var()
    constant_cols = variances[variances == 0].index.tolist()
    if constant_cols:
        print(f"Dropping {len(constant_cols)} zero-variance columns: {constant_cols[:5]}...")
        X_train_cleaned = X_train_cleaned.drop(columns=constant_cols)
        for col in constant_cols:
            imputer_medians.pop(col, None)
            
    feature_names = list(X_train_cleaned.columns)
    
    # Clean val and test features using training statistics
    X_val_cleaned, _ = clean_features(
        X_val_raw, is_training=False, imputer_medians=imputer_medians, expected_features=feature_names
    )
    X_test_cleaned, _ = clean_features(
        X_test_raw, is_training=False, imputer_medians=imputer_medians, expected_features=feature_names
    )
    
    # Fit StandardScaler strictly on X_train
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_cleaned)
    X_val_scaled = scaler.transform(X_val_cleaned)
    X_test_scaled = scaler.transform(X_test_cleaned)
    
    # Package preprocessing artifact
    preprocessor = {
        "scaler": scaler,
        "feature_names": feature_names,
        "imputer_medians": imputer_medians,
        "dropped_constant_columns": constant_cols,
        "label_mapping": label_mapping,
        "n_features": len(feature_names)
    }
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path(processed_data_dir).mkdir(parents=True, exist_ok=True)
    
    artifact_path = os.path.join(output_dir, "preprocessing.pkl")
    joblib.dump(preprocessor, artifact_path)
    print(f"Preprocessing artifact saved to: {artifact_path}")
    
    # Save processed numpy arrays for fast reproducible loading
    np.savez_compressed(
        os.path.join(processed_data_dir, "splits.npz"),
        X_train=X_train_scaled, y_train=y_train.values,
        X_val=X_val_scaled, y_val=y_val.values,
        X_test=X_test_scaled, y_test=y_test.values
    )
    print(f"Processed splits saved to {processed_data_dir}/splits.npz")
    print(f"Dataset summary: Train={len(y_train)}, Val={len(y_val)}, Test={len(y_test)} | Features={len(feature_names)}")
    print(f"Attack ratio: Train={y_train.mean():.3f}, Val={y_val.mean():.3f}, Test={y_test.mean():.3f}")
    
    return {
        "X_train": X_train_scaled, "y_train": y_train.values,
        "X_val": X_val_scaled, "y_val": y_val.values,
        "X_test": X_test_scaled, "y_test": y_test.values,
        "preprocessor": preprocessor,
        "feature_names": feature_names
    }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ThreatLens Preprocessing Pipeline")
    parser.add_argument("--csv", type=str, default="data/raw/cicids2017_sample.csv", help="Path to input raw CSV")
    args = parser.parse_args()
    preprocess_and_split(args.csv)
