# Task P6-3: Build and Train a Mini-GPT (🔥 The Big One)

**Goal:** Build a complete GPT-style character-level language model from scratch and train it on Shakespeare. You should understand every single line of code.

This is the most important homework in the entire curriculum. Andrej Karpathy calls this the "GPT from scratch" video. Follow along, then implement it yourself.

Create a Jupyter Notebook in `homework/lab-files/`.

---

## Prerequisites

Review `03_building_gpt_from_scratch.md` first. This homework is an extension of it.

## Part 1: Implement MiniGPT from Memory

Without copying from the concept notes, implement these classes in order:
1. `CausalSelfAttention` — must use a pre-built causal mask registered as a buffer
2. `GPTBlock` — Pre-LayerNorm style, no Post-LN
3. `MiniGPT` — Full model with weight tying between token embedding and `lm_head`

**Check your implementation passes these assertions:**
```python
model = MiniGPT(vocab_size=65, d_model=64, n_heads=4, n_layers=3, max_seq_len=128)

x = torch.randint(0, 65, (2, 50))
logits, loss = model(x, x)

assert logits.shape == (2, 50, 65), f"Wrong shape: {logits.shape}"

# Initial loss should be close to ln(vocab_size) = ln(65) ≈ 4.17
# (random weights → uniform distribution over vocab)
assert 3.5 < loss.item() < 5.0, f"Initial loss is weird: {loss.item()}"

print("All assertions passed!")
```

## Part 2: Train on Shakespeare

Use the training code from `03_building_gpt_from_scratch.md`. Train with these settings on Google Colab (use GPU!):

```python
model = MiniGPT(
    vocab_size  = vocab_size,  # ~65 for character-level
    d_model     = 256,
    n_heads     = 8,
    n_layers    = 6,
    max_seq_len = 256,
    dropout     = 0.2
)

# Training config
BATCH_SIZE = 64
SEQ_LEN    = 256
LR         = 3e-4
MAX_STEPS  = 5000
```

Track and plot **both training loss AND validation loss** at every 500 steps. If the validation loss starts increasing while training loss decreases, you are overfitting.

## Part 3: Generate Text

Generate 4 different text samples:
```python
temperatures = [0.5, 0.8, 1.0, 1.3]
for temp in temperatures:
    seed = torch.zeros((1, 1), dtype=torch.long, device=device)
    generated = model.generate(seed, max_new_tokens=200, temperature=temp, top_k=40)
    print(f"\n=== Temperature {temp} ===")
    print(decode(generated[0].tolist()))
```

## Part 4: Scale It Up (Challenge)

Scaling laws: bigger models trained on more data perform better. Experiment with:

| Config | d_model | n_heads | n_layers | Params |
|--------|---------|---------|----------|--------|
| nano   | 64      | 4       | 3        | ~0.3M  |
| small  | 128     | 4       | 4        | ~1.2M  |
| medium | 256     | 8       | 6        | ~9M    |
| large  | 512     | 8       | 8        | ~48M   |

Train each for the same number of steps. Plot final validation loss vs parameter count. You should observe that more parameters → lower loss. This is the empirical scaling law.

## Questions to Answer

1. What is **weight tying** between `token_emb` and `lm_head`? Why does it work conceptually?
2. At `temperature=0.5`, the text is more coherent but repetitive. At `temperature=1.3`, it's creative but garbled. Why? (Hint: think about what temperature does to the logit distribution.)
3. At what step does your training loss roughly stop improving? What does this tell you about the amount of data vs model capacity?
