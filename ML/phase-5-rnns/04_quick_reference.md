# Phase 5: Quick Reference & Cheat Sheet

## API Comparison: RNN vs LSTM vs GRU

The three modules have almost identical APIs. The only difference is what state tensors they accept and return.

```python
import torch
import torch.nn as nn

batch, seq_len, features = 8, 20, 10
x = torch.randn(batch, seq_len, features)

# --- RNN ---
# One state tensor: h (hidden state)
rnn  = nn.RNN(features, hidden_size=64, num_layers=2, batch_first=True, dropout=0.3)
h0   = torch.zeros(2, batch, 64)            # (num_layers, batch, hidden)
out, h_n = rnn(x, h0)
# out: (8, 20, 64)  — hidden state at every timestep
# h_n: (2, 8, 64)  — final hidden state (one per layer)

# --- LSTM ---
# TWO state tensors: (h, c) — hidden and cell state
lstm = nn.LSTM(features, hidden_size=64, num_layers=2, batch_first=True, dropout=0.3)
h0   = torch.zeros(2, batch, 64)
c0   = torch.zeros(2, batch, 64)
out, (h_n, c_n) = lstm(x, (h0, c0))        # Note the TUPLE input and output

# --- GRU ---
# One state tensor: h (no separate cell state)
gru  = nn.GRU(features, hidden_size=64, num_layers=2, batch_first=True, dropout=0.3)
h0   = torch.zeros(2, batch, 64)
out, h_n = gru(x, h0)                      # Same API as RNN
```

## Sequence Classification (e.g. Sentiment Analysis)

```python
class SequenceClassifier(nn.Module):
    """For tasks where you need ONE label for the WHOLE sequence."""
    def __init__(self, input_size, hidden_size, num_classes, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=0.3)
        self.dropout = nn.Dropout(0.5)
        self.fc = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        out, (h_n, c_n) = self.lstm(x)
        
        # Take only the FINAL hidden state of the LAST layer for classification
        last_hidden = h_n[-1]       # (batch, hidden_size)
        last_hidden = self.dropout(last_hidden)
        return self.fc(last_hidden) # (batch, num_classes)
```

## Token-Level Prediction (e.g. Named Entity Recognition)

```python
class TokenClassifier(nn.Module):
    """For tasks where you need ONE label PER TOKEN in the sequence."""
    def __init__(self, input_size, hidden_size, num_classes, num_layers=2):
        super().__init__()
        # bidirectional=True processes the sequence in BOTH directions.
        # Forward pass sees left context; backward pass sees right context.
        # This doubles the effective hidden size.
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers,
                            batch_first=True, dropout=0.3, bidirectional=True)
        self.fc = nn.Linear(hidden_size * 2, num_classes)  # *2 for bidirectional
    
    def forward(self, x):
        # x: (batch, seq_len, input_size)
        out, _ = self.lstm(x)
        # out: (batch, seq_len, hidden_size * 2)
        # Use ALL timestep outputs (not just the last one)
        return self.fc(out)  # (batch, seq_len, num_classes)
```

## Gradient Clipping (Always use with RNNs!)

```python
# In your training loop, AFTER loss.backward() and BEFORE optimizer.step()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

## Text Preprocessing with Embeddings

Real NLP uses integer token IDs, not raw one-hot vectors. `nn.Embedding` converts token IDs into dense vectors.

```python
vocab_size   = 10000  # Number of unique words in your vocabulary
embedding_dim = 128   # Each word maps to a 128-dimensional vector

embedding_layer = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
# padding_idx=0: index 0 is reserved for padding (short sequences padded to same length)

# Token IDs (not one-hot — just integers)
token_ids = torch.tensor([[5, 23, 1, 876, 0, 0],  # Padded to length 6
                           [45, 7, 233, 0, 0, 0]]) # Shape: (2, 6)

embeddings = embedding_layer(token_ids)
print(embeddings.shape)  # (2, 6, 128) — ready to feed into an LSTM!
```
