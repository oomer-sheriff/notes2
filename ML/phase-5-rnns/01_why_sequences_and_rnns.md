# Why Sequences are Different: The Case for RNNs

## The Problem with MLPs and CNNs on Sequential Data

Both MLPs and CNNs require **fixed-size inputs**. A CNN trained on 32×32 images crashes if you give it a 33×32 image. But natural language, audio, and time series data are inherently **variable-length**. A sentence can be 5 words or 500 words. You cannot predefine a fixed input size for this.

Even if you could pad everything to the same length, a deeper problem remains: **order matters in sequences but not in fixed inputs**. The sentence "The dog bit the man" and "The man bit the dog" contain the exact same words. An MLP operating on a bag-of-words would see them as identical. But they have opposite meanings. The network must know that token position carries critical information.

CNNs handle local spatial relationships (nearby pixels), but they don't have a way to carry information from the beginning of a long sequence all the way to the end. A sentence like "The cat, which had been sitting in the corner ever since it arrived, was hungry" requires the network to link "was hungry" back to "The cat" across 14 tokens of noise.

---

## The Recurrent Neural Network (RNN)

The RNN solution is elegant: at each step, the network doesn't just process the current input — it also takes a **hidden state** from the previous step. This hidden state is a compressed memory of everything the network has seen so far.

```
Step 1:   x₁  →  [RNN]  →  h₁
                    ↑
                   h₀ (zeros initially)

Step 2:   x₂  →  [RNN]  →  h₂
                    ↑
                   h₁ (from step 1)

Step 3:   x₃  →  [RNN]  →  h₃
                    ↑
                   h₂ (from step 2)
```

The crucial insight is that **the same weight matrices are used at every timestep**. The RNN doesn't learn one set of weights for position 1 and another for position 2. It learns a general rule for "how should I update my memory given a new input?" This is called **parameter sharing** and is what allows the RNN to handle sequences of any length.

The update equations at each timestep are:
```
h_t = tanh(W_h · h_{t-1}  +  W_x · x_t  +  b)
y_t = W_y · h_t
```

`W_h` learns how much of the previous memory to carry forward. `W_x` learns how to incorporate the new input. `tanh` squishes the result to `[-1, 1]` to prevent values exploding. `y_t` is the output at this timestep (the prediction for this position in the sequence).

---

## Implementing the RNN Math by Hand

Before we use PyTorch's built-in RNN, let's implement it from scratch so you can see there is truly no magic:

```python
import torch
import torch.nn as nn
import numpy as np

# --- Hand-implemented RNN cell ---
# Imagine a tiny vocabulary: [a=0, b=1, c=2]
# We'll process the sequence [a, b, c] one token at a time

input_size  = 3   # Vocabulary size (one-hot encoded inputs)
hidden_size = 4   # Dimension of the hidden state vector
output_size = 3   # Output one prediction per class

torch.manual_seed(42)

# These are the learnable weights. In a real RNN, these are nn.Parameters.
W_x = torch.randn(input_size, hidden_size)   # Input → Hidden
W_h = torch.randn(hidden_size, hidden_size)  # Hidden → Hidden (the memory)
b   = torch.zeros(hidden_size)               # Bias
W_y = torch.randn(hidden_size, output_size)  # Hidden → Output

# Start with zero hidden state (no prior knowledge)
h = torch.zeros(hidden_size)

# Process three timesteps of a sequence
sequence = [
    torch.tensor([1., 0., 0.]),  # Token 'a' (one-hot)
    torch.tensor([0., 1., 0.]),  # Token 'b' (one-hot)
    torch.tensor([0., 0., 1.]),  # Token 'c' (one-hot)
]

print("Processing sequence step by step:")
for t, x_t in enumerate(sequence):
    # The core RNN equation: new hidden state mixes current input and prior memory
    h = torch.tanh(x_t @ W_x  +  h @ W_h  +  b)
    y = h @ W_y  # Output for this timestep
    
    print(f"  Timestep {t+1}: h_t norm={h.norm():.3f}, "
          f"output logits={[f'{v:.2f}' for v in y.tolist()]}")

print(f"\nFinal hidden state (this encodes the whole sequence): {h.detach().numpy().round(3)}")
```

---

## Using PyTorch's Built-in RNN

Writing the loop manually works but is slow and doesn't run on a GPU efficiently. PyTorch's `nn.RNN` runs the same computation but fused into optimized CUDA kernels. The API takes the entire sequence at once and returns the output at each timestep plus the final hidden state.

```python
# batch_first=True means input shape is (Batch, Sequence, Features)
# instead of the default (Sequence, Batch, Features)
rnn_layer = nn.RNN(input_size=10, hidden_size=32, num_layers=1, batch_first=True)

# Simulate a batch of 4 sentences, each 15 tokens long, each token a 10-dim vector
batch_size  = 4
seq_length  = 15
input_dim   = 10

x = torch.randn(batch_size, seq_length, input_dim)  # (4, 15, 10)

# The RNN processes all 15 timesteps at once internally
# output: hidden state at EVERY timestep — shape (4, 15, 32)
# h_n:   hidden state at the FINAL timestep only — shape (1, 4, 32)
output, h_n = rnn_layer(x)

print(f"Input shape:  {x.shape}")
print(f"Output shape: {output.shape}")  # (Batch=4, Seq=15, Hidden=32)
print(f"h_n shape:    {h_n.shape}")     # (NumLayers=1, Batch=4, Hidden=32)

# For sequence classification (e.g. sentiment analysis), 
# you typically only need the LAST hidden state h_n:
final_hidden = h_n.squeeze(0)  # Remove the layers dimension -> (4, 32)
print(f"Final hidden for classification: {final_hidden.shape}")
```

---

## The Vanishing Gradient Problem

RNNs suffer badly from a fundamental flaw. During backpropagation through time (BPTT), the gradient must flow backwards through every timestep. Each step involves multiplying by `W_h` and the derivative of `tanh`.

The derivative of `tanh` is at most `1.0` and usually much less (close to zero when the input is large or very negative). So at each timestep, the gradient gets multiplied by something less than 1. Over 50 timesteps, you're multiplying 50 small numbers together, and the gradient shrinks exponentially toward zero.

**The result:** An RNN trained on a 50-word sentence cannot learn long-range dependencies. The gradient signal from the word at position 1 essentially disappears by the time it reaches the weights that processed the early words. The network effectively has a **short-term memory** of only ~10 timesteps in practice.

```python
# Visualize how a gradient decays over timesteps
# If the gradient at each step is multiplied by 0.8:
grad = 1.0
decay_factor = 0.8

print("Gradient magnitude at each timestep (flowing backwards):")
for step in range(20):
    print(f"  Timestep -{step+1}: {grad:.6f}")
    grad *= decay_factor  # Simulate one step of gradient flow

# After 20 steps, the gradient is 0.8^20 ≈ 0.012 — almost gone
# After 50 steps, it's 0.8^50 ≈ 0.000143 — completely vanished
```

The **exploding gradient** problem is the opposite — if weights are large, the gradient grows exponentially and training becomes numerically unstable. The fix for exploding gradients is simple: **gradient clipping** (cap the gradient norm at a maximum value). The fix for vanishing gradients requires a fundamentally different architecture: the LSTM.

```python
# Gradient clipping in PyTorch — always use this when training RNNs/LSTMs
optimizer = torch.optim.Adam(rnn_layer.parameters(), lr=0.001)

# After loss.backward(), before optimizer.step():
# This clips the gradient norm to at most 1.0, preventing explosions
torch.nn.utils.clip_grad_norm_(rnn_layer.parameters(), max_norm=1.0)
```

---
## References
*   [Chris Olah: Understanding LSTMs](https://colah.github.io/posts/2015-08-Understanding-LSTMs/) — The definitive visual explanation
*   [Andrej Karpathy: The Unreasonable Effectiveness of Recurrent Neural Networks](http://karpathy.github.io/2015/05/21/rnn-effectiveness/)
*   [Stanford CS224n: NLP with Deep Learning](https://web.stanford.edu/class/cs224n/)
