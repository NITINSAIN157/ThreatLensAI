"""
ThreatLens AI - PyTorch Deep Learning Classifier & Explainability Engine
Multi-Layer Perceptron (MLP) for Network Intrusion Detection with Feature Saliency.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any, Tuple

class ThreatLensMLP(nn.Module):
    """
    Deep Learning Multi-Layer Perceptron (MLP) for binary network flow classification.
    
    Architecture:
    Input Layer (D features) -> Dense(64) -> BatchNorm1d -> ReLU -> Dropout(0.2)
                            -> Dense(32) -> BatchNorm1d -> ReLU -> Dropout(0.2)
                            -> Dense(1)  -> Raw Logits
    """
    def __init__(self, input_dim: int, hidden_dim1: int = 64, hidden_dim2: int = 32, dropout_rate: float = 0.2):
        super(ThreatLensMLP, self).__init__()
        self.input_dim = input_dim
        
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim1),
            nn.BatchNorm1d(hidden_dim1),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_dim1, hidden_dim2),
            nn.BatchNorm1d(hidden_dim2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            
            nn.Linear(hidden_dim2, 1)
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass returning unnormalized logits (shape: [batch_size, 1])."""
        return self.network(x)
        
    def predict_proba(self, x: torch.Tensor) -> torch.Tensor:
        """Returns anomaly probabilities in range [0, 1] using Sigmoid activation."""
        self.eval()
        with torch.no_grad():
            logits = self.forward(x)
            return torch.sigmoid(logits)

    def explain_flow(self, x_single: torch.Tensor, feature_names: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Explainability via Input * Gradient attribution saliency.
        Identifies which features most significantly pushed the prediction toward 'Attack'.
        """
        self.eval()
        if x_single.ndim == 1:
            x_single = x_single.unsqueeze(0)
            
        x_tensor = x_single.clone().detach().requires_grad_(True)
        
        # Forward pass
        logit = self.forward(x_tensor)
        
        # Calculate gradients with respect to leaf input tensor
        self.zero_grad()
        logit.backward()
        
        # Saliency score: Input * Gradient (signifies direct contribution to the positive class logit)
        grad = x_tensor.grad.squeeze(0)
        saliency = (grad * x_tensor.squeeze(0)).detach().cpu().numpy()
        
        # Rank by contribution magnitude
        top_indices = np.argsort(saliency)[::-1][:top_k]
        
        explanations = []
        for idx in top_indices:
            explanations.append({
                "feature": feature_names[idx],
                "attribution_score": float(saliency[idx]),
                "normalized_value": float(x_tensor.squeeze(0)[idx].item())
            })
            
        return explanations
