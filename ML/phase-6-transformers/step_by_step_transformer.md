# Step-by-Step: Transformer (GPT-Style) — Full Walkthrough with Numbers

This is a complete numerical trace through one Transformer block, expanding on the example you provided. We use tiny dimensions so every number can be verified by hand.

**Setup:**  
- Vocabulary: `{cat=1, sat=2, on=3, mat=4}`  
- Sentence: `"cat sat on mat"` → token IDs: `[1, 2, 3, 4]`  
- Sequence length: `T = 4`  
- Embedding dimension: `d_model = 2`  
- Attention heads: `1` (single-head to keep numbers manageable)  
- `d_k = d_model = 2`  

---

## 1. Token Embeddings

Each token ID maps to a 2D vector via the embedding table:

```
Token embedding table E:
  token 1 (cat) → [1.0, 0.0]
  token 2 (sat) → [0.0, 1.0]
  token 3 (on)  → [1.0, 1.0]
  token 4 (mat) → [2.0, 1.0]

X = E[[1,2,3,4]] =
  [[1.0, 0.0],   ← cat
   [0.0, 1.0],   ← sat
   [1.0, 1.0],   ← on
   [2.0, 1.0]]   ← mat

Shape: (T=4, d_model=2)
```

---

## 2. Positional Embeddings

The Transformer has no inherent sense of order — the self-attention operation is a set operation. We add a position-specific vector to each token so the model knows "I am at position 2."

```
Positional embedding table P:
  position 0 → [0.1, 0.0]
  position 1 → [0.0, 0.1]
  position 2 → [0.1, 0.1]
  position 3 → [0.2, 0.1]

H0 = X + P:
  cat + pos0: [1.0+0.1, 0.0+0.0] = [1.1, 0.0]
  sat + pos1: [0.0+0.0, 1.0+0.1] = [0.0, 1.1]
  on  + pos2: [1.0+0.1, 1.0+0.1] = [1.1, 1.1]
  mat + pos3: [2.0+0.2, 1.0+0.1] = [2.2, 1.1]

H0 =
  [[1.1, 0.0],
   [0.0, 1.1],
   [1.1, 1.1],
   [2.2, 1.1]]

Shape: (4, 2) — same as X but now each row encodes WHAT + WHERE
```

---

## 3. Pre-LayerNorm

Modern GPT applies LayerNorm **before** each sub-layer (Pre-LN style).

**LayerNorm formula:**  
`LN(x) = (x - μ) / σ` (then scale + shift with learned γ, β — we assume γ=1, β=0 here)

**For cat's embedding `[1.1, 0.0]`:**
```
μ = (1.1 + 0.0) / 2 = 0.55
σ² = ((1.1-0.55)² + (0.0-0.55)²) / 2 = (0.3025 + 0.3025) / 2 = 0.3025
σ  = √0.3025 = 0.55

LN([1.1, 0.0]) = [(1.1-0.55)/0.55, (0.0-0.55)/0.55]
               = [1.0, -1.0]
```

**For sat's embedding `[0.0, 1.1]` (symmetric):**
```
μ = 0.55, σ = 0.55
LN([0.0, 1.1]) = [-1.0, 1.0]
```

**For on's embedding `[1.1, 1.1]`:**
```
μ = 1.1, σ² = ((1.1-1.1)² + (1.1-1.1)²)/2 = 0, σ = 0
→ Both values are equal, LN is undefined (or [0, 0] with ε stabilization)
LN([1.1, 1.1]) ≈ [0.0, 0.0]   (all same values → zero after normalization)
```

**For mat's embedding `[2.2, 1.1]`:**
```
μ = (2.2 + 1.1)/2 = 1.65
σ² = ((2.2-1.65)² + (1.1-1.65)²) / 2 = (0.3025 + 0.3025) / 2 = 0.3025
σ  = 0.55

LN([2.2, 1.1]) = [(2.2-1.65)/0.55, (1.1-1.65)/0.55]
               = [1.0, -1.0]
```

```
LN(H0) =
  [[ 1.0, -1.0],   ← cat
   [-1.0,  1.0],   ← sat
   [ 0.0,  0.0],   ← on
   [ 1.0, -1.0]]   ← mat
```

---

## 4. Compute Q, K, V

We project LN(H0) into Query, Key, Value spaces using learned weight matrices.

```
W_Q = [[1, 0],   (identity — Q = LN(H0))
       [0, 1]]

W_K = [[1, 1],
       [0, 1]]

W_V = [[1, 0],
       [1, 1]]
```

**Q = LN(H0) @ W_Q** (identity, so Q = LN(H0)):
```
Q =
  [[ 1.0, -1.0],
   [-1.0,  1.0],
   [ 0.0,  0.0],
   [ 1.0, -1.0]]
```

**K = LN(H0) @ W_K** (row-by-row: [q1, q2] @ [[1,1],[0,1]] = [q1, q1+q2]):
```
cat:  [1.0, -1.0] @ W_K → [1*1+(-1)*0, 1*1+(-1)*1] = [1, 0]
sat:  [-1.0, 1.0] @ W_K → [-1, 0]
on:   [0.0, 0.0]  @ W_K → [0, 0]
mat:  [1.0, -1.0] @ W_K → [1, 0]

K =
  [[ 1,  0],
   [-1,  0],
   [ 0,  0],
   [ 1,  0]]
```

**V = LN(H0) @ W_V** ([q1, q2] @ [[1,0],[1,1]] = [q1+q2, q2]):
```
cat:  [1.0, -1.0] → [1+(-1), -1] = [0, -1]
sat:  [-1.0, 1.0] → [-1+1, 1]   = [0,  1]
on:   [0.0, 0.0]  → [0, 0]      = [0,  0]
mat:  [1.0, -1.0] → [0, -1]     = [0, -1]

V =
  [[ 0, -1],
   [ 0,  1],
   [ 0,  0],
   [ 0, -1]]
```

---

## 5. Raw Attention Scores: S = Q @ K.T

Shape: (4, 2) @ (2, 4) = (4, 4). Entry S[i,j] = "how much does token i want to attend to token j?"

```
Row 0 (cat query = [1,-1]) dot each key:
  key0=[1,0]:   1*1 + (-1)*0  =  1
  key1=[-1,0]:  1*(-1)+(-1)*0 = -1
  key2=[0,0]:   0              =  0
  key3=[1,0]:   1              =  1
  → S[0] = [1, -1, 0, 1]

Row 1 (sat query = [-1,1]):
  key0=[1,0]:  -1             = -1
  key1=[-1,0]:  1             =  1
  key2=[0,0]:   0             =  0
  key3=[1,0]:  -1             = -1
  → S[1] = [-1, 1, 0, -1]

Row 2 (on query = [0,0]):
  All dots = 0
  → S[2] = [0, 0, 0, 0]

Row 3 (mat query = [1,-1]):
  Same as row 0
  → S[3] = [1, -1, 0, 1]

S =
  [[ 1, -1,  0,  1],
   [-1,  1,  0, -1],
   [ 0,  0,  0,  0],
   [ 1, -1,  0,  1]]
```

---

## 6. Scale by √d_k

`d_k = 2`, `√2 ≈ 1.414`

```
S_scaled = S / 1.414

Row 0: [ 0.707, -0.707, 0.000, 0.707]
Row 1: [-0.707,  0.707, 0.000,-0.707]
Row 2: [ 0.000,  0.000, 0.000, 0.000]
Row 3: [ 0.707, -0.707, 0.000, 0.707]
```

---

## 7. Apply Causal Mask (GPT Only)

Token at position i can only attend to positions 0..i (no future peeking).

```
Causal mask (lower-triangular, 0=blocked):
  [[1, 0, 0, 0],
   [1, 1, 0, 0],
   [1, 1, 1, 0],
   [1, 1, 1, 1]]

Blocked positions get score = -∞:

Masked scores:
  Row 0: [ 0.707,   -∞,     -∞,    -∞  ]   ← cat only sees itself
  Row 1: [-0.707,  0.707,   -∞,    -∞  ]   ← sat sees cat, sat
  Row 2: [ 0.000,  0.000, 0.000,   -∞  ]   ← on sees cat, sat, on
  Row 3: [ 0.707, -0.707, 0.000, 0.707]    ← mat sees all 4
```

---

## 8. Softmax Along Key Dimension

`softmax([a, -∞, -∞, -∞]) = [1, 0, 0, 0]` because e^(-∞) = 0.

**Row 0 (cat):** `softmax([0.707, -∞, -∞, -∞]) = [1.0, 0, 0, 0]`

**Row 1 (sat):** `softmax([-0.707, 0.707, -∞, -∞])`
```
e^(-0.707) = 0.493
e^(0.707)  = 2.028
sum = 2.521

softmax = [0.493/2.521, 2.028/2.521, 0, 0]
        = [0.196, 0.804, 0, 0]
```

**Row 2 (on):** `softmax([0, 0, 0, -∞])`
```
e^0 = 1 (three of them), sum = 3
softmax = [0.333, 0.333, 0.333, 0]
```

**Row 3 (mat):** `softmax([0.707, -0.707, 0, 0.707])`
```
e^0.707  = 2.028
e^-0.707 = 0.493
e^0      = 1.0
sum      = 2.028 + 0.493 + 1.0 + 2.028 = 5.549

softmax = [2.028/5.549, 0.493/5.549, 1.0/5.549, 2.028/5.549]
        = [0.365, 0.089, 0.180, 0.365]
```

```
Attention weights A:
  [[1.000, 0.000, 0.000, 0.000],   ← cat only sees itself
   [0.196, 0.804, 0.000, 0.000],   ← sat mostly attends to sat
   [0.333, 0.333, 0.333, 0.000],   ← on equally attends to cat/sat/on
   [0.365, 0.089, 0.180, 0.365]]   ← mat splits between cat, on, mat
```

---

## 9. Weighted Sum of Values: Z = A @ V

V shape: (4, 2). A shape: (4, 4). Z shape: (4, 2).

**Row 0 (cat):** `1.0*V[0] = 1.0*[0,-1] = [0, -1]`

**Row 1 (sat):**
```
0.196*V[0] + 0.804*V[1]
= 0.196*[0,-1] + 0.804*[0,1]
= [0, -0.196] + [0, 0.804]
= [0, 0.608]
```

**Row 2 (on):**
```
0.333*V[0] + 0.333*V[1] + 0.333*V[2]
= 0.333*[0,-1] + 0.333*[0,1] + 0.333*[0,0]
= [0, -0.333] + [0, 0.333] + [0, 0]
= [0, 0.000]
```

**Row 3 (mat):**
```
0.365*[0,-1] + 0.089*[0,1] + 0.180*[0,0] + 0.365*[0,-1]
= [0, -0.365] + [0, 0.089] + [0, 0] + [0, -0.365]
= [0, -0.641]
```

```
Z (attention output) =
  [[ 0, -1.000],   ← cat
   [ 0,  0.608],   ← sat
   [ 0,  0.000],   ← on
   [ 0, -0.641]]   ← mat
```

---

## 10. Output Projection + Residual Connection

**Output projection** (W_O = identity for simplicity): `O = Z`

**Residual add:** `H1 = H0 + O`
```
cat: [1.1, 0.0] + [0, -1.000] = [1.1, -1.000]
sat: [0.0, 1.1] + [0,  0.608] = [0.0,  1.708]
on:  [1.1, 1.1] + [0,  0.000] = [1.1,  1.100]
mat: [2.2, 1.1] + [0, -0.641] = [2.2,  0.459]

H1 =
  [[1.1, -1.000],
   [0.0,  1.708],
   [1.1,  1.100],
   [2.2,  0.459]]
```

The residual connection means the token representations only need to learn the **change** (residual), not the full new representation from scratch.

---

## 11. Feed-Forward Network

Apply another LayerNorm, then a 2-layer MLP to each token independently.

**FFN for cat's representation `[1.1, -1.0]`:**
```
W1 = [[1, 0, 1, 0],    (d_model=2 → d_ff=4)
      [0, 1, 0, 1]]

h = [1.1, -1.0] @ W1.T + b1
  = [1*1.1+0*(-1.0), 0*1.1+1*(-1.0), 1*1.1+0*(-1.0), 0*1.1+1*(-1.0)]
  = [1.1, -1.0, 1.1, -1.0]

GELU(h):  ≈ [0.92, -0.16, 0.92, -0.16]

W2 = [[1, 0],          (d_ff=4 → d_model=2)
      [0, 1],
      [1, 0],
      [0, 1]]

output = GELU(h) @ W2 + b2
       = [0.92+0.92, -0.16+(-0.16)]
       = [1.84, -0.32]
```

**Second Residual:**
```
H2_cat = H1_cat + FFN(H1_cat) = [1.1, -1.0] + [1.84, -0.32] = [2.94, -1.32]
```

---

## 12. What Changed After One Block?

```
cat representation:
  Input  H0: [1.1, 0.0]      (embedding + position only)
  After attn H1: [1.1, -1.0]  (pulled value from itself: V[cat]=[0,-1])
  After FFN H2: [2.94, -1.32] (non-linear transformation applied)

sat representation:
  Input  H0: [0.0, 1.1]
  After attn H1: [0.0, 1.708]  (attended 80% to sat's own V=[0,1])
  After FFN H2: (would be computed similarly)

mat representation:
  Input  H0: [2.2, 1.1]
  After attn H1: [2.2, 0.459]  (split attention across cat, on, mat — all have similar values)
  After FFN H2: (computed similarly)
```

After `N` such blocks (GPT-2: N=12, GPT-3: N=96), each token's representation has gathered information from all relevant past tokens.

---

## 13. Generating the Next Token (Inference)

After all N blocks, we take the **last token's** final representation and project it to vocabulary logits:

```
mat final representation → h_mat = [2.2, 0.459]  (simplified example)

Logit layer: h_mat @ W_vocab.T   (W_vocab shape: vocab_size × d_model)
→ one logit score per vocabulary token

softmax(logits) → probability distribution over next word
argmax → predict "sat" (or sample from distribution)
```

The model predicts: after "cat sat on mat", the next token might be "."

---

## Key Takeaways

| Step | Why it exists |
|---|---|
| Token + Pos embedding | Encodes WHAT the token is and WHERE it is |
| LayerNorm (Pre) | Stabilizes activations before each sublayer |
| Q, K, V projections | Different "views" of the same token for attending |
| QK^T scores | How relevant is each key to this query |
| √d_k scaling | Prevents softmax from collapsing to one-hot |
| Causal mask | Prevents "cheating" by looking at future tokens |
| Softmax weights | Turn scores into probability-like attention weights |
| A @ V | Weighted average of value vectors (information retrieval) |
| Residual H0 + Z | Gradient highway; model only needs to learn the delta |
| Feed-Forward | Non-linear transformation; stores factual knowledge |
| Repeat N times | Each layer refines contextual understanding deeper |
