# Task P6-1: Self-Attention from Scratch + Visualization

**Goal:** Implement scaled dot-product attention from scratch and build intuition for what the attention weights actually mean.

Create a Jupyter Notebook in `homework/lab-files/`.

---

## Step 1: Implement the Core Function

Implement `scaled_dot_product_attention` without copying from the concept notes. The signature is:

```python
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q: (batch, seq_len_q, d_k)
    K: (batch, seq_len_k, d_k)
    V: (batch, seq_len_k, d_v)
    mask: (seq_len_q, seq_len_k) — 1=attend, 0=block
    
    Returns: output (batch, seq_len_q, d_v), weights (batch, seq_len_q, seq_len_k)
    """
    d_k = Q.size(-1)
    
    # 1. Compute raw scores: how similar is each query to each key?
    scores = ...  # shape: (batch, seq_len_q, seq_len_k)
    
    # 2. Scale by sqrt(d_k)
    scores = ...
    
    # 3. If mask provided, fill masked positions with -inf
    if mask is not None:
        scores = ...
    
    # 4. Softmax over the key dimension
    weights = ...
    
    # 5. Weighted sum of values
    output = ...
    
    return output, weights
```

Test it:
```python
Q = torch.randn(1, 4, 8)
K = torch.randn(1, 4, 8)
V = torch.randn(1, 4, 8)

out, w = scaled_dot_product_attention(Q, K, V)
print(f"Output:  {out.shape}")   # (1, 4, 8)
print(f"Weights: {w.shape}")     # (1, 4, 4)

# Each row of weights must sum to 1 (it's a probability distribution)
print("Row sums (must all be 1.0):", w[0].sum(dim=-1).tolist())
```

## Step 2: Visualize Attention Weights

Create a scenario where you manually set Q and K such that one query is clearly more similar to one key than others. Visualize the resulting attention weights as a heatmap.

```python
# Craft specific Q and K values so that:
# Query at position 1 should strongly attend to Key at position 3
# (Make them nearly identical vectors, while others are random)
d_k = 16
K = torch.randn(1, 5, d_k)
Q = torch.randn(1, 5, d_k)
Q[0, 1] = K[0, 3].clone()  # Make Q[1] identical to K[3]

V = torch.randn(1, 5, d_k)
_, weights = scaled_dot_product_attention(Q, K, V)

# Plot the 5×5 attention matrix
# Does position 1 in the query dimension strongly attend to position 3 in keys?
```

## Step 3: Add Causal Masking

Add a lower-triangular causal mask and verify:
1. The upper triangle of the attention weights is **exactly 0**
2. Each row still sums to 1.0

```python
seq_len = 5
causal_mask = torch.tril(torch.ones(seq_len, seq_len))  # Lower triangle

_, masked_weights = scaled_dot_product_attention(Q, K, V, mask=causal_mask)
print("Causal Attention Weights:")
print(masked_weights[0].detach().round(decimals=3))
# Row 0 should only have weight at position 0
# Row 4 should have weight spread across all 5 positions
```

## Step 4: The Scaling Experiment

Answer this question empirically:

1. Create Q and K with `d_k = 128` (large dimension)
2. Compute attention weights *with* and *without* the `/ sqrt(d_k)` scaling
3. Print the **entropy** of each attention distribution (entropy = -sum(w * log(w)))
4. Higher entropy = more distributed attention (good). Lower entropy = peaked/collapsed.

```python
import math

def entropy(weights):
    """Compute entropy of a probability distribution."""
    # Clip to avoid log(0)
    w = weights.clamp(min=1e-9)
    return -(w * w.log()).sum(dim=-1).mean().item()

# Compare entropy with vs without scaling
# What does low entropy (collapsed attention) mean for learning?
```
