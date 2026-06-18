# Phase 7: Generative Models

> **Goal:** Understand how AI creates new images, audio, and data.
> **Duration:** 4 weeks ⭐ Critical Phase

## Generative vs. Discriminative
- Discriminative (CNNs, ResNet): $P(Y|X)$. Given an image, what is the class?
- Generative (GANs, Diffusion): $P(X)$. Learn the distribution of the data to generate new, realistic samples.

## The Evolution of Generation
1. **VAEs (Variational Autoencoders):** Probabilistic, fast, but blurry images.
2. **GANs (Generative Adversarial Networks):** Two networks (Generator vs Discriminator) playing a game. Sharp images, but notoriously hard to train (mode collapse).
3. **Diffusion Models (DDPM, Stable Diffusion):** The current State-of-the-Art.
   - *Forward Process:* Slowly add Gaussian noise to an image until it's static.
   - *Reverse Process:* Train a U-Net to remove noise step-by-step.
   - Extremely stable training, incredible quality.

## Diffusion Transformers (DiT)
The latest trend (used in Sora, Stable Diffusion 3). Replacing the U-Net backbone in diffusion models with a Transformer architecture for better scaling.

## Homework
- Complete `homework/P7-1_gans.md`
- Complete `homework/P7-2_diffusion_from_scratch.md`
