# Phase 6: Quick Reference & Cheat Sheet

## The Attention Formula

```
Attention(Q, K, V) = softmax( Q·Kᵀ / √d_k ) · V

Q: (batch, seq, d_k)  — "What am I looking for?"
K: (batch, seq, d_k)  — "What do I contain?"
V: (batch, seq, d_v)  — "What do I give?"
```

## Shapes Through a Transformer

```python
# Input sequence
x = torch.randn(batch=4, seq=128, d_model=512)

# After Multi-Head Attention (shape-preserving)
# MHA input/output: (4, 128, 512)

# After Feed-Forward (shape-preserving)
# FFN input/output: (4, 128, 512)

# For classification: pool over sequence dimension
# CLS token pooling (BERT):
cls_token = x[:, 0, :]       # (4, 512)
# Mean pooling (SentenceTransformers):
pooled = x.mean(dim=1)       # (4, 512)

# Final classifier head
output = nn.Linear(512, num_classes)(pooled)  # (4, num_classes)
```

## Causal Mask Generation

```python
# Creates a lower-triangular mask for decoder self-attention
def get_causal_mask(seq_len, device):
    return torch.tril(torch.ones(seq_len, seq_len, device=device))

# Usage:
mask = get_causal_mask(seq_len=128, device=device)
# In attention: scores.masked_fill(mask == 0, float('-inf'))
```

## Key Architectural Differences

| Component | Encoder (BERT) | Decoder (GPT) |
|---|---|---|
| Attention mask | None (bidirectional) | Causal (lower-triangular) |
| Pre-training | Masked LM | Next-token prediction |
| Positional encoding | Learned embeddings | Learned embeddings |
| LayerNorm placement | Post-LN (original) | Pre-LN (more stable) |
| Use case | Understanding tasks | Generation tasks |

## HuggingFace Quick Patterns

```python
from transformers import AutoTokenizer, AutoModel, pipeline

# --- Load tokenizer + model for any task ---
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

# --- Tokenize text (handles padding, truncation) ---
encoded = tokenizer(
    ["First sentence.", "Second sentence, longer."],
    padding=True,          # Pad to longest in batch
    truncation=True,       # Cut at max_length
    max_length=512,
    return_tensors="pt"    # Return PyTorch tensors
)
# encoded.input_ids:      (2, max_len) — token IDs
# encoded.attention_mask: (2, max_len) — 1=real token, 0=padding

# --- Get embeddings ---
with torch.no_grad():
    output = model(**encoded)
    # output.last_hidden_state: (2, seq_len, 768) — contextual embeddings
    # CLS token representation:
    cls_embedding = output.last_hidden_state[:, 0, :]  # (2, 768)

# --- One-liner pipelines ---
generator  = pipeline("text-generation",         model="gpt2")
classifier = pipeline("text-classification",     model="distilbert-base-uncased-finetuned-sst-2-english")
qa_pipe    = pipeline("question-answering",      model="deepset/roberta-base-squad2")
ner_pipe   = pipeline("token-classification",   model="dbmdz/bert-large-cased-finetuned-conll03-english")
summarizer = pipeline("summarization",           model="facebook/bart-large-cnn")
```

## Hyperparameter Defaults (from literature)

| Hyperparameter | GPT-2 Small | BERT-base | Your Mini-GPT |
|---|---|---|---|
| d_model | 768 | 768 | 128-256 |
| n_heads | 12 | 12 | 4-8 |
| n_layers | 12 | 12 | 4-6 |
| d_ff | 3072 | 3072 | 4 × d_model |
| max_seq_len | 1024 | 512 | 256-512 |
| Dropout | 0.1 | 0.1 | 0.1 |
| Learning rate | 2.5e-4 | 2e-5 (finetune) | 3e-4 |
| Warmup steps | 2000 | 10k | 100-500 |
