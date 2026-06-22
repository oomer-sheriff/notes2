# Step-by-Step: LSTM Cell — One Timestep with Actual Numbers

**Scenario:** A character-level model has seen `"ca"` and must update its memory state when it sees `"t"`.

**Dimensions:**  
- Input: `x_t` is a 2-dimensional vector (embedding of the character 't')  
- Hidden state: `h_t` is 3-dimensional (the model's "short-term memory")  
- Cell state: `C_t` is 3-dimensional (the model's "long-term memory")  

---

## 1. Inputs

```
Current input (embedding of 't'):
  x_t = [1.0, 0.5]          (shape: 2)

Previous hidden state (from 'a'):
  h_{t-1} = [0.3, -0.1, 0.7]   (shape: 3)

Previous cell state:
  C_{t-1} = [0.5, 0.2, -0.4]   (shape: 3)
```

In the LSTM, we always **concatenate** x_t and h_{t-1} into one vector:

```
combined = [x_t, h_{t-1}]
         = [1.0, 0.5, 0.3, -0.1, 0.7]    (shape: 5 = input_size + hidden_size)
```

Each gate is a Linear layer applied to this combined vector, plus a bias.

---

## 2. The Forget Gate — "What should we erase from memory?"

The forget gate asks: given what we just saw (`x_t`) and what we remember (`h_{t-1}`), what fraction of the old cell state should we keep?

**Gate weights and bias (2×5 matrix → 3 output dims):**
```
W_f = [[0.1, -0.2,  0.3,  0.1, -0.1],
       [0.2,  0.1, -0.1,  0.3,  0.2],
       [-0.1, 0.3,  0.2, -0.2,  0.1]]

b_f = [0.1, 0.0, -0.1]
```

**Compute pre-activation:**
```
z_f = W_f @ combined + b_f

Row 0: 0.1*1.0 + (-0.2)*0.5 + 0.3*0.3 + 0.1*(-0.1) + (-0.1)*0.7 + 0.1
     = 0.1 - 0.1 + 0.09 - 0.01 - 0.07 + 0.1
     = 0.11

Row 1: 0.2*1.0 + 0.1*0.5 + (-0.1)*0.3 + 0.3*(-0.1) + 0.2*0.7 + 0.0
     = 0.2 + 0.05 - 0.03 - 0.03 + 0.14 + 0.0
     = 0.33

Row 2: (-0.1)*1.0 + 0.3*0.5 + 0.2*0.3 + (-0.2)*(-0.1) + 0.1*0.7 + (-0.1)
     = -0.1 + 0.15 + 0.06 + 0.02 + 0.07 - 0.1
     = 0.10

z_f = [0.11, 0.33, 0.10]
```

**Apply Sigmoid (outputs values 0–1):**
```
σ(x) = 1 / (1 + e^(-x))

f_t[0] = σ(0.11) = 1/(1+e^(-0.11)) ≈ 0.527
f_t[1] = σ(0.33) = 1/(1+e^(-0.33)) ≈ 0.582
f_t[2] = σ(0.10) = 1/(1+e^(-0.10)) ≈ 0.525

f_t = [0.527, 0.582, 0.525]
```

**Interpretation:** All values are near 0.5, meaning the model will keep about 50% of each memory dimension. A trained model would output values closer to 0 (erase) or 1 (keep).

---

## 3. The Input Gate — "What new information should we write?"

The input gate has two sub-computations that work together.

**3a. Input gate i_t — WHICH cells to update:**
```
(Using simplified weights, same structure as forget gate)

z_i = [0.4, -0.2, 0.6]   (computed identically to z_f but with W_i)

i_t = σ(z_i) = [0.599, 0.450, 0.646]
```

**3b. Candidate values g_t — WHAT values to write:**
```
z_g = [0.7, 0.3, -0.5]   (computed with W_g)

g_t = tanh(z_g)           (tanh keeps values between -1 and 1)
    = [tanh(0.7), tanh(0.3), tanh(-0.5)]
    = [0.604, 0.291, -0.462]
```

**3c. What actually gets written (element-wise multiply):**
```
i_t * g_t = [0.599 * 0.604, 0.450 * 0.291, 0.646 * (-0.462)]
           = [0.362,         0.131,          -0.298]
```

This is the new information — scaled by how much the input gate allows.

---

## 4. Update the Cell State — The Conveyor Belt

The cell state `C_t` is updated by forgetting some old memory and adding new information:

```
C_t = f_t * C_{t-1}  +  i_t * g_t
    = (forget old)   +  (write new)

f_t * C_{t-1}:
  [0.527 * 0.5,  0.582 * 0.2,  0.525 * (-0.4)]
= [0.264,        0.116,         -0.210]

i_t * g_t:
= [0.362,        0.131,         -0.298]

C_t = [0.264+0.362, 0.116+0.131, -0.210+(-0.298)]
    = [0.626,        0.247,        -0.508]
```

The cell state has been updated. Memory dimensions 0 and 1 increased slightly. Dimension 2 became more negative.

---

## 5. The Output Gate — "What do we expose as the hidden state?"

```
z_o = [0.5, 0.1, 0.3]   (computed with W_o)

o_t = σ(z_o) = [0.622, 0.525, 0.574]
```

**Compute new hidden state:**
```
h_t = o_t * tanh(C_t)

tanh(C_t):
  tanh(0.626)  = 0.556
  tanh(0.247)  = 0.243
  tanh(-0.508) = -0.469

o_t * tanh(C_t):
  [0.622*0.556, 0.525*0.243, 0.574*(-0.469)]
= [0.346,       0.128,       -0.269]

h_t = [0.346, 0.128, -0.269]
```

---

## 6. Summary: One LSTM Step

```
BEFORE processing 't':                AFTER processing 't':
  x_t     = [1.0, 0.5]     (input)
  h_{t-1} = [0.3, -0.1, 0.7]         h_t = [0.346, 0.128, -0.269]
  C_{t-1} = [0.5, 0.2, -0.4]         C_t = [0.626, 0.247, -0.508]

Gates that controlled the update:
  Forget gate f_t = [0.527, 0.582, 0.525]   (kept ~55% of old memory)
  Input gate  i_t = [0.599, 0.450, 0.646]   (how much of new info to write)
  Candidate   g_t = [0.604, 0.291, -0.462]  (proposed new memory values)
  Output gate o_t = [0.622, 0.525, 0.574]   (how much of C_t to expose)
```

---

## 7. How This Handles Long-Range Dependencies

Suppose 100 timesteps earlier the model saw `"the cat"`. The forget gate for the "subject=cat" memory dimension learned to output `f ≈ 1.0` for all non-subject tokens. That means:

```
After 100 steps: C[subject_dim] ≈ 0.5 * (1.0)^100 + ... ≈ 0.5 (mostly preserved!)
```

In a vanilla RNN: the gradient flowing backwards through 100 timesteps of `tanh` multiplications would be `~0.5^100 ≈ 10^{-30}` — completely vanished. The LSTM cell state gradient only multiplies by `f_t` (the forget gate), which can be close to 1.0 if the memory was relevant, allowing the gradient to survive.

---

## Key Takeaways

| Gate | Formula | Sigmoid/Tanh? | Controls |
|---|---|---|---|
| Forget `f_t` | σ(W_f·[h,x]+b) | Sigmoid (0–1) | How much of C_{t-1} to keep |
| Input `i_t` | σ(W_i·[h,x]+b) | Sigmoid (0–1) | Which cells in C to update |
| Candidate `g_t` | tanh(W_g·[h,x]+b) | Tanh (-1 to 1) | What new values to potentially write |
| Output `o_t` | σ(W_o·[h,x]+b) | Sigmoid (0–1) | What portion of C_t to expose as h_t |
| Cell state `C_t` | f_t⊙C_{t-1} + i_t⊙g_t | — | The "conveyor belt" long-term memory |
| Hidden state `h_t` | o_t⊙tanh(C_t) | — | Short-term output passed to next step |
