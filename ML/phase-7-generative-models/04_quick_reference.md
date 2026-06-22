# Phase 7: Quick Reference & Cheat Sheet

## The Generative Triad

| Model | How it generates | Pros | Cons |
|---|---|---|---|
| **VAE** | Samples from smooth latent distribution | Continuous latent space, stable training, fast | Blurry images, lower quality than GANs/Diffusion |
| **GAN** | Min-max adversarial game (Generator vs Discriminator) | Very sharp images, fast sampling | Unstable training, mode collapse, hard to evaluate |
| **Diffusion** | Iterative denoising starting from pure noise | Highest quality, stable training, easy to condition | Slow generation (many steps) |

## VAE Math
**Reparameterization Trick:** `z = μ + σ * ε`, where `ε ~ N(0, 1)` and `σ = exp(0.5 * logvar)`
**Loss:** `MSE(x, x̂) + KL_Divergence(N(μ, σ²) || N(0, 1))`

## GAN Math
**Discriminator Loss:** Maximize `log(D(x)) + log(1 - D(G(z)))`
**Generator Loss:** Maximize `log(D(G(z)))` (Non-saturating heuristic)

## Diffusion Math (Simplified)
**Forward (Noise injection):** $x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon$
**Loss:** $MSE(\epsilon_{predicted}, \epsilon_{actual})$
**CFG (Guidance):** $\epsilon_{final} = \epsilon_{uncond} + w \cdot (\epsilon_{cond} - \epsilon_{uncond})$

## Common Architectures
- **U-Net:** Backbone of almost all diffusion models. Symmetrical encoder/decoder with skip connections.
- **Latent Diffusion:** Runs the diffusion process on VAE-compressed representations (e.g., $64 \times 64$) instead of raw pixels ($512 \times 512$) for speed.
- **ControlNet:** Adds spatial conditioning (edges, poses) to a frozen diffusion model.
- **DiT (Diffusion Transformers):** Replaces U-Net with a Transformer block architecture (used in Sora, SD3).

## Hugging Face Diffusers (Quick Start)
```python
# pip install diffusers transformers accelerate
from diffusers import DiffusionPipeline
import torch

pipe = DiffusionPipeline.from_pretrained(
    "stabilityai/stable-diffusion-xl-base-1.0",
    torch_dtype=torch.float16,
    use_safetensors=True,
    variant="fp16"
)
pipe.to("cuda")

prompt = "A cinematic shot of a cyberpunk city, neon lights, 4k"
image = pipe(prompt=prompt, num_inference_steps=50, guidance_scale=7.5).images[0]
image.save("cyberpunk.png")
```
