# Diffusion Models

Diffusion models are the current state-of-the-art for image generation (DALL-E, Midjourney, Stable Diffusion). They completely replaced GANs because they are easier to train (no adversarial instability) and offer much finer control over generation.

## The Core Idea

Instead of generating an image from noise in one single step (like a GAN or VAE), a diffusion model does it iteratively in hundreds of tiny steps.

1. **Forward Process (Destruction):** Take a real image and gradually add Gaussian noise over $T$ steps (e.g., $T=1000$) until it becomes pure static. This process requires no training; it's a fixed mathematical formula.
2. **Reverse Process (Creation):** Train a neural network (typically a U-Net) to predict the noise that was added at each step. By subtracting the predicted noise, we can start with pure static and iteratively denoise it back into a real image.

```
Forward:  x₀ (real) → x₁ → x₂ → ... → x_{T} (pure noise)
Reverse:  x_{T} (noise) → x_{T-1} → ... → x₁ → x₀ (generated image)
```

---

## 1. The Forward Process (Adding Noise)

At step $t$, we add a tiny bit of noise to $x_{t-1}$. The variance schedule $\beta_t$ controls how much noise is added.
$x_t = \sqrt{1 - \beta_t} x_{t-1} + \sqrt{\beta_t} \epsilon$  where $\epsilon \sim \mathcal{N}(0, I)$

**The Diffusion Trick:** We don't actually have to iterate step-by-step to get $x_t$. Through a mathematical shortcut (using $\alpha_t = 1 - \beta_t$ and $\bar{\alpha}_t = \prod_{i=1}^t \alpha_i$), we can jump directly from the clean image $x_0$ to any step $t$:

$x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon$

```python
import torch
import numpy as np

# A simple linear noise schedule
T = 1000
beta = torch.linspace(1e-4, 0.02, T)  # Small noise at start, larger at end
alpha = 1.0 - beta
alpha_bar = torch.cumprod(alpha, dim=0)

def forward_diffusion(x_0, t):
    """
    Jumps directly from clean image x_0 to noisy image x_t at timestep t.
    """
    noise = torch.randn_like(x_0)  # Random Gaussian noise
    
    # Get the scaling factors for timestep t
    sqrt_alpha_bar = torch.sqrt(alpha_bar[t])
    sqrt_one_minus_alpha_bar = torch.sqrt(1.0 - alpha_bar[t])
    
    # Create the noisy image
    x_t = sqrt_alpha_bar * x_0 + sqrt_one_minus_alpha_bar * noise
    return x_t, noise
```

---

## 2. The Neural Network (U-Net)

The network takes two inputs:
1. The noisy image $x_t$
2. The current timestep $t$ (injected via sinusoidal positional embeddings, exactly like in Transformers, so the network knows "how noisy" the image is supposed to be)

The network outputs:
- The predicted noise $\epsilon_\theta(x_t, t)$ that was added to make $x_t$.

The backbone is almost always a **U-Net** (from Phase 4 segmentation) but augmented with self-attention layers (from Phase 6) at the lower resolutions.

---

## 3. Training: Astonishingly Simple

The loss function for a diffusion model is incredibly simple: Mean Squared Error between the *actual* noise added in the forward pass, and the *predicted* noise from the U-Net.

```python
import torch.nn.functional as F

# Pseudocode for the training loop
# Assume `model` is our U-Net
optimizer = torch.optim.Adam(model.parameters(), lr=1e-4)

for x_0 in dataloader:  # Batch of real images
    batch_size = x_0.size(0)
    
    # 1. Pick a random timestep t for each image in the batch
    t = torch.randint(0, T, (batch_size,))
    
    # 2. Corrupt the image to timestep t
    x_t, true_noise = forward_diffusion(x_0, t)
    
    # 3. Predict the noise using the U-Net
    predicted_noise = model(x_t, t)
    
    # 4. Compute Loss (MSE)
    loss = F.mse_loss(predicted_noise, true_noise)
    
    # 5. Backprop
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

That's it! No discriminator, no min-max game, no KL divergence. Just "predict the noise I added."

---

## 4. The Reverse Process (Sampling / Generation)

Once trained, we generate an image by starting from pure noise and using the model to iteratively denoise it step-by-step from $T$ down to 0.

At each step $t$:
1. We ask the model to predict the noise: $\epsilon_\theta = model(x_t, t)$
2. We subtract a fraction of that noise to estimate $x_{t-1}$.
3. We add back a little bit of *new* random noise. (This Langevin dynamics step is crucial for high-quality images; without it, the image looks blurry).

```python
@torch.no_grad()
def sample(model, image_shape=(1, 3, 64, 64)):
    # 1. Start with pure random noise
    x = torch.randn(image_shape)
    
    # 2. Iterate backwards from T-1 down to 0
    for t in reversed(range(T)):
        t_batch = torch.full((1,), t, dtype=torch.long)
        
        # Predict noise
        predicted_noise = model(x, t_batch)
        
        # Math to get x_{t-1} (simplified DDPM formula)
        alpha_t = alpha[t]
        alpha_bar_t = alpha_bar[t]
        beta_t = beta[t]
        
        # Remove the predicted noise
        x = (1 / torch.sqrt(alpha_t)) * (x - (beta_t / torch.sqrt(1 - alpha_bar_t)) * predicted_noise)
        
        # Add back some noise if t > 0
        if t > 0:
            noise = torch.randn_like(x)
            x = x + torch.sqrt(beta_t) * noise
            
    return x  # x_0: The generated clean image!
```

---

## Advanced Architectures: Stable Diffusion (Latent Diffusion)

Running a U-Net 1000 times on a $1024 \times 1024$ image requires massive compute. **Stable Diffusion** (Rombach et al., 2022) solved this using a **Latent Diffusion Model (LDM)**.

1. Train a VAE to compress a $512 \times 512$ image into a $64 \times 64$ latent space.
2. Run the entire diffusion process (adding noise, U-Net denoising) entirely in the $64 \times 64$ latent space. This is $64\times$ faster.
3. Decode the final denoised latent vector back into a $512 \times 512$ image using the VAE decoder.

## Classifier-Free Guidance (CFG)

How do you make text-to-image models actually follow the prompt?
You train the U-Net on both text-conditioned inputs and unconditional (empty text) inputs.
During generation, you run the U-Net twice at every step:
- $\epsilon_{cond}$: Prediction with the prompt ("A cat in space")
- $\epsilon_{uncond}$: Prediction with an empty prompt ("")

You extrapolate away from the unconditional prediction:
$\epsilon_{final} = \epsilon_{uncond} + w \cdot (\epsilon_{cond} - \epsilon_{uncond})$

Where $w$ is the **Guidance Scale** (typically 7.0 to 10.0). Higher $w$ forces the model to adhere strictly to the prompt, but too high causes color saturation artifacts.

---
## References
*   [Ho et al. (2020): Denoising Diffusion Probabilistic Models (DDPM)](https://arxiv.org/abs/2006.11239)
*   [Rombach et al. (2022): High-Resolution Image Synthesis with Latent Diffusion Models](https://arxiv.org/abs/2112.10752) — Stable Diffusion
*   [Lilian Weng: What are Diffusion Models?](https://lilianweng.github.io/posts/2021-07-11-diffusion-models/)
