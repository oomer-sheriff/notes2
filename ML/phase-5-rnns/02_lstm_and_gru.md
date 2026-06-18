# LSTMs and GRUs: Solving Long-Term Memory

## The LSTM: Gates as a Memory Controller

The LSTM (Long Short-Term Memory, Hochreiter & Schmidhuber, 1997) doesn't fix the vanishing gradient by changing the backpropagation algorithm. Instead, it fundamentally changes the **architecture** so that gradients have a path through time that doesn't multiply by small numbers over and over.

The key innovation is a separate **Cell State** `C_t` — a "conveyor belt" that runs straight through the sequence with only minor linear interactions. Gradients can flow back along this conveyor belt almost unimpeded, giving the network a way to remember information across hundreds of timesteps.

The cell state is controlled by three **gates** — each is a sigmoid neural network that outputs a number between 0 and 1. You can think of a gate output of `0.0` as "block everything" and `1.0` as "let everything through."

---

## The Three Gates in Detail

### The Forget Gate — "What old memory should I erase?"

The forget gate looks at the current input `x_t` and the previous hidden state `h_{t-1}`, and decides what fraction of the old cell state `C_{t-1}` to keep. A value of 1 means "keep all of this memory." A value of 0 means "completely erase it."

```
f_t = sigmoid(W_f · [h_{t-1}, x_t] + b_f)
```

For example: if you're reading text and you just encountered a period `.`, the forget gate might output values close to 0 for everything related to the prior subject, clearing the slate for the next sentence.

### The Input Gate — "What new information should I write to memory?"

The input gate has two parts that work together:
1. `i_t`: A sigmoid that decides *which* memory slots to update (0 = don't touch, 1 = update)
2. `g_t`: A tanh that creates a vector of candidate values to potentially write into those slots

```
i_t = sigmoid(W_i · [h_{t-1}, x_t] + b_i)   # Which memory cells to update?
g_t = tanh(W_g · [h_{t-1}, x_t]   + b_g)   # What values to write into them?
```

The new cell state is then:
```
C_t = f_t * C_{t-1}  +  i_t * g_t
       ↑                   ↑
    keep old memory     write new info
    (scaled by forget)  (scaled by input gate)
```

### The Output Gate — "What should I output right now?"

The output gate decides what to expose as the hidden state `h_t` (which is what's passed to the next timestep and what the classifier reads):

```
o_t = sigmoid(W_o · [h_{t-1}, x_t] + b_o)
h_t = o_t * tanh(C_t)
```

This means the hidden state `h_t` is a filtered version of the cell state — not everything in memory needs to be relevant to the current output.

---

## Building an LSTM from Scratch

Let's implement a single LSTM cell using raw PyTorch operations — no `nn.LSTM` — to make the equations completely transparent:

```python
import torch
import torch.nn as nn

class LSTMCellFromScratch(nn.Module):
    """A single LSTM cell. Processes ONE timestep at a time.
    
    Inputs:
        x_t:   (batch, input_size)  — the input at the current timestep
        h_t_1: (batch, hidden_size) — hidden state from previous timestep
        C_t_1: (batch, hidden_size) — cell state from previous timestep
    
    Outputs:
        h_t:   (batch, hidden_size) — new hidden state
        C_t:   (batch, hidden_size) — new cell state
    """
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.hidden_size = hidden_size
        
        # Each gate needs its own set of weights:
        # one weight matrix for x_t, one for h_{t-1}, and a bias.
        # In practice, we combine [x_t, h_{t-1}] into one vector and use one big weight matrix.
        # This is exactly what PyTorch does internally for efficiency.
        combined_size = input_size + hidden_size  # We'll concat x and h before multiplying
        
        # Forget gate: decides what to erase from cell state
        self.W_f = nn.Linear(combined_size, hidden_size)
        # Input gate: decides which cell state positions to update
        self.W_i = nn.Linear(combined_size, hidden_size)
        # Candidate values gate: what values to potentially write
        self.W_g = nn.Linear(combined_size, hidden_size)
        # Output gate: decides what to expose as the hidden state
        self.W_o = nn.Linear(combined_size, hidden_size)
    
    def forward(self, x_t, h_t_1, C_t_1):
        # Concatenate input and previous hidden state into one vector.
        # Shape: (batch, input_size + hidden_size)
        combined = torch.cat([x_t, h_t_1], dim=1)
        
        # ---- The three gates ----
        # Sigmoid outputs are between 0 and 1: they act as soft on/off switches
        f_t = torch.sigmoid(self.W_f(combined))   # Forget gate: 0=erase, 1=keep
        i_t = torch.sigmoid(self.W_i(combined))   # Input gate: 0=don't update, 1=update
        o_t = torch.sigmoid(self.W_o(combined))   # Output gate: 0=hide, 1=expose
        
        # Candidate cell update: tanh keeps values between -1 and 1
        g_t = torch.tanh(self.W_g(combined))
        
        # ---- Cell State Update (the conveyor belt) ----
        # f_t * C_t_1: forget some of the old memory
        # i_t * g_t:   write new information into some cells
        C_t = f_t * C_t_1  +  i_t * g_t
        
        # ---- Hidden State (the output) ----
        # Only expose a filtered version of the cell state
        h_t = o_t * torch.tanh(C_t)
        
        return h_t, C_t


# Test the cell
batch_size  = 3
input_size  = 10
hidden_size = 20

cell = LSTMCellFromScratch(input_size, hidden_size)

# Initial states are all zeros (the network has no prior knowledge)
h = torch.zeros(batch_size, hidden_size)
C = torch.zeros(batch_size, hidden_size)

# Process a 5-timestep sequence
seq_len = 5
for t in range(seq_len):
    x_t = torch.randn(batch_size, input_size)  # Fake input at this timestep
    h, C = cell(x_t, h, C)
    print(f"Step {t+1}: h_t norm={h.norm():.4f}, C_t norm={C.norm():.4f}")

print(f"\nFinal hidden state shape: {h.shape}")  # (3, 20) — ready to pass to classifier
```

---

## Using PyTorch's Built-in LSTM

In practice, you use `nn.LSTM` which is highly optimized. The main difference from `nn.RNN` is that it returns **two** state tensors: `h_n` (hidden state) and `c_n` (cell state). You must initialize and pass both.

```python
# Stacked LSTM: 2 layers deep, with dropout between layers
lstm = nn.LSTM(
    input_size=10, 
    hidden_size=64, 
    num_layers=2,       # Stack 2 LSTM layers on top of each other
    batch_first=True,
    dropout=0.3         # Dropout applied between layers (not on the last layer)
)

x = torch.randn(8, 20, 10)  # (batch=8, seq_len=20, features=10)

# For LSTM, you need to initialize BOTH hidden and cell states
h0 = torch.zeros(2, 8, 64)  # (num_layers=2, batch=8, hidden=64)
c0 = torch.zeros(2, 8, 64)

# Pass both initial states as a tuple
output, (h_n, c_n) = lstm(x, (h0, c0))

print(f"Output (all timesteps): {output.shape}")  # (8, 20, 64) — useful for seq labeling
print(f"h_n (final hidden):     {h_n.shape}")     # (2, 8, 64) — one per layer
print(f"c_n (final cell):       {c_n.shape}")     # (2, 8, 64) — one per layer

# For classification, use the FINAL hidden state of the LAST layer:
last_hidden = h_n[-1]  # (8, 64) — the final timestep of layer 2
print(f"Feature vector for classifier: {last_hidden.shape}")
```

---

## The GRU: A Simpler Alternative

The GRU (Gated Recurrent Unit, Cho et al. 2014) is a streamlined LSTM. It merges the forget and input gates into a single **Update Gate**, and eliminates the separate cell state by merging it into the hidden state. The result is a model with fewer parameters that often performs comparably to an LSTM.

```
Update gate:  z_t = sigmoid(W_z · [h_{t-1}, x_t])
Reset gate:   r_t = sigmoid(W_r · [h_{t-1}, x_t])
Candidate:    n_t = tanh(W_n · [r_t * h_{t-1}, x_t])   ← reset gate masks old memory
New hidden:   h_t = (1 - z_t) * h_{t-1}  +  z_t * n_t
                     ↑                          ↑
              keep old memory             write new memory
```

The GRU's update gate `z_t` simultaneously decides how much old memory to forget AND how much new information to write. When `z_t ≈ 0`, it keeps old memory and ignores new input. When `z_t ≈ 1`, it completely replaces the hidden state. This is more elegant than the LSTM's separate forget and input gates.

```python
# In PyTorch, GRU has an identical API to RNN — no separate cell state
gru = nn.GRU(input_size=10, hidden_size=64, num_layers=2, 
             batch_first=True, dropout=0.3)

x = torch.randn(8, 20, 10)
h0 = torch.zeros(2, 8, 64)

# Only ONE state tensor (unlike LSTM which needs (h, c) tuple)
output, h_n = gru(x, h0)

print(f"GRU output: {output.shape}")  # (8, 20, 64)
print(f"GRU h_n:    {h_n.shape}")     # (2, 8, 64)
```

---

## When to Use What

| Model   | Parameters | Long-range memory | Speed | Best for |
|---------|-----------|-------------------|-------|----------|
| RNN     | Fewest    | Poor (< 10 steps) | Fast  | Toy examples, understanding concepts |
| GRU     | Medium    | Good              | Faster than LSTM | When dataset is small, quick experiments |
| LSTM    | Most      | Excellent         | Slower | Long sequences, when accuracy matters |
| Transformer | Varies | Perfect (all pairs) | Fastest on GPU | NLP, any modern production use case |

The honest truth: in modern NLP, **Transformers have almost entirely replaced LSTMs**. But understanding LSTMs is critical because (1) they still appear in time-series and audio tasks where sequential order is strict, and (2) the attention mechanism in Transformers was invented *to fix the bottleneck problem in Seq2Seq LSTM models*. You need to understand the problem to understand why the solution works.

---
## References
*   [Chris Olah: Understanding LSTMs](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — Must-read
*   [Original LSTM Paper: Hochreiter & Schmidhuber, 1997](https://www.bioinf.jku.at/publications/older/2604.pdf)
*   [GRU Paper: Cho et al., 2014](https://arxiv.org/abs/1406.1078)
