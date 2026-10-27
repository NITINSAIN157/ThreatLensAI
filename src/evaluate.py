"""
ThreatLens AI - Model Evaluation Suite
Rigorous evaluation comparing PyTorch MLP vs Logistic Regression Baseline
on held-out test data across Precision, Recall, F1, ROC-AUC, PR-AUC, Confusion Matrix,
and CPU Inference Latency.
"""

import os
import sys
import json
import time
import joblib
from pathlib import Path

# Add project root to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
from typing import Dict, Any
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    average_precision_score, confusion_matrix, roc_curve, precision_recall_curve
)

from src.model import ThreatLensMLP

def benchmark_inference_latency(model, X_sample: np.ndarray, n_iterations: int = 100) -> Dict[str, float]:
    """Measures single sample latency and batch throughput on CPU."""
    # Warmup
    x_single = torch.tensor(X_sample[0:1], dtype=torch.float32)
    for _ in range(10):
        _ = model.predict_proba(x_single)
        
    start_time = time.perf_counter()
    for _ in range(n_iterations):
        _ = model.predict_proba(x_single)
    single_latency_ms = ((time.perf_counter() - start_time) / n_iterations) * 1000.0
    
    # Batch throughput
    x_batch = torch.tensor(X_sample, dtype=torch.float32)
    start_time = time.perf_counter()
    _ = model.predict_proba(x_batch)
    batch_time = time.perf_counter() - start_time
    throughput_samples_per_sec = len(X_sample) / max(batch_time, 1e-6)
    
    return {
        "single_sample_latency_ms": round(float(single_latency_ms), 4),
        "batch_throughput_samples_per_sec": round(float(throughput_samples_per_sec), 2)
    }

def evaluate_models(
    splits_path: str = "data/processed/splits.npz",
    models_dir: str = "models",
    output_path: str = "models/evaluation_results.json"
) -> Dict[str, Any]:
    print("=" * 70)
    print("ThreatLens AI: Comprehensive Model Evaluation (Held-Out Test Set)")
    print("=" * 70)
    
    # 1. Load test data
    data = np.load(splits_path)
    X_test, y_test = data["X_test"], data["y_test"]
    
    preprocessor = joblib.load(os.path.join(models_dir, "preprocessing.pkl"))
    feature_names = preprocessor["feature_names"]
    
    # 2. Load PyTorch MLP
    checkpoint = torch.load(os.path.join(models_dir, "mlp_model.pt"), weights_only=False)
    mlp_model = ThreatLensMLP(
        input_dim=checkpoint["input_dim"],
        hidden_dim1=checkpoint["hidden_dim1"],
        hidden_dim2=checkpoint["hidden_dim2"],
        dropout_rate=checkpoint["dropout_rate"]
    )
    mlp_model.load_state_dict(checkpoint["state_dict"])
    mlp_model.eval()
    threshold = checkpoint.get("optimal_threshold", 0.50)
    
    # 3. Load Baseline Logistic Regression
    baseline_path = os.path.join(models_dir, "baseline_logreg.pkl")
    baseline_model = joblib.load(baseline_path) if os.path.exists(baseline_path) else None
    
    # 4. PyTorch MLP Evaluation
    with torch.no_grad():
        mlp_probs = mlp_model.predict_proba(torch.tensor(X_test, dtype=torch.float32)).numpy().flatten()
    mlp_preds = (mlp_probs >= threshold).astype(int)
    
    mlp_cm = confusion_matrix(y_test, mlp_preds).tolist()
    tn, fp, fn, tp = confusion_matrix(y_test, mlp_preds).ravel()
    mlp_specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
    
    mlp_prec, mlp_rec, _ = precision_recall_curve(y_test, mlp_probs)
    mlp_fpr, mlp_tpr, _ = roc_curve(y_test, mlp_probs)
    
    mlp_latency = benchmark_inference_latency(mlp_model, X_test)
    
    mlp_results = {
        "model_name": "ThreatLens Deep MLP",
        "decision_threshold": float(threshold),
        "accuracy": float((tp + tn) / len(y_test)),
        "precision": float(precision_score(y_test, mlp_preds, zero_division=0)),
        "recall": float(recall_score(y_test, mlp_preds, zero_division=0)),
        "specificity": mlp_specificity,
        "f1_score": float(f1_score(y_test, mlp_preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, mlp_probs)),
        "pr_auc": float(average_precision_score(y_test, mlp_probs)),
        "confusion_matrix": {
            "matrix": mlp_cm,
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)
        },
        "latency": mlp_latency,
        "roc_curve": {
            "fpr": mlp_fpr[::max(1, len(mlp_fpr)//100)].tolist(),
            "tpr": mlp_tpr[::max(1, len(mlp_tpr)//100)].tolist()
        },
        "pr_curve": {
            "precision": mlp_prec[::max(1, len(mlp_prec)//100)].tolist(),
            "recall": mlp_rec[::max(1, len(mlp_rec)//100)].tolist()
        }
    }
    
    # 5. Baseline Evaluation
    baseline_results = None
    if baseline_model is not None:
        base_probs = baseline_model.predict_proba(X_test)[:, 1]
        base_preds = (base_probs >= 0.50).astype(int)
        
        base_cm = confusion_matrix(y_test, base_preds).tolist()
        btn, bfp, bfn, btp = confusion_matrix(y_test, base_preds).ravel()
        base_spec = float(btn / (btn + bfp)) if (btn + bfp) > 0 else 0.0
        
        base_prec, base_rec, _ = precision_recall_curve(y_test, base_probs)
        base_fpr, base_tpr, _ = roc_curve(y_test, base_probs)
        
        # Measure baseline latency
        start_t = time.perf_counter()
        for _ in range(100):
            _ = baseline_model.predict_proba(X_test[0:1])
        base_single_lat = ((time.perf_counter() - start_t) / 100) * 1000.0
        
        baseline_results = {
            "model_name": "Logistic Regression Baseline",
            "decision_threshold": 0.50,
            "accuracy": float((btp + btn) / len(y_test)),
            "precision": float(precision_score(y_test, base_preds, zero_division=0)),
            "recall": float(recall_score(y_test, base_preds, zero_division=0)),
            "specificity": base_spec,
            "f1_score": float(f1_score(y_test, base_preds, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, base_probs)),
            "pr_auc": float(average_precision_score(y_test, base_probs)),
            "confusion_matrix": {
                "matrix": base_cm,
                "tn": int(btn), "fp": int(bfp), "fn": int(bfn), "tp": int(btp)
            },
            "latency": {
                "single_sample_latency_ms": round(float(base_single_lat), 4)
            },
            "roc_curve": {
                "fpr": base_fpr[::max(1, len(base_fpr)//100)].tolist(),
                "tpr": base_tpr[::max(1, len(base_tpr)//100)].tolist()
            },
            "pr_curve": {
                "precision": base_prec[::max(1, len(base_prec)//100)].tolist(),
                "recall": base_rec[::max(1, len(base_rec)//100)].tolist()
            }
        }
        
    evaluation_payload = {
        "dataset_name": "CIC-IDS2017 Held-out Test Split",
        "test_samples": int(len(y_test)),
        "attack_prevalence": float(y_test.mean()),
        "deep_learning_mlp": mlp_results,
        "baseline_logistic_regression": baseline_results
    }
    
    with open(output_path, "w") as f:
        json.dump(evaluation_payload, f, indent=2)
        
    print(f"\nEvaluation Summary on {len(y_test)} Held-Out Test Records:")
    print("-" * 65)
    print(f"{'Metric':<20} | {'PyTorch MLP':<18} | {'Baseline (LogReg)':<18}")
    print("-" * 65)
    print(f"{'Precision':<20} | {mlp_results['precision']:<18.4f} | {baseline_results['precision']:<18.4f}")
    print(f"{'Recall':<20} | {mlp_results['recall']:<18.4f} | {baseline_results['recall']:<18.4f}")
    print(f"{'F1-Score':<20} | {mlp_results['f1_score']:<18.4f} | {baseline_results['f1_score']:<18.4f}")
    print(f"{'ROC-AUC':<20} | {mlp_results['roc_auc']:<18.4f} | {baseline_results['roc_auc']:<18.4f}")
    print(f"{'PR-AUC':<20} | {mlp_results['pr_auc']:<18.4f} | {baseline_results['pr_auc']:<18.4f}")
    print(f"{'Single Latency (ms)':<20} | {mlp_results['latency']['single_sample_latency_ms']:<18.4f} | {baseline_results['latency']['single_sample_latency_ms']:<18.4f}")
    print("-" * 65)
    print(f"Results saved to: {output_path}")
    
    return evaluation_payload

if __name__ == "__main__":
    evaluate_models()
