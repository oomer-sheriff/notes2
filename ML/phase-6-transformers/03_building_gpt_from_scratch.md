# Building a GPT from Scratch (Decoder-Only Transformer)

GPT (Generative Pre-trained Transformer) is a **decoder-only** Transformer. It predicts the next token given all previous tokens. This simple objective — trained at massive scale — turns out to be an extraordinarily powerful way to learn language.

The key architectural difference from the encoder is the **causal mask**: every token can only attend to itself and the tokens before it. It cannot "peek" at future tokens. This is what makes it possible to train efficiently on the whole sequence at once (teacher forcing), while still learning to generate autoregressively.

---

## The Full GPT Architecture, Piece by Piece

```
Input token IDs
       ↓
Token Embedding  +  Positional Embedding   ←  Both are learned (not sinusoidal in GPT)
       ↓
  Dropout
       ↓
┌────────────────────────────┐
│  Transformer Block × N     │
│  ┌──────────────────────┐  │
│  │  LayerNorm (Pre-LN)  │  │
│  │  Masked Self-Attention│  │
│  │  Residual Add        │  │
│  ├──────────────────────┤  │
│  │  LayerNorm (Pre-LN)  │  │
│  │  Feed-Forward (MLP)  │  │
│  │  Residual Add        │  │
│  └──────────────────────┘  │
└────────────────────────────┘
       ↓
  Final LayerNorm
       ↓
  Linear Head (d_model → vocab_size)
       ↓
  Logits (probabilities over vocabulary)
```

Note: GPT uses **Pre-LayerNorm** (LayerNorm *before* the sub-layer) rather than the Post-LN in the original Attention paper. Pre-LN trains more stably for very deep models.

---

## Complete GPT Implementation

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class CausalSelfAttention(nn.Module):
    """
    Masked Multi-Head Self-Attention — the heart of the GPT decoder block.
    
    "Causal" means each position can only attend to itself and prior positions.
    We enforce this with a triangular mask registered as a buffer (not trained).
    """
    def __init__(self, d_model, n_heads, max_seq_len, dropout=0.1):
        super().__init__()
        assert d_model % n_heads == 0
        self.n_heads = n_heads
        self.d_k     = d_model // n_heads
        self.d_model = d_model
        
        # Combined projection for Q, K, V in a single matrix (3× more efficient)
        self.qkv_proj = nn.Linear(d_model, 3 * d_model, bias=False)
        self.out_proj  = nn.Linear(d_model, d_model, bias=False)
        
        self.attn_drop = nn.Dropout(dropout)
        self.resid_drop = nn.Dropout(dropout)
        
        # The causal mask: register_buffer means it's NOT a trained parameter,
        # but it IS saved/loaded with the model and moved to GPU automatically.
        # Shape: (1, 1, max_seq_len, max_seq_len) — broadcast over batch & heads
        mask = torch.tril(torch.ones(max_seq_len, max_seq_len))
        self.register_buffer('mask', mask.view(1, 1, max_seq_len, max_seq_len))
    
    def forward(self, x):
        # x: (batch, seq_len, d_model)
        B, T, C = x.size()  # Batch, sequence length (T for "Time"), channels
        
        # Single matrix multiply computes Q, K, V all at once: much faster
        qkv = self.qkv_proj(x)            # (B, T, 3*d_model)
        Q, K, V = qkv.split(self.d_model, dim=2)  # Each: (B, T, d_model)
        
        # Reshape for multi-head: (B, n_heads, T, d_k)
        Q = Q.view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        K = K.view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        V = V.view(B, T, self.n_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)
        
        # Apply causal mask: slice to current sequence length
        # The mask was pre-built for max_seq_len; we only use the T×T top-left submatrix
        scores = scores.masked_fill(self.mask[:, :, :T, :T] == 0, float('-inf'))
        
        weights = F.softmax(scores, dim=-1)
        weights = self.attn_drop(weights)
        
        # Weighted sum of values, then reassemble heads
        out = torch.matmul(weights, V)                          # (B, n_heads, T, d_k)
        out = out.transpose(1, 2).contiguous().view(B, T, C)   # (B, T, d_model)
        
        return self.resid_drop(self.out_proj(out))


class GPTBlock(nn.Module):
    """
    One GPT Transformer block using Pre-LayerNorm (LayerNorm before sublayer).
    
    This differs from the original "Attention Is All You Need" paper which used Post-LN.
    Pre-LN is more stable for training very deep networks (GPT uses this).
    """
    def __init__(self, d_model, n_heads, max_seq_len, dropout=0.1):
        super().__init__()
        d_ff = 4 * d_model  # Feed-forward inner dimension is always 4× d_model in GPT
        
        self.ln1  = nn.LayerNorm(d_model)
        self.attn = CausalSelfAttention(d_model, n_heads, max_seq_len, dropout)
        
        self.ln2  = nn.LayerNorm(d_model)
        self.ff   = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.GELU(),           # GPT uses GELU, not ReLU
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout),
        )
    
    def forward(self, x):
        # Pre-LN: normalize BEFORE the sublayer, then add residual
        x = x + self.attn(self.ln1(x))   # Self-attention sublayer
        x = x + self.ff(self.ln2(x))     # Feed-forward sublayer
        return x


class MiniGPT(nn.Module):
    """
    A complete character-level GPT model.
    This is essentially Karpathy's nanoGPT, explained in detail.
    
    vocab_size:  Number of unique tokens (characters or subwords)
    d_model:     Embedding dimension (model width)
    n_heads:     Number of attention heads per block
    n_layers:    Number of stacked transformer blocks (model depth)
    max_seq_len: Maximum context window (sequence length)
    """
    def __init__(self, vocab_size, d_model=128, n_heads=4, n_layers=4,
                 max_seq_len=256, dropout=0.1):
        super().__init__()
        
        # Token embedding: maps integer token IDs to d_model-dimensional vectors
        # Unlike BERT which uses subword tokens, a char-level model uses characters
        self.token_emb = nn.Embedding(vocab_size, d_model)
        
        # Learned positional embedding: each position gets its own vector (not sinusoidal)
        # Simpler and often works just as well for shorter sequences
        self.pos_emb   = nn.Embedding(max_seq_len, d_model)
        
        self.drop = nn.Dropout(dropout)
        
        # N stacked transformer blocks: this is where all the learning happens
        self.blocks = nn.Sequential(*[
            GPTBlock(d_model, n_heads, max_seq_len, dropout)
            for _ in range(n_layers)
        ])
        
        self.final_ln = nn.LayerNorm(d_model)  # Post-norm before the output head
        
        # Language model head: projects from d_model back to vocab size
        # This is the logit layer — cross-entropy loss is applied here
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        
        # Weight tying: share weights between token embedding and lm_head
        # This is a critical trick used in all modern LLMs.
        # The embedding and the output projection are inverses of each other —
        # tying them halves those parameters AND improves performance.
        self.lm_head.weight = self.token_emb.weight
        
        self.max_seq_len = max_seq_len
    
    def forward(self, token_ids, targets=None):
        """
        token_ids: (batch, seq_len) — integer token indices
        targets:   (batch, seq_len) — the NEXT token at each position (for computing loss)
        
        Returns:
            logits: (batch, seq_len, vocab_size)
            loss:   scalar loss (if targets is provided), else None
        """
        B, T = token_ids.shape
        assert T <= self.max_seq_len, f"Sequence too long: {T} > {self.max_seq_len}"
        
        # Create position indices [0, 1, 2, ..., T-1]
        positions = torch.arange(T, device=token_ids.device)
        
        # Sum token embedding + position embedding
        # This is how the model knows both WHAT a token is AND WHERE it is
        x = self.token_emb(token_ids) + self.pos_emb(positions)  # (B, T, d_model)
        x = self.drop(x)
        
        # Pass through all N transformer blocks
        x = self.blocks(x)      # Still (B, T, d_model)
        x = self.final_ln(x)
        
        # Project to vocabulary size: one set of logits per position
        logits = self.lm_head(x)  # (B, T, vocab_size)
        
        loss = None
        if targets is not None:
            # CrossEntropyLoss expects (N, C) and (N,)
            # We reshape: (B*T, vocab_size) and (B*T,)
            # Each of the B*T positions predicts the next token
            loss = F.cross_entropy(
                logits.view(-1, logits.size(-1)),  # (B*T, vocab_size)
                targets.view(-1)                   # (B*T,)
            )
        
        return logits, loss
    
    @torch.no_grad()
    def generate(self, prompt_ids, max_new_tokens, temperature=0.8, top_k=None):
        """
        Autoregressively generate tokens from a prompt.
        
        This loop is what happens at INFERENCE TIME:
        1. Run the model forward to get logits for the LAST position
        2. Sample the next token from those logits
        3. Append it to the sequence
        4. Repeat
        
        temperature: Controls randomness (lower = more deterministic)
        top_k: If set, only sample from the top-k most likely tokens
        """
        self.eval()
        for _ in range(max_new_tokens):
            # Crop context to max_seq_len if it's gotten too long
            context = prompt_ids[:, -self.max_seq_len:]
            
            logits, _ = self(context)  # Forward pass
            
            # We only care about the LAST position's prediction
            logits = logits[:, -1, :]  # (B, vocab_size)
            
            # Apply temperature scaling
            logits = logits / temperature
            
            # Optional: top-k filtering
            # Zero out all logits except the top-k largest, preventing unlikely tokens
            if top_k is not None:
                values, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                # Set everything below the k-th value to -inf
                logits[logits < values[:, [-1]]] = float('-inf')
            
            # Convert to probabilities and sample
            probs    = F.softmax(logits, dim=-1)
            next_tok = torch.multinomial(probs, num_samples=1)  # (B, 1)
            
            # Append the new token and continue
            prompt_ids = torch.cat([prompt_ids, next_tok], dim=1)
        
        return prompt_ids


# --- Instantiate and sanity-check ---
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# "Small" GPT: like GPT-nano (for quick experiments)
model = MiniGPT(
    vocab_size=65,    # Character-level: 65 unique ASCII chars in Shakespeare
    d_model=128,
    n_heads=4,
    n_layers=4,
    max_seq_len=256
).to(device)

total_params = sum(p.numel() for p in model.parameters())
print(f"Model parameters: {total_params:,}")  # ~4M params

# Test forward pass with fake data
dummy_tokens  = torch.randint(0, 65, (4, 128)).to(device)   # Batch=4, SeqLen=128
dummy_targets = torch.randint(0, 65, (4, 128)).to(device)

logits, loss = model(dummy_tokens, dummy_targets)
print(f"Logits shape: {logits.shape}")   # (4, 128, 65)
print(f"Initial loss: {loss.item():.4f}")  # Should be ~ln(65) ≈ 4.17 (random model)
```

---

## Training on Shakespeare

```python
import urllib.request

# Download Shakespeare
url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
urllib.request.urlretrieve(url, "shakespeare.txt")

with open("shakespeare.txt", 'r') as f:
    text = f.read()

# Build character-level vocabulary
chars     = sorted(set(text))
vocab_size = len(chars)
stoi      = {c: i for i, c in enumerate(chars)}  # string → index
itos      = {i: c for i, c in enumerate(chars)}  # index → string

encode = lambda s: [stoi[c] for c in s]
decode = lambda l: ''.join([itos[i] for i in l])

# Convert entire text to tensor of integers
data      = torch.tensor(encode(text), dtype=torch.long)
n_train   = int(0.9 * len(data))
train_data = data[:n_train]
val_data   = data[n_train:]

print(f"Vocab size: {vocab_size}")
print(f"Train tokens: {len(train_data):,}, Val tokens: {len(val_data):,}")

# Training hyperparameters
SEQ_LEN   = 256
BATCH     = 32
LR        = 3e-4
MAX_STEPS = 5000

model = MiniGPT(vocab_size=vocab_size, d_model=128, n_heads=4, n_layers=4,
                max_seq_len=SEQ_LEN).to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=0.1)

def get_batch(split):
    """Sample a random batch of sequences from the dataset."""
    data  = train_data if split == 'train' else val_data
    # Random starting positions (batch_size of them)
    ix    = torch.randint(len(data) - SEQ_LEN, (BATCH,))
    x     = torch.stack([data[i:i+SEQ_LEN]   for i in ix]).to(device)
    # Target is the same sequence shifted by 1: predict NEXT token
    y     = torch.stack([data[i+1:i+SEQ_LEN+1] for i in ix]).to(device)
    return x, y

train_losses, val_losses = [], []

for step in range(MAX_STEPS):
    model.train()
    x, y = get_batch('train')
    _, loss = model(x, y)
    
    optimizer.zero_grad()
    loss.backward()
    # Gradient clipping: Transformers also need this!
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    
    train_losses.append(loss.item())
    
    if step % 500 == 0:
        # Evaluate on validation set
        model.eval()
        with torch.no_grad():
            val_x, val_y = get_batch('val')
            _, val_loss = model(val_x, val_y)
        val_losses.append(val_loss.item())
        print(f"Step {step:5d}: train_loss={loss.item():.4f}, val_loss={val_loss.item():.4f}")

# Generate some text!
model.eval()
seed = torch.tensor([[stoi['\n']]], device=device)  # Start from newline
generated_ids = model.generate(seed, max_new_tokens=500, temperature=0.8, top_k=40)
print("\n=== Generated Shakespeare ===")
print(decode(generated_ids[0].tolist()))
```

---
## References
*   [Andrej Karpathy: Let's build GPT from scratch](https://www.youtube.com/watch?v=kCc8FmEb1nY) — Follow along with this!
*   [nanoGPT GitHub](https://github.com/karpathy/nanoGPT) — Karpathy's clean reference implementation
*   [The Illustrated GPT-2](https://jalammar.github.io/illustrated-gpt2/)
