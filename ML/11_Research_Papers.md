# 📄 Must-Read Research Papers

> **How to read a paper:** Don't read linearly. First pass: abstract + figures + conclusion (10 min). Second pass: intro + method, skip proofs (30 min). Third pass: full deep dive (1-2 hrs). Only do the third pass for papers critical to your understanding.

---

## 🏛️ Foundational Papers (Read These)

### 1. Attention Is All You Need (2017)
**Authors:** Vaswani et al. (Google Brain)  
**Link:** https://arxiv.org/abs/1706.03762  
**Why:** THE paper that introduced the Transformer architecture. Everything modern in AI traces back to this.  
**Read in:** Phase 6  
**Key takeaway:** Self-attention can replace recurrence entirely, enabling parallelization and scaling.

### 2. Deep Residual Learning for Image Recognition — ResNet (2015)
**Authors:** He et al. (Microsoft Research)  
**Link:** https://arxiv.org/abs/1512.03385  
**Why:** Skip connections made deep networks trainable. Without this, we wouldn't have 100+ layer networks.  
**Read in:** Phase 4  
**Key takeaway:** Identity shortcuts solve the degradation problem — deeper networks should never be worse.

### 3. ImageNet Classification with Deep Convolutional Neural Networks — AlexNet (2012)
**Authors:** Krizhevsky, Sutskever, Hinton  
**Link:** https://papers.nips.cc/paper/2012/hash/c399862d3b9d6b76c8436e924a68c45b-Abstract.html  
**Why:** Started the deep learning revolution. Showed GPUs could make neural nets practical.  
**Read in:** Phase 4  
**Key takeaway:** ReLU, dropout, data augmentation, and GPU training — all introduced/popularized here.

### 4. BERT: Pre-training of Deep Bidirectional Transformers (2018)
**Authors:** Devlin et al. (Google)  
**Link:** https://arxiv.org/abs/1810.04805  
**Why:** Showed that pre-training + fine-tuning is insanely effective for NLP.  
**Read in:** Phase 6  
**Key takeaway:** Bidirectional context via masked language modeling → massive gains on every NLP benchmark.

### 5. Language Models are Few-Shot Learners — GPT-3 (2020)
**Authors:** Brown et al. (OpenAI)  
**Link:** https://arxiv.org/abs/2005.14165  
**Why:** Showed that scaling up works. In-context learning emerges at scale.  
**Read in:** Phase 8  
**Key takeaway:** With enough parameters and data, models can perform tasks they weren't explicitly trained for.

---

## 🎨 Generative Models (Core Reading)

### 6. Generative Adversarial Networks (2014)
**Authors:** Goodfellow et al.  
**Link:** https://arxiv.org/abs/1406.2661  
**Why:** Introduced the adversarial framework for generation.  
**Read in:** Phase 7  
**Key takeaway:** Two networks competing → realistic sample generation.

### 7. Auto-Encoding Variational Bayes — VAE (2013)
**Authors:** Kingma & Welling  
**Link:** https://arxiv.org/abs/1312.6114  
**Why:** Principled probabilistic framework for generative modeling.  
**Read in:** Phase 7  
**Key takeaway:** Reparameterization trick makes variational inference differentiable.

### 8. Denoising Diffusion Probabilistic Models — DDPM (2020)
**Authors:** Ho et al.  
**Link:** https://arxiv.org/abs/2006.11239  
**Why:** Made diffusion models practical. Simple training objective, incredible sample quality.  
**Read in:** Phase 7  
**Key takeaway:** Predict and remove noise iteratively → generate images from pure noise.

### 9. High-Resolution Image Synthesis with Latent Diffusion Models — Stable Diffusion (2022)
**Authors:** Rombach et al.  
**Link:** https://arxiv.org/abs/2112.10752  
**Why:** Made diffusion practical at high resolution by working in latent space.  
**Read in:** Phase 7  
**Key takeaway:** Compress to latent space first, then run diffusion → orders of magnitude more efficient.

### 10. Scalable Diffusion Models with Transformers — DiT (2023)
**Authors:** Peebles & Xie  
**Link:** https://arxiv.org/abs/2212.09748  
**Why:** Replaced U-Net with Transformer in diffusion models. Used in DALL-E 3, Sora.  
**Read in:** Phase 7  
**Key takeaway:** Transformer scaling laws apply to diffusion models too.

---

## 🧠 LLMs & Alignment

### 11. Training language models to follow instructions — InstructGPT (2022)
**Authors:** Ouyang et al. (OpenAI)  
**Link:** https://arxiv.org/abs/2203.02155  
**Why:** RLHF explained. How to make LLMs actually helpful.  
**Read in:** Phase 8  
**Key takeaway:** SFT → Reward Model → PPO = aligned language model.

### 12. LoRA: Low-Rank Adaptation of Large Language Models (2021)
**Authors:** Hu et al.  
**Link:** https://arxiv.org/abs/2106.09685  
**Why:** Made fine-tuning accessible. Train 0.1% of parameters, get most of the benefit.  
**Read in:** Phase 8  
**Key takeaway:** Weight updates have low intrinsic rank — exploit this for efficiency.

### 13. Direct Preference Optimization — DPO (2023)
**Authors:** Rafailov et al.  
**Link:** https://arxiv.org/abs/2305.18290  
**Why:** Simpler alternative to RLHF — no reward model needed.  
**Read in:** Phase 8  
**Key takeaway:** Treat alignment as a classification problem on preference pairs.

### 14. Retrieval-Augmented Generation — RAG (2020)
**Authors:** Lewis et al. (Meta)  
**Link:** https://arxiv.org/abs/2005.11401  
**Why:** You already use RAG — now read the original paper.  
**Read in:** Phase 8  
**Key takeaway:** Parametric memory (LLM) + non-parametric memory (retrieval) = best of both worlds.

---

## 🔭 Frontier / Optional (Pick What Interests You)

### 15. Learning Transferable Visual Models from Natural Language Supervision — CLIP (2021)
**Authors:** Radford et al. (OpenAI)  
**Link:** https://arxiv.org/abs/2103.00020  
**Read in:** Phase 10

### 16. Mamba: Linear-Time Sequence Modeling with Selective State Spaces (2023)
**Authors:** Gu & Dao  
**Link:** https://arxiv.org/abs/2312.00752  
**Read in:** Phase 10

### 17. Outrageously Large Neural Networks: The Sparsely-Gated Mixture-of-Experts Layer (2017)
**Authors:** Shazeer et al. (Google)  
**Link:** https://arxiv.org/abs/1701.06538  
**Read in:** Phase 10

### 18. An Image is Worth 16x16 Words — ViT (2020)
**Authors:** Dosovitskiy et al. (Google)  
**Link:** https://arxiv.org/abs/2010.11929  
**Read in:** Phase 6

### 19. U-Net: Convolutional Networks for Biomedical Image Segmentation (2015)
**Authors:** Ronneberger et al.  
**Link:** https://arxiv.org/abs/1505.04597  
**Read in:** Phase 4 / Phase 7

### 20. Proximal Policy Optimization Algorithms — PPO (2017)
**Authors:** Schulman et al. (OpenAI)  
**Link:** https://arxiv.org/abs/1707.06347  
**Read in:** Phase 10

---

## 📖 Reading Order

Follow this order for the best learning experience:

| # | Paper | When |
|---|-------|------|
| 1 | AlexNet | Phase 4, Week 1 |
| 2 | ResNet | Phase 4, Week 2 |
| 3 | U-Net | Phase 4, Week 3 |
| 4 | Attention Is All You Need | Phase 6, Week 1 |
| 5 | BERT | Phase 6, Week 2 |
| 6 | ViT | Phase 6, Week 3 |
| 7 | GAN (Goodfellow) | Phase 7, Week 1 |
| 8 | VAE | Phase 7, Week 1 |
| 9 | DDPM | Phase 7, Week 2 |
| 10 | Latent Diffusion | Phase 7, Week 3 |
| 11 | DiT | Phase 7, Week 4 |
| 12 | GPT-3 | Phase 8, Week 1 |
| 13 | RAG | Phase 8, Week 1 |
| 14 | InstructGPT | Phase 8, Week 2 |
| 15 | LoRA | Phase 8, Week 2 |
| 16 | DPO | Phase 8, Week 3 |
| 17 | CLIP | Phase 10 |
| 18 | PPO | Phase 10 |
| 19 | Mamba | Phase 10 |
| 20 | MoE | Phase 10 |
