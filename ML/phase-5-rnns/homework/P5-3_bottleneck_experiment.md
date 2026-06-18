# Task P5-3: The Bottleneck Experiment

**Goal:** Empirically demonstrate the information bottleneck problem in the basic Seq2Seq architecture, and measure exactly how performance degrades as sequence length grows. This motivates why Attention (Phase 6) was invented.

Create a Jupyter Notebook in `homework/lab-files/`.

---

## Setup

We'll use the sequence reversal task from the concept notes — it's pure logic with no domain knowledge, so any degradation is purely due to the architecture's memory limitations.

```python
import torch
import torch.nn as nn
import random
import matplotlib.pyplot as plt

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# Vocabulary: numbers 1-9 (0 reserved for padding)
VOCAB_SIZE  = 10
HIDDEN_SIZE = 128

class Encoder(nn.Module):
    def __init__(self, hidden_size, num_layers=1):
        super().__init__()
        # Each token is a number 1-9; embedding gives it a dense representation
        self.embedding = nn.Embedding(VOCAB_SIZE, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True)
    
    def forward(self, x):
        x = self.embedding(x)
        _, (h_n, c_n) = self.lstm(x)
        return h_n, c_n  # The "context" — the bottleneck


class Decoder(nn.Module):
    def __init__(self, hidden_size, num_layers=1):
        super().__init__()
        self.embedding = nn.Embedding(VOCAB_SIZE, hidden_size)
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, batch_first=True)
        self.fc   = nn.Linear(hidden_size, VOCAB_SIZE)  # Predict one of vocab_size tokens
    
    def forward(self, x, h, c):
        # x: (batch, 1) — a single integer token
        x   = self.embedding(x)  # (batch, 1, hidden_size)
        out, (h_n, c_n) = self.lstm(x, (h, c))
        return self.fc(out), h_n, c_n  # (batch, 1, vocab_size)


class Seq2Seq(nn.Module):
    def __init__(self, encoder, decoder):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
    
    def forward(self, src, target_len, target=None, teacher_forcing=0.5):
        batch  = src.size(0)
        outputs = torch.zeros(batch, target_len, VOCAB_SIZE).to(device)
        
        h, c = self.encoder(src)
        
        # Start token for the decoder (we'll use token index 0 as <START>)
        dec_in = torch.zeros(batch, 1, dtype=torch.long).to(device)
        
        for t in range(target_len):
            pred, h, c = self.decoder(dec_in, h, c)
            outputs[:, t, :] = pred.squeeze(1)
            
            if target is not None and random.random() < teacher_forcing:
                dec_in = target[:, t].unsqueeze(1)
            else:
                dec_in = pred.argmax(dim=2)  # Greedy decode: pick most likely token
        
        return outputs
```

## The Bottleneck Experiment: Accuracy vs Sequence Length

Train the model once on short sequences, then test it on sequences of increasing length. The accuracy should degrade noticeably as sequence length grows beyond the training length.

```python
def generate_reversal_batch(batch_size, seq_len):
    """Generates random number sequences and their reverses."""
    src = torch.randint(1, VOCAB_SIZE, (batch_size, seq_len))
    tgt = src.flip(dims=[1])
    return src.to(device), tgt.to(device)

# Build and train the model on length-8 sequences
encoder = Encoder(HIDDEN_SIZE)
decoder = Decoder(HIDDEN_SIZE)
model   = Seq2Seq(encoder, decoder).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.CrossEntropyLoss()

print("Training on sequence length 8...")
for step in range(3000):
    model.train()
    src, tgt = generate_reversal_batch(batch_size=128, seq_len=8)
    optimizer.zero_grad()
    out  = model(src, target_len=8, target=tgt, teacher_forcing=0.5)
    # out: (128, 8, VOCAB_SIZE); tgt: (128, 8)
    loss = criterion(out.reshape(-1, VOCAB_SIZE), tgt.reshape(-1))
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    
    if (step + 1) % 500 == 0:
        print(f"  Step {step+1}/3000, Loss: {loss.item():.4f}")


def evaluate_accuracy(model, seq_len, num_batches=20):
    """Compute exact-match accuracy: every token in the sequence must be correct."""
    model.eval()
    correct_seqs = 0
    total_seqs   = 0
    
    with torch.no_grad():
        for _ in range(num_batches):
            src, tgt = generate_reversal_batch(batch_size=64, seq_len=seq_len)
            out      = model(src, target_len=seq_len, teacher_forcing=0.0)
            preds    = out.argmax(dim=2)  # (64, seq_len)
            
            # A sequence is "correct" only if EVERY token matches
            correct_seqs += (preds == tgt).all(dim=1).sum().item()
            total_seqs   += tgt.size(0)
    
    return correct_seqs / total_seqs

# Test at multiple sequence lengths
lengths    = [4, 6, 8, 10, 12, 15, 20]
accuracies = []

print("\n--- Bottleneck Experiment Results ---")
for l in lengths:
    acc = evaluate_accuracy(model, seq_len=l)
    accuracies.append(acc)
    print(f"  Sequence length {l:>2}: {acc:.1%} exact accuracy")

# Plot the degradation curve
plt.figure(figsize=(8, 5))
plt.plot(lengths, accuracies, marker='o', linewidth=2)
plt.axvline(x=8, color='red', linestyle='--', label='Training length')
plt.xlabel("Sequence Length")
plt.ylabel("Exact Match Accuracy")
plt.title("Seq2Seq Bottleneck: Accuracy vs Sequence Length")
plt.legend()
plt.grid(True)
# plt.show()
```

## Your Tasks

1. **Observe the cliff**: At what sequence length does accuracy drop below 50%? Below 10%?
2. **Double the hidden size** to 256. Does it help? By how much, and for how long?
3. **Try training on length 20** instead of length 8. Now test lengths 5-30. What changes?
4. **The key question to answer:** Why does the model fail? Write 2-3 sentences explaining the information bottleneck in your own words, based on what you observe in the numbers. (This is exactly the problem that Attention was invented to solve — you'll understand it much better in Phase 6.)
