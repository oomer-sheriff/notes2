# Task P5-1: Char-Level RNN — Text Generation

**Goal:** Build a character-level RNN that learns to mimic the style of a text and generates new text. This is the classic "predict the next character" task that shows exactly what RNNs learn from sequences.

Create a Jupyter Notebook in `homework/lab-files/`.

---

## Setup: Text Corpus

Use a short excerpt of Shakespeare. The RNN will learn to generate Shakespearean-sounding text.

```python
import torch
import torch.nn as nn
import numpy as np
import matplotlib.pyplot as plt

# Full text — you can replace this with any text you like
text = """
To be, or not to be, that is the question:
Whether 'tis nobler in the mind to suffer
The slings and arrows of outrageous fortune,
Or to take arms against a sea of troubles
And by opposing end them. To die—to sleep,
No more; and by a sleep to say we end
The heartache, and the thousand natural shocks
That flesh is heir to: 'tis a consummation
Devoutly to be wish'd. To die, to sleep;
To sleep, perchance to dream.
""".lower()

# Build a character-level vocabulary
chars     = sorted(set(text))   # All unique characters
vocab_size = len(chars)

# Two lookup tables: char → integer and integer → char
char_to_idx = {ch: i for i, ch in enumerate(chars)}
idx_to_char = {i: ch for i, ch in enumerate(chars)}

print(f"Vocabulary size: {vocab_size} unique characters")
print(f"Characters: {chars}")
print(f"Text length: {len(text)} characters")
```

## The Model

```python
class CharRNN(nn.Module):
    """Character-level text generation using a stacked LSTM."""
    def __init__(self, vocab_size, hidden_size, num_layers=2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers  = num_layers
        
        # Embedding: maps each character integer to a dense vector
        # This is richer than one-hot encoding (characters near in meaning become near in space)
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        
        # The LSTM processes the sequence of character embeddings
        self.lstm = nn.LSTM(hidden_size, hidden_size, num_layers, 
                            batch_first=True, dropout=0.3)
        
        # The output head maps hidden states to character probabilities
        self.fc = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, x, hidden=None):
        # x shape:      (batch, seq_len) — integer token indices
        # hidden: tuple (h_n, c_n) or None (will default to zeros)
        x   = self.embedding(x)  # (batch, seq_len, hidden_size)
        out, hidden = self.lstm(x, hidden)
        out = self.fc(out)        # (batch, seq_len, vocab_size) — one prediction per char
        return out, hidden
```

## Training

The training objective is **next-character prediction**: given the first N characters, predict what character N+1 is. This is the same principle behind GPT — just at the word/token level instead of the character level.

```python
# Convert text to integers
data = [char_to_idx[c] for c in text]

def get_batch(data, seq_len=50, batch_size=32):
    """Sample random chunks of the text as training batches."""
    # Random starting positions
    starts = torch.randint(0, len(data) - seq_len - 1, (batch_size,))
    x = torch.stack([torch.tensor(data[s:s+seq_len])   for s in starts])
    # Target: same chunk shifted by 1 (the "next" character at each position)
    y = torch.stack([torch.tensor(data[s+1:s+seq_len+1]) for s in starts])
    return x, y

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model  = CharRNN(vocab_size, hidden_size=128, num_layers=2).to(device)

optimizer = torch.optim.Adam(model.parameters(), lr=0.002)
criterion = nn.CrossEntropyLoss()

losses = []
for step in range(2000):
    model.train()
    x, y = get_batch(data, seq_len=60, batch_size=64)
    x, y = x.to(device), y.to(device)
    
    optimizer.zero_grad()
    output, _ = model(x)    # (64, 60, vocab_size)
    
    # CrossEntropyLoss expects (N, C, *), so we permute
    loss = criterion(output.permute(0, 2, 1), y)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    optimizer.step()
    losses.append(loss.item())
    
    if (step + 1) % 200 == 0:
        print(f"Step {step+1}: Loss = {loss.item():.4f}")

plt.plot(losses)
plt.title("Training Loss")
plt.xlabel("Step")
# plt.show()
```

## Text Generation

```python
def generate(model, seed_text, length=200, temperature=0.8):
    """
    Generate new text starting from seed_text.
    
    Temperature controls randomness:
      - Low temp (0.1): very conservative, repeats common patterns
      - High temp (1.5): very creative, often nonsensical
      - ~0.8: usually a good balance
    """
    model.eval()
    generated = seed_text
    
    # Convert seed to indices
    input_ids = torch.tensor([[char_to_idx[c] for c in seed_text]]).to(device)
    
    with torch.no_grad():
        _, hidden = model(input_ids)  # Process seed, capture hidden state
        
        # The last predicted character becomes the next input
        next_input = input_ids[:, -1:]  # Shape: (1, 1)
        
        for _ in range(length):
            output, hidden = model(next_input, hidden)
            
            # output: (1, 1, vocab_size) — one prediction for the one input token
            logits = output[0, 0]  # (vocab_size,)
            
            # Apply temperature: divide logits before softmax
            # High temperature → flatter distribution → more random sampling
            probs = torch.softmax(logits / temperature, dim=0)
            
            # Sample from the probability distribution (not just argmax!)
            # argmax always picks the most likely character → repetitive text
            next_char_idx = torch.multinomial(probs, num_samples=1)
            
            generated  += idx_to_char[next_char_idx.item()]
            next_input  = next_char_idx.unsqueeze(0)  # (1, 1) for next step

    return generated

# Generate text with different temperatures
for temp in [0.5, 0.8, 1.2]:
    print(f"\n=== Temperature {temp} ===")
    print(generate(model, seed_text="to be", length=150, temperature=temp))
```

## Your Tasks

1. **Train with `nn.RNN`** instead of `nn.LSTM`. Does the quality of generated text differ?
2. **Experiment with temperatures** 0.2, 0.8, and 1.5. Describe what you observe for each.
3. **Try a longer text** — download Project Gutenberg's full Shakespeare (~4MB). Does more data improve coherence?
4. **Challenge:** Add a `nn.Embedding` layer that reduces the embedding dimension from `hidden_size` to 32. Does it still work?
