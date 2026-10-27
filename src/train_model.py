"""
ThreatLens AI - Model Training Pipeline
Trains the PyTorch MLP and Logistic Regression baseline on CIC-IDS2017 splits.
Includes class weighting, early stopping, LR scheduling, and validation threshold tuning.
"""

import os
import sys
import json
import joblib
from pathlib import Path

# Add project root to path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_recall_curve

from src.model import ThreatLensMLP

def train_pipeline(
    splits_path: str = "data/processed/splits.npz",
    preprocessor_path: str = "models/preprocessing.pkl",
    output_dir: str = "models",
    epochs: int = 25,
    batch_size: int = 256,
    learning_rate: float = 0.002,
    patience: int = 5
):
    print("=" * 70)
    print("ThreatLens AI: Deep Learning Training Pipeline")
    print("=" * 70)
    
    # 1. Load data
    data = np.load(splits_path)
    X_train, y_train = data["X_train"], data["y_train"]
    X_val, y_val = data["X_val"], data["y_val"]
    X_test, y_test = data["X_test"], data["y_test"]
    
    preprocessor = joblib.load(preprocessor_path)
    feature_names = preprocessor["feature_names"]
    input_dim = len(feature_names)
    
    print(f"Loaded datasets: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
    print(f"Features count: {input_dim}")
    
    # Calculate class imbalance pos_weight
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    pos_weight = float(n_neg / max(n_pos, 1))
    print(f"Class imbalance: Benign={n_neg}, Attack={n_pos} | Loss pos_weight={pos_weight:.2f}")
    
    # Convert to PyTorch Tensors
    train_dataset = TensorDataset(
        torch.tensor(X_train, dtype=torch.float32),
        torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    )
    val_dataset = TensorDataset(
        torch.tensor(X_val, dtype=torch.float32),
        torch.tensor(y_val, dtype=torch.float32).unsqueeze(1)
    )
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 2. Initialize Neural Network
    model = ThreatLensMLP(input_dim=input_dim, hidden_dim1=64, hidden_dim2=32, dropout_rate=0.2)
    criterion = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight]))
    optimizer = optim.Adam(model.parameters(), lr=learning_rate, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=2)
    
    # 3. Training Loop with Early Stopping
    best_val_loss = float("inf")
    best_weights = None
    epochs_no_improve = 0
    history = {"train_loss": [], "val_loss": [], "val_f1": []}
    
    print("\nStarting PyTorch MLP Training...")
    for epoch in range(1, epochs + 1):
        model.train()
        train_loss = 0.0
        
        for batch_x, batch_y in train_loader:
            optimizer.zero_grad()
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            train_loss += loss.item() * len(batch_x)
            
        train_loss /= len(train_dataset)
        
        # Validation evaluation
        model.eval()
        val_loss = 0.0
        val_preds, val_targets = [], []
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                logits = model(batch_x)
                loss = criterion(logits, batch_y)
                val_loss += loss.item() * len(batch_x)
                probs = torch.sigmoid(logits)
                val_preds.extend(probs.cpu().numpy().flatten())
                val_targets.extend(batch_y.cpu().numpy().flatten())
                
        val_loss /= len(val_dataset)
        val_preds = np.array(val_preds)
        val_targets = np.array(val_targets)
        val_f1 = f1_score(val_targets, (val_preds >= 0.5).astype(int), zero_division=0)
        
        scheduler.step(val_loss)
        
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["val_f1"].append(float(val_f1))
        
        print(f"Epoch {epoch:02d}/{epochs:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val F1: {val_f1:.4f}")
        
        # Early stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_weights = model.state_dict().copy()
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered after {epoch} epochs (Patience={patience}).")
                break
                
    # Restore best weights
    model.load_state_dict(best_weights)
    
    # 4. Tune Decision Threshold on Validation Set (Strictly NEVER on Test Set)
    model.eval()
    with torch.no_grad():
        val_probs = model.predict_proba(torch.tensor(X_val, dtype=torch.float32)).numpy().flatten()
        
    threshold_candidates = np.linspace(0.1, 0.9, 81)
    best_threshold = 0.50
    best_thresh_f1 = 0.0
    
    for th in threshold_candidates:
        score = f1_score(y_val, (val_probs >= th).astype(int), zero_division=0)
        if score > best_thresh_f1:
            best_thresh_f1 = score
            best_threshold = float(th)
            
    print(f"\nOptimal Validation Decision Threshold: {best_threshold:.2f} (Val F1: {best_thresh_f1:.4f})")
    
    # 5. Save PyTorch Model Artifacts
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    model_save_path = output_path / "mlp_model.pt"
    torch.save({
        "state_dict": model.state_dict(),
        "input_dim": input_dim,
        "hidden_dim1": 64,
        "hidden_dim2": 32,
        "dropout_rate": 0.2,
        "optimal_threshold": best_threshold
    }, model_save_path)
    print(f"PyTorch model saved to: {model_save_path}")
    
    # 6. Train Baseline Model (Logistic Regression)
    print("\nTraining Baseline Model (Logistic Regression)...")
    baseline = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
    baseline.fit(X_train, y_train)
    baseline_save_path = output_path / "baseline_logreg.pkl"
    joblib.dump(baseline, baseline_save_path)
    print(f"Baseline Logistic Regression saved to: {baseline_save_path}")
    
    # Save training configuration
    config = {
        "input_dim": input_dim,
        "batch_size": batch_size,
        "epochs_trained": len(history["train_loss"]),
        "best_val_loss": float(best_val_loss),
        "optimal_threshold": float(best_threshold),
        "history": history
    }
    with open(output_path / "model_config.json", "w") as f:
        json.dump(config, f, indent=2)
        
    print("\nTraining complete! Proceed to evaluation.")
    return model, baseline, config

if __name__ == "__main__":
    train_pipeline()
