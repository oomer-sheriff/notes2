# Task P6-2: Multi-Head Attention + Encoder Block

**Goal:** Implement Multi-Head Attention and a full Encoder Block from scratch, understanding the reshape trick that makes parallel heads efficient.

Create a Jupyter Notebook in `homework/lab-files/`.

---

## Step 1: Implement MultiHeadAttention

Using `scaled_dot_product_attention` from P6-1, implement the full MHA module:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k     = d_model // n_heads
        
        # Four linear projections
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)
        self.W_o = nn.Linear(d_model, d_model, bias=False)
    
    def forward(self, Q_in, K_in, V_in, mask=None):
        B = Q_in.size(0)
        
        # 1. Project Q, K, V from d_model → d_model
        Q = self.W_q(Q_in)
        K = self.W_k(K_in)
        V = self.W_v(V_in)
        
        # 2. Reshape to (B, n_heads, seq, d_k)
        # Hint: use .view() then .transpose(1, 2)
        # Before: (B, seq, d_model) = (B, seq, n_heads * d_k)
        # After:  (B, n_heads, seq, d_k)
        Q = Q.view(B, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = ...
        V = ...
        
        # 3. Run scaled dot-product attention on all heads simultaneously
        out, attn_w = scaled_dot_product_attention(Q, K, V, mask)
        # out shape: (B, n_heads, seq, d_k)
        
        # 4. Reassemble: (B, n_heads, seq, d_k) → (B, seq, d_model)
        # Hint: transpose(1,2).contiguous().view(B, -1, d_model)
        out = ...
        
        # 5. Final output projection
        return self.W_o(out), attn_w

# Test
mha = MultiHeadAttention(d_model=64, n_heads=4)
x   = torch.randn(2, 10, 64)
out, w = mha(x, x, x)  # Self-attention
print("Output shape:", out.shape)   # (2, 10, 64)
print("Weights shape:", w.shape)   # (2, 4, 10, 10)
```

## Step 2: Implement EncoderBlock and Stack It

```python
class FeedForward(nn.Module):
    def __init__(self, d_model, d_ff=None, dropout=0.1):
        super().__init__()
        d_ff = d_ff or 4 * d_model
        self.net = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
        )
    def forward(self, x):
        return self.net(x)


class EncoderBlock(nn.Module):
    def __init__(self, d_model, n_heads, dropout=0.1):
        super().__init__()
        self.attn  = MultiHeadAttention(d_model, n_heads)
        self.ff    = FeedForward(d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.drop  = nn.Dropout(dropout)
    
    def forward(self, x, mask=None):
        # Sub-layer 1: self-attention with residual
        attn_out, _ = self.attn(x, x, x, mask)
        x = self.norm1(x + self.drop(attn_out))
        
        # Sub-layer 2: feed-forward with residual
        x = self.norm2(x + self.drop(self.ff(x)))
        return x


# Stack 4 encoder blocks (like a mini-BERT)
encoder = nn.Sequential(*[EncoderBlock(64, 4) for _ in range(4)])
x = torch.randn(2, 20, 64)
out = encoder(x)
print("Encoder stack output:", out.shape)  # (2, 20, 64)
```

## Step 3: Questions to Answer

After running your implementation:

1. **Shape Trace:** Add `print(Q.shape)` after each reshaping step in `MultiHeadAttention.forward()`. Trace the shape through: `(B, seq, d_model)` → `(B, seq, n_heads, d_k)` → `(B, n_heads, seq, d_k)`. Make sure you understand WHY each step is needed.

2. **Parameter Count:** How many parameters does `MultiHeadAttention(d_model=512, n_heads=8)` have? Calculate it by hand (4 matrices of shape 512×512), then verify with `sum(p.numel() for p in mha.parameters())`.

3. **Self vs Cross Attention:** Change the `forward` call to use different tensors for Q vs K, V:
   ```python
   decoder_query = torch.randn(2, 5, 64)   # From decoder (shorter)
   encoder_kv    = torch.randn(2, 20, 64)  # From encoder (longer)
   out, w = mha(decoder_query, encoder_kv, encoder_kv)
   print(out.shape)   # (2, 5, 64) — decoder seq length
   print(w.shape)     # (2, 4, 5, 20) — 5 decoder queries × 20 encoder keys
   ```
   This is **cross-attention** — the same MHA module used differently!
