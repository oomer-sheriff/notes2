# Phase 6: Transformers & Attention

> **Goal:** Master the architecture that revolutionized AI.
> **Duration:** 4 weeks ⭐ Critical Phase

## Attention Is All You Need
The Transformer (2017) discarded recurrence (RNNs) entirely in favor of the **Self-Attention** mechanism.

## The Core Concept: Self-Attention
Instead of compressing a sequence into a single hidden state, self-attention allows *every token to look at every other token* in the sequence to understand context.
- **Query, Key, Value:** The three matrices that calculate attention scores. "What am I looking for?" (Query), "What do I have?" (Key), "What information do I output?" (Value).

## Why Transformers Won
1. **Parallelization:** Unlike RNNs, the entire sequence is processed at once. GPUs love this.
2. **Long-range Dependencies:** A token can easily attend to a word 1000 tokens away without information degradation.

## The Ecosystem
- **Encoders (BERT):** Look in both directions. Great for classification, NER, embedding generation.
- **Decoders (GPT):** Autoregressive (look only at the past). Great for generation.
- **Vision Transformers (ViT):** Split an image into patches and treat them like words.

## Homework
- Complete `homework/P6-1_build_attention.md`
- Complete `homework/P6-2_nanogpt.md`
