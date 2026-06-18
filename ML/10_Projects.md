# 🏗️ Capstone Projects

> **Philosophy:** Each project is end-to-end: problem → data → model → evaluation → deployment.  
> **Requirement:** Document everything in the project folder. Someone reading your code should understand your thought process.  
> **Portfolio:** These become your ML portfolio on GitHub.

---

## Project 1: Image Classifier Web App
**Phase required:** 4 (CNNs)  
**Difficulty:** ⭐⭐  
**Estimated time:** 8-12 hrs

### Spec
Build a CNN-based image classifier that identifies objects in user-uploaded images, deployed as a web API.

### Acceptance Criteria
- [ ] Custom CNN trained on CIFAR-10 or a custom dataset (>90% accuracy)
- [ ] Transfer learning comparison (your CNN vs fine-tuned ResNet)
- [ ] FastAPI endpoint: POST image → get prediction + confidence
- [ ] Dockerized, runnable with `docker compose up`
- [ ] Training notebook with loss curves, confusion matrix, sample predictions
- [ ] 1-page writeup: architecture choices, what worked, what didn't

### Bonus
- [ ] Deploy to your K8s cluster
- [ ] Add GradCAM visualization endpoint (show what the model "sees")
- [ ] A/B test two model versions

---

## Project 2: Shakespeare Text Generator (nanoGPT)
**Phase required:** 6 (Transformers)  
**Difficulty:** ⭐⭐⭐  
**Estimated time:** 10-15 hrs

### Spec
Build a character-level Transformer (GPT) from scratch that generates Shakespeare-like text.

### Acceptance Criteria
- [ ] Transformer decoder implemented from scratch (no Hugging Face)
- [ ] Multi-head self-attention, positional encoding, layer norm, residual connections
- [ ] Trained on the complete works of Shakespeare (~1M characters)
- [ ] Generates coherent-looking (not necessarily meaningful) text after training
- [ ] Experiment log: vary model size (layers, heads, embedding dim) and report results
- [ ] Training notebook with loss curves and generated samples at different training stages

### Bonus
- [ ] Implement KV-cache for faster generation
- [ ] Compare with an LSTM baseline — quantify the difference
- [ ] Add temperature and top-k/top-p sampling controls

---

## Project 3: MNIST Diffusion Model
**Phase required:** 7 (Generative Models)  
**Difficulty:** ⭐⭐⭐  
**Estimated time:** 12-18 hrs

### Spec
Build a DDPM (Denoising Diffusion Probabilistic Model) from scratch that generates handwritten digits.

### Acceptance Criteria
- [ ] Forward diffusion process (noise schedule) implemented from scratch
- [ ] U-Net or simple ConvNet as the noise prediction network
- [ ] Training loop with MSE loss on noise prediction
- [ ] Reverse sampling process that generates digits from pure noise
- [ ] Grid of generated samples at different training stages
- [ ] Comparison with your GAN from Phase 7 homework

### Bonus
- [ ] Add class conditioning (generate a specific digit)
- [ ] Implement DDIM sampling for faster generation
- [ ] Implement classifier-free guidance
- [ ] Scale up to Fashion-MNIST or CIFAR-10

---

## Project 4: RAG System — ML Theory Edition
**Phase required:** 8 (NLP & LLMs)  
**Difficulty:** ⭐⭐⭐  
**Estimated time:** 10-15 hrs

### Spec
Build a RAG chatbot over your own ML notes (the files from this learning directory). You know RAG — now build one where you understand every ML component.

### Acceptance Criteria
- [ ] Chunk and embed all your learning notes using a sentence transformer
- [ ] Vector store (ChromaDB or FAISS — you choose)
- [ ] Retrieval pipeline: query → embed → search → rerank → answer
- [ ] Implement at least one component from scratch (embedding, similarity search, or reranking)
- [ ] FastAPI endpoint for chat
- [ ] Evaluation: test with 20 ML questions, measure answer quality

### Bonus
- [ ] Compare retrieval methods: dense vs sparse (BM25) vs hybrid
- [ ] Fine-tune the embedding model on ML-specific data
- [ ] Add conversation memory / multi-turn context
- [ ] Deploy with Docker + K8s

---

## Project 5: Fine-Tuned Domain Expert LLM
**Phase required:** 8 (NLP & LLMs)  
**Difficulty:** ⭐⭐⭐⭐  
**Estimated time:** 15-20 hrs

### Spec
Take an open-source LLM and fine-tune it to be an expert in a specific domain using LoRA/QLoRA.

### Acceptance Criteria
- [ ] Select a base model (TinyLlama, Phi-2, or Mistral-7B)
- [ ] Curate a domain-specific instruction dataset (≥500 examples)
- [ ] Fine-tune with LoRA using PEFT library
- [ ] Evaluate: compare base model vs fine-tuned on domain questions
- [ ] Document hyperparameter choices and their effects
- [ ] Training notebook with W&B logging

### Bonus
- [ ] Try QLoRA for a larger model (7B+)
- [ ] Implement DPO alignment on the fine-tuned model
- [ ] Merge LoRA weights back into the base model for deployment
- [ ] Serve with vLLM for optimized inference

---

## Project 6: Full ML Pipeline (The Boss Fight) 🔥
**Phase required:** All phases  
**Difficulty:** ⭐⭐⭐⭐⭐  
**Estimated time:** 20-30 hrs

### Spec
Build a complete, production-grade ML pipeline from data ingestion to monitoring. Choose any problem (classification, generation, NLP — your pick).

### Acceptance Criteria
- [ ] Data pipeline: loading, cleaning, splitting, versioning (DVC)
- [ ] Model training with experiment tracking (W&B)
- [ ] Model evaluation with proper metrics and visualizations
- [ ] API serving with FastAPI
- [ ] Dockerized with multi-stage build
- [ ] CI/CD: GitHub Actions → test → build → deploy
- [ ] Deployed to K8s with proper health checks
- [ ] Basic monitoring: latency, error rate, prediction distribution

### Bonus
- [ ] Data drift detection
- [ ] Automated retraining pipeline
- [ ] A/B testing between model versions
- [ ] Load testing with Locust
