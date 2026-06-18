# Sequence-to-Sequence (Seq2Seq) Models

So far, we've used RNNs to classify a *whole* sequence into a single label (sentiment analysis: sequence → positive/negative). But many real problems require mapping one sequence to another sequence of a *different length*:
- Machine Translation: "Hello" → "Hola" (English → Spanish)
- Text Summarization: 1000-word article → 50-word summary
- Speech Recognition: audio waveform → text transcript

This is the **Sequence-to-Sequence (Seq2Seq)** problem, and it requires a fundamentally different architecture.

---

## The Encoder-Decoder Architecture

The solution is to split the network into two specialized halves:

**Encoder:** An LSTM (or RNN) that reads the entire input sequence one token at a time. It doesn't produce any useful output during this phase — it just compresses the input into a single **context vector**: the final hidden state `h_n`. This vector is supposed to be a dense summary of the entire input.

**Decoder:** A separate LSTM that *generates* the output sequence, one token at a time. At each step, it takes:
1. The previous token it generated (or a special `<START>` token at step 1)
2. Its own previous hidden state
3. The context vector from the encoder (only at step 1)

The decoder keeps generating until it outputs a special `<END>` token.

```
Input:  [ "the", "dog", "is", "hungry" ]
            ↓      ↓      ↓      ↓
         [ENC]  [ENC]  [ENC]  [ENC]  →  context vector h_c
                                              ↓
Output:  [ "el", "perro", "tiene", "hambre", <END> ]
            ↑       ↑        ↑        ↑        ↑
         [DEC]   [DEC]   [DEC]   [DEC]   [DEC]
```

---

## Building a Complete Seq2Seq Model

Let's build a working Seq2Seq model for a simple task: **reversing a sequence of numbers**. For example, `[3, 7, 2, 5, 1]` → `[1, 5, 2, 7, 3]`. This is a pure learning task with no domain knowledge required, so it's perfect for isolating how well the architecture works.

```python
import torch
import torch.nn as nn
import random

# --- HYPERPARAMETERS ---
INPUT_SIZE   = 1     # Each token is just a single number
HIDDEN_SIZE  = 64    # Hidden state dimension
OUTPUT_SIZE  = 1     # Each output token is also a single number
NUM_LAYERS   = 1
DEVICE       = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class Encoder(nn.Module):
    """Reads the entire input sequence and compresses it into a context vector.
    
    The encoder's job is to summarize everything about the input.
    It processes the sequence from left to right and its final hidden state
    captures what it "remembers" about the full input.
    """
    def __init__(self, input_size, hidden_size, num_layers=1):
        super().__init__()
        # batch_first=True means inputs are (batch, seq_len, features)
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_size)
        # We don't need 'outputs' here — just the final hidden and cell states
        outputs, (h_n, c_n) = self.lstm(x)
        # h_n shape: (num_layers, batch, hidden_size)
        # c_n shape: (num_layers, batch, hidden_size)
        return h_n, c_n  # These together form the "context" for the decoder


class Decoder(nn.Module):
    """Generates the output sequence, one token at a time.
    
    At each step, it consumes its own previous output and uses
    the context from the encoder (passed in as the initial hidden state).
    This creates a feedback loop — the decoder attends to its own prior output.
    """
    def __init__(self, output_size, hidden_size, num_layers=1):
        super().__init__()
        # Input at each step: the previous output token (1 value)
        self.lstm = nn.LSTM(output_size, hidden_size, num_layers, batch_first=True)
        # Maps from hidden state to the actual prediction
        self.fc   = nn.Linear(hidden_size, output_size)
    
    def forward(self, x, h, c):
        # x shape:      (batch, 1, output_size)  — one token at a time
        # h, c shapes:  (num_layers, batch, hidden_size)
        output, (h_n, c_n) = self.lstm(x, (h, c))
        # output shape: (batch, 1, hidden_size)
        prediction = self.fc(output)  # (batch, 1, output_size)
        return prediction, h_n, c_n


class Seq2Seq(nn.Module):
    """Combines the Encoder and Decoder into a single trainable model.
    
    The key design decision is how to connect them:
    - The encoder's FINAL hidden and cell states become the decoder's INITIAL states.
    - This is the "bottleneck": all information about the input must pass through h_n and c_n.
    """
    def __init__(self, encoder, decoder, device):
        super().__init__()
        self.encoder = encoder
        self.decoder = decoder
        self.device  = device
    
    def forward(self, src, target_len, target_seq=None, teacher_forcing_ratio=0.5):
        """
        src:                  (batch, src_len, 1)    — the input sequence
        target_len:           int                    — how many tokens to generate
        target_seq:           (batch, target_len, 1) — the true outputs (for training)
        teacher_forcing_ratio: float                 — probability of using true token vs predicted
        
        Teacher Forcing: During training, instead of feeding the decoder its own (possibly wrong)
        prediction back in, we sometimes feed it the CORRECT token from the ground truth.
        This stabilizes training early on. We gradually reduce the ratio as training progresses.
        """
        batch_size = src.size(0)
        outputs    = torch.zeros(batch_size, target_len, 1).to(self.device)
        
        # Step 1: Run the encoder over the entire input sequence
        h, c = self.encoder(src)
        
        # Step 2: The first decoder input is a zero vector (the "start" signal)
        decoder_input = torch.zeros(batch_size, 1, 1).to(self.device)
        
        # Step 3: Generate output tokens one at a time
        for t in range(target_len):
            prediction, h, c = self.decoder(decoder_input, h, c)
            outputs[:, t:t+1, :] = prediction
            
            # Teacher Forcing Decision:
            # During training (when we have target_seq), we randomly decide whether
            # to feed the TRUE next token or the PREDICTED next token as the next input.
            if target_seq is not None and random.random() < teacher_forcing_ratio:
                decoder_input = target_seq[:, t:t+1, :]  # Use the real answer
            else:
                decoder_input = prediction                # Use the model's own guess
        
        return outputs
```

---

## Training and Testing the Seq2Seq Model

```python
import matplotlib.pyplot as plt

# --- BUILD MODEL ---
encoder = Encoder(input_size=1, hidden_size=HIDDEN_SIZE)
decoder = Decoder(output_size=1, hidden_size=HIDDEN_SIZE)
model   = Seq2Seq(encoder, decoder, DEVICE).to(DEVICE)

optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
criterion = nn.MSELoss()

def generate_batch(batch_size, seq_len):
    """Creates a batch of random sequences and their reverses."""
    src = torch.randint(1, 10, (batch_size, seq_len, 1)).float()
    tgt = src.flip(dims=[1])  # Simply reverse the sequence
    return src.to(DEVICE), tgt.to(DEVICE)


# --- TRAINING ---
loss_history = []
EPOCHS = 500

for epoch in range(EPOCHS):
    model.train()
    src, tgt = generate_batch(batch_size=64, seq_len=6)
    
    optimizer.zero_grad()
    # During training, use teacher forcing 50% of the time
    output = model(src, target_len=6, target_seq=tgt, teacher_forcing_ratio=0.5)
    
    loss = criterion(output, tgt)
    loss.backward()
    
    # Clip gradients to prevent exploding gradients problem
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    optimizer.step()
    loss_history.append(loss.item())
    
    if (epoch + 1) % 100 == 0:
        print(f"Epoch {epoch+1}/{EPOCHS}, Loss: {loss.item():.4f}")

# Plot the learning curve
plt.figure(figsize=(8, 4))
plt.plot(loss_history)
plt.title("Seq2Seq Training Loss (Sequence Reversal)")
plt.xlabel("Epoch")
plt.ylabel("MSE Loss")
# plt.show()


# --- TESTING ---
model.eval()
with torch.no_grad():
    test_src, test_tgt = generate_batch(batch_size=1, seq_len=6)
    # At inference time: teacher_forcing_ratio=0, so decoder uses its own predictions
    prediction = model(test_src, target_len=6, teacher_forcing_ratio=0.0)
    
    src_list  = test_src.squeeze().cpu().int().tolist()
    tgt_list  = test_tgt.squeeze().cpu().int().tolist()
    pred_list = prediction.squeeze().cpu().detach().round().int().tolist()
    
    print(f"\nInput:      {src_list}")
    print(f"Target:     {tgt_list}")
    print(f"Prediction: {pred_list}")
```

---

## The Bottleneck Problem

The fundamental weakness of this architecture is the **information bottleneck**. Every single thing the encoder knows about the input must be compressed into the context vector `h_n` — a fixed-size tensor (e.g., 64 numbers) regardless of whether the input is 5 tokens or 500 tokens.

Try increasing `seq_len` to 20 or 30 in the code above. The model will start making more errors because `h_n` simply cannot hold enough information to perfectly reconstruct a long sequence. It's like trying to describe an entire novel in a single 64-character tweet.

The solution — which became one of the most important ideas in all of deep learning — is **Attention**. Instead of forcing the decoder to rely on a single context vector, the attention mechanism lets the decoder look back at the encoder's *hidden state at every timestep* and decide which parts of the input are relevant at each step of generation. This is the foundation of the Transformer, which is the entire subject of Phase 6.

---
## References
*   [Sutskever et al. (2014): Sequence to Sequence Learning with Neural Networks](https://arxiv.org/abs/1409.3215) — The original Seq2Seq paper
*   [Bahdanau et al. (2015): Neural Machine Translation by Jointly Learning to Align and Translate](https://arxiv.org/abs/1409.0473) — The paper that introduced Attention to fix the bottleneck
