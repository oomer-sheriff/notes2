# BERT and Hugging Face Transformers

## Encoder-Only vs Decoder-Only

You've now seen two types of Transformers. It helps to understand the landscape:

| Model Type | Mask | Pre-training Task | Best For |
|---|---|---|---|
| **Encoder-only** (BERT) | Bidirectional — every token sees all others | Masked Language Modeling (predict `[MASK]`) | Understanding: classification, NER, Q&A |
| **Decoder-only** (GPT) | Causal — each token sees only past tokens | Next-token prediction (language modeling) | Generation: chatbots, code, creative writing |
| **Encoder-Decoder** (T5, BART) | Encoder: bidirectional; Decoder: causal | Text-to-text (span corruption, denoising) | Translation, summarization, seq2seq |

**The key insight:** BERT reads the whole sequence bidirectionally, which makes it excellent at understanding context but prevents it from generating text (you can't predict the next token if you already see it). GPT only reads left-to-right, which makes it naturally generative.

---

## BERT: Masked Language Modeling

BERT (Bidirectional Encoder Representations from Transformers) is pre-trained on two tasks:

1. **Masked Language Modeling (MLM):** 15% of input tokens are randomly replaced with `[MASK]`. The model must predict the original tokens. This forces the model to build rich bidirectional representations — it must understand both left and right context to fill in a masked word.

2. **Next Sentence Prediction (NSP):** Two sentences are given; the model predicts whether sentence B naturally follows sentence A. (Note: later research found NSP doesn't help much; RoBERTa dropped it.)

---

## Using Hugging Face Transformers

The Hugging Face `transformers` library lets you download and use pretrained models with just a few lines of code. You don't need to rebuild the architecture — just load, fine-tune, and evaluate.

```python
# pip install transformers datasets

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from datasets import load_dataset
import torch
import numpy as np

# ---- STEP 1: Load data ----
# We'll fine-tune BERT on IMDB sentiment analysis (the same task from Phase 5!)
# so you can directly compare LSTM accuracy vs BERT accuracy
dataset = load_dataset("imdb")

print("Example review:", dataset["train"][0]["text"][:200])
print("Label:", dataset["train"][0]["label"])  # 0=negative, 1=positive
```

---

## Tokenization: Not Just Splitting on Spaces

BERT doesn't use character-level or word-level tokenization. It uses **WordPiece tokenization**: a subword algorithm that splits rare words into smaller pieces and keeps common words whole.

For example: `"tokenizing"` → `["token", "##izing"]`
- `##` prefix means "this piece continues the previous word"
- Common words like "the", "is", "running" stay as single tokens
- Rare words like "transformerization" get split into known subword pieces

This gives a vocabulary of ~30,000 tokens that can represent any English text without having unknown tokens.

```python
# ---- STEP 2: Tokenization ----
# AutoTokenizer loads the exact tokenizer that was used to train BERT
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

# See what the tokenizer does
sample_text = "The movie was surprisingly good, despite my low expectations."
tokens = tokenizer.tokenize(sample_text)
print("Tokens:", tokens)
# ['the', 'movie', 'was', 'surprisingly', 'good', ',', 'despite', 'my', 'low', 'expectations', '.']

encoded = tokenizer(sample_text, return_tensors='pt')
print("Input IDs:", encoded['input_ids'])
# tensor([[  101, 1996, 3185, 2001, ...  102]])
# 101 = [CLS] special classification token (always first)
# 102 = [SEP] separator token (always last)
print("Special tokens added:", tokenizer.convert_ids_to_tokens(encoded['input_ids'][0]))


def tokenize_function(examples):
    """
    Tokenize a batch of examples.
    truncation=True: cut reviews longer than max_length
    padding='max_length': pad short reviews with [PAD] tokens to same length
    max_length=256: use 256 instead of full 512 to save memory/speed
    """
    return tokenizer(
        examples["text"],
        truncation=True,
        padding="max_length",
        max_length=256
    )

# Apply to the whole dataset at once (cached on disk for speed)
tokenized = dataset.map(tokenize_function, batched=True)

# Rename 'label' to 'labels' — HuggingFace Trainer expects this name
tokenized = tokenized.rename_column("label", "labels")
tokenized.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

print("\nTokenized dataset columns:", tokenized["train"].features)
print("Input IDs shape of first item:", tokenized["train"][0]["input_ids"].shape)
```

---

## Fine-Tuning BERT

Loading a pretrained BERT and adding a classification head on top is a single line. The `AutoModelForSequenceClassification` class automatically replaces BERT's MLM head with a linear classifier for `num_labels` classes.

```python
# ---- STEP 3: Load pre-trained model ----
# bert-base-uncased: 12 layers, 12 heads, d_model=768, ~110M parameters
# This is the same BERT published by Google in 2018
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased",
    num_labels=2  # Binary: negative (0) or positive (1)
)

# The model has all of BERT's pre-trained weights loaded.
# Only the new classification head is randomly initialized.
# Fine-tuning will update ALL weights, but the LR keeps changes small for old layers.
total = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total:,}")  # ~110M


# ---- STEP 4: Evaluation metric ----
def compute_metrics(eval_pred):
    """Called by Trainer at the end of each evaluation epoch."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = (predictions == labels).mean()
    return {"accuracy": accuracy}


# ---- STEP 5: Training with Hugging Face Trainer ----
# TrainingArguments handles all the boilerplate: checkpointing, logging, LR scheduling
training_args = TrainingArguments(
    output_dir             = "./bert-imdb-results",
    num_train_epochs       = 3,
    per_device_train_batch_size = 16,  # Batch size per GPU
    per_device_eval_batch_size  = 32,
    warmup_steps           = 200,      # Gradually increase LR for first 200 steps
    weight_decay           = 0.01,     # AdamW regularization
    logging_dir            = "./logs",
    evaluation_strategy    = "epoch",  # Evaluate at end of each epoch
    save_strategy          = "epoch",
    load_best_model_at_end = True,     # Keep the checkpoint with the best eval accuracy
    learning_rate          = 2e-5,     # Standard fine-tuning LR for BERT (very small!)
)

# Trainer handles the full training loop, GPU movement, and evaluation for you
trainer = Trainer(
    model          = model,
    args           = training_args,
    train_dataset  = tokenized["train"],
    eval_dataset   = tokenized["test"],
    compute_metrics= compute_metrics,
)

trainer.train()

# After 3 epochs, BERT-base should achieve ~93% accuracy on IMDB
# Compare: your Phase 5 LSTM achieved ~85-88%
```

---

## Inference: Using Your Fine-Tuned Model

```python
from transformers import pipeline

# The pipeline abstraction handles tokenization + inference + decoding for you
classifier = pipeline(
    "text-classification",
    model="bert-base-uncased",   # Or path to your saved checkpoint
    tokenizer=tokenizer,
    device=0 if torch.cuda.is_available() else -1
)

reviews = [
    "This was the best film I've seen in years. Absolutely stunning.",
    "Terrible. A complete waste of two hours. The plot made no sense.",
    "It was okay. Not great, not bad. Just... fine.",
]

results = classifier(reviews)
for review, result in zip(reviews, results):
    print(f"Review: {review[:50]}...")
    print(f"  → Label: {result['label']}, Score: {result['score']:.2%}\n")
```

---
## References
*   [Hugging Face Course: Fine-tuning a pre-trained model](https://huggingface.co/course/chapter3) — The best hands-on guide
*   [BERT Paper: Devlin et al. (2018)](https://arxiv.org/abs/1810.04805)
*   [Jay Alammar: The Illustrated BERT](https://jalammar.github.io/illustrated-bert/)
