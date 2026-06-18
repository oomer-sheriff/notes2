# Phase 8: NLP & LLM Theory

> **Goal:** Understand the ML principles behind the tools you use every day (RAG, Agents, APIs).
> **Duration:** 3 weeks

## The Pipeline
1. **Tokenization:** Text to numbers (BPE, SentencePiece).
2. **Embeddings:** Numbers to semantic vectors (Word2Vec, dense embeddings).
3. **Language Modeling:** Predicting the next token.

## Fine-Tuning 
Full fine-tuning is too expensive for 70B+ parameter models.
- **PEFT (Parameter-Efficient Fine-Tuning):** Freeze the base model, train a small adapter.
- **LoRA (Low-Rank Adaptation):** The most popular PEFT method. Injects small, trainable rank decomposition matrices into Transformer layers.

## Alignment
Base models just predict the next word (they might output infinite loops of text).
- **SFT (Supervised Fine-Tuning):** Train on instruction/response pairs to act like a chatbot.
- **RLHF (Reinforcement Learning from Human Feedback):** Train a reward model on human preferences, use PPO to optimize the LLM.
- **DPO (Direct Preference Optimization):** Newer, simpler alternative to RLHF.

## RAG Theory
- **Bi-Encoders:** Fast retrieval (FAISS, Chroma). Embed query and document independently, compute cosine similarity.
- **Cross-Encoders:** Slow, accurate reranking. Feed query + document together into attention layers.

## Homework
- Complete `homework/P8-1_lora_finetune.md`
- Complete `homework/P8-2_custom_tokenizer.md`
