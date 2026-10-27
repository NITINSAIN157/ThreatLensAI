"""
ThreatLens AI - Inference & Explainability Engine
Loads saved PyTorch MLP model and preprocessing artifacts to perform live batch
or single-flow predictions with feature attribution explanations.
"""

import os
import sys
import joblib
from pathlib import Path

# Add project root to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import torch
from typing import Dict, Any, List, Optional, Tuple

from src.model import ThreatLensMLP
from src.data_preprocessing import clean_column_names, clean_features

class ThreatLensPredictor:
    """Production-grade inference engine for ThreatLens AI."""
    
    def __init__(self, models_dir: str = "models", device: str = "cpu"):
        self.device = torch.device(device)
        self.models_dir = Path(models_dir)
        
        # Load preprocessing artifacts
        preproc_path = self.models_dir / "preprocessing.pkl"
        if not preproc_path.exists():
            raise FileNotFoundError(f"Preprocessing artifact not found at {preproc_path}. Run training first.")
        self.preprocessor = joblib.load(preproc_path)
        self.scaler = self.preprocessor["scaler"]
        self.feature_names = self.preprocessor["feature_names"]
        self.imputer_medians = self.preprocessor["imputer_medians"]
        
        # Load PyTorch MLP
        model_path = self.models_dir / "mlp_model.pt"
        if not model_path.exists():
            raise FileNotFoundError(f"Trained model not found at {model_path}. Run training first.")
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
        
        self.model = ThreatLensMLP(
            input_dim=checkpoint["input_dim"],
            hidden_dim1=checkpoint["hidden_dim1"],
            hidden_dim2=checkpoint["hidden_dim2"],
            dropout_rate=checkpoint["dropout_rate"]
        )
        self.model.load_state_dict(checkpoint["state_dict"])
        self.model.to(self.device)
        self.model.eval()
        
        self.threshold = checkpoint.get("optimal_threshold", 0.50)

    def preprocess_input(self, df: pd.DataFrame) -> Tuple[np.ndarray, pd.DataFrame]:
        """Aligns, cleans, and scales input dataframe to exact training schema."""
        df_clean = clean_column_names(df)
        
        # Check if ground truth label is present; if so, preserve it for analysis
        label_col = None
        for col in df_clean.columns:
            if "label" in col.lower():
                label_col = col
                break
        ground_truth = df_clean[label_col].values if label_col else None
        if label_col:
            df_features = df_clean.drop(columns=[label_col])
        else:
            df_features = df_clean
            
        # Clean features with training medians and aligned feature order
        cleaned_df, _ = clean_features(
            df_features,
            is_training=False,
            imputer_medians=self.imputer_medians,
            expected_features=self.feature_names
        )
        
        # Scale features
        scaled_array = self.scaler.transform(cleaned_df[self.feature_names])
        return scaled_array, df_clean

    def predict_dataframe(self, df: pd.DataFrame, top_k_explanations: int = 3) -> pd.DataFrame:
        """
        Runs full inference on a DataFrame of flow records.
        Returns original data augmented with ThreatLens AI classification,
        anomaly score, risk level, and top contributing features.
        """
        scaled_features, original_df = self.preprocess_input(df)
        tensor_x = torch.tensor(scaled_features, dtype=torch.float32, device=self.device)
        
        with torch.no_grad():
            probs = self.model.predict_proba(tensor_x).cpu().numpy().flatten()
            
        preds = (probs >= self.threshold).astype(int)
        
        # Determine risk severity
        risk_levels = []
        for p in probs:
            if p >= 0.70:
                risk_levels.append("CRITICAL")
            elif p >= self.threshold:
                risk_levels.append("SUSPICIOUS")
            elif p >= 0.30:
                risk_levels.append("ELEVATED")
            else:
                risk_levels.append("BENIGN")
                
        # Generate explanations for flagged / suspicious records
        explanations = []
        for i in range(len(scaled_features)):
            if probs[i] >= (self.threshold - 0.15):  # Explain any border or suspicious flow
                exp = self.model.explain_flow(tensor_x[i], self.feature_names, top_k=top_k_explanations)
                exp_str = ", ".join([f"{e['feature']} ({e['attribution_score']:.2f})" for e in exp])
                explanations.append(exp_str)
            else:
                explanations.append("Traffic matches standard baseline profile")
                
        results_df = original_df.copy()
        results_df["Anomaly_Score"] = np.round(probs, 4)
        results_df["Prediction"] = np.where(preds == 1, "ATTACK", "BENIGN")
        results_df["Risk_Level"] = risk_levels
        results_df["Top_Contributing_Features"] = explanations
        
        return results_df
