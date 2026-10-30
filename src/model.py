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
        Explainability via weight-based saliency attribution (autograd-free, production-stable).
        
        Computes: saliency[j] = mean_over_neurons(|W1[n,j]|) * |x[j]|
        where W1 is the first Linear layer weight matrix.
        This measures how strongly each input feature is amplified by the first layer,
        weighted by the magnitude of the feature value itself — a fast, stable proxy
        for gradient saliency that avoids BatchNorm1d autograd conflicts entirely.
        
        Identifies which features most significantly contributed to the anomaly decision.
        """
        self.eval()
        with torch.no_grad():
            # Flatten to 1-D feature vector
            x_val = x_single.squeeze(0) if x_single.ndim > 1 else x_single

            # First Linear layer weight: shape [hidden_dim1, input_dim]
            W1 = self.network[0].weight  # nn.Linear is network[0]

            # Mean absolute weight per input feature (how much each feature is used)
            mean_abs_weight = W1.abs().mean(dim=0)  # shape [input_dim]

            # Weight by absolute feature value so large activations score higher
            saliency = (mean_abs_weight * x_val.abs()).cpu().numpy()

        top_indices = np.argsort(saliency)[::-1][:top_k]

        return [
            {
                "feature": feature_names[idx],
                "attribution_score": float(saliency[idx]),
                "normalized_value": float(x_val[idx].item())
            }
            for idx in top_indices
        ]
