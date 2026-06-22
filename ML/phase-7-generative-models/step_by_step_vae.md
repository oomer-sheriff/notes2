# Step-by-Step: Variational Autoencoder (VAE)

**Scenario:** We have a tiny 1D "image" of 2 pixels. We want to encode it into a 1D latent space (just a single number) and reconstruct it.

**Input:** `x = [0.8, 0.2]` (Shape: 2)

---

## 1. The Encoder (Outputting Parameters)

Unlike a standard autoencoder that outputs a single latent value `z`, a VAE outputs two parameters describing a normal distribution:
- `μ` (mean)
- `log(σ²)` (log variance — we use log variance so the network can output negative numbers without breaking the math)

Let's assume our trained encoder outputs:
```
μ = 1.5
log(σ²) = -1.0
```

---

## 2. Converting Log Variance to Standard Deviation

We need `σ` (standard deviation) to sample from the distribution.

```
σ² = exp(log(σ²)) = exp(-1.0) ≈ 0.368
σ = √0.368 ≈ 0.607
```

Our latent distribution for this specific input is $N(1.5, \ 0.368)$.

---

## 3. The Reparameterization Trick (Sampling)

We need to draw a sample `z` from this distribution, but we *must* do it in a way that allows gradients to flow backwards through `μ` and `σ`.

If we just call `z = random.normal(mu, sigma)`, the gradient stops at the random function.

**The Trick:** Sample `ε` from a standard normal $N(0,1)$ (which has no learnable parameters), then shift and scale it.

1. **Sample ε:** `ε = 0.4` (Drawn randomly from $N(0,1)$ during this forward pass)
2. **Compute z:**
   ```
   z = μ + σ * ε
   z = 1.5 + (0.607 * 0.4)
   z = 1.5 + 0.243
   z = 1.743
   ```

`z = 1.743` is the actual latent code we feed into the decoder.

---

## 4. The Decoder (Reconstruction)

Let's assume the decoder has a simple weight matrix `W_dec = [0.5, -0.2]` and no bias, followed by a Sigmoid to keep outputs between 0 and 1.

```
Pre-activation = z * W_dec
               = 1.743 * [0.5, -0.2]
               = [0.871, -0.349]

Output x̂ = Sigmoid([0.871, -0.349])
         = [1 / (1 + e^(-0.871)), 1 / (1 + e^(0.349))]
         = [0.705, 0.414]
```

---

## 5. Computing the Loss

The VAE loss has two parts:

### A. Reconstruction Loss (How close is x̂ to x?)
Using Mean Squared Error (MSE):
```
x = [0.8, 0.2]
x̂ = [0.705, 0.414]

Error = [(0.8 - 0.705)², (0.2 - 0.414)²]
      = [0.009, 0.046]

MSE = (0.009 + 0.046) / 2 = 0.0275
```

### B. KL Divergence (How close is our latent distribution to N(0,1)?)
We want to penalize the encoder if it outputs a `μ` far from 0, or a `σ²` far from 1.
The formula for a single dimension is:
`KL = -0.5 * (1 + log(σ²) - μ² - σ²)`

Plugging in our values:
```
KL = -0.5 * (1 + (-1.0) - (1.5)² - 0.368)
   = -0.5 * (0 - 2.25 - 0.368)
   = -0.5 * (-2.618)
   = 1.309
```

### Total Loss
```
Total Loss = Reconstruction Loss + KL Divergence
           = 0.0275 + 1.309
           = 1.3365
```

---

## 6. Backpropagation (Why the Trick Matters)

When we compute $\frac{\partial \text{Loss}}{\partial \mu}$ and $\frac{\partial \text{Loss}}{\partial \sigma}$, the gradient flows perfectly backwards through `z` because `z = μ + σ * ε` is just a simple addition and multiplication. The randomness `ε` is treated as a constant during backprop.

---
## Key Takeaways

| Concept | What it does |
|---|---|
| Encoder outputs | `μ` and `log(σ²)` instead of a direct latent vector. |
| Reparameterization | `z = μ + σ * ε`. Keeps the randomness outside the gradient path. |
| KL Divergence Loss | Forces the latent space to form a nice, dense cluster around 0, rather than spreading out into disjoint islands. |
| Generative capability | Because the KL loss forces the latent space to look like $N(0,1)$, we can later discard the encoder, sample $z \sim N(0,1)$, and decode it to generate brand new data! |
