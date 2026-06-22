# Task P6-4: Fine-tune BERT on Real Data

**Goal:** Use the Hugging Face Trainer to fine-tune BERT on a classification task, then compare it quantitatively against your Phase 5 LSTM.

Create a Jupyter Notebook in `homework/lab-files/`. **Run this on Google Colab with a T4 GPU** — fine-tuning BERT-base takes ~20 minutes per epoch on CPU, but only ~3 minutes per epoch on GPU.

---

## Part 1: Fine-tune BERT on IMDB

Follow the code from `04_bert_and_huggingface.md`. Your goal is to:

1. Load IMDB dataset
2. Tokenize with `bert-base-uncased` tokenizer using `max_length=256`
3. Load `AutoModelForSequenceClassification` with `num_labels=2`
4. Train for 3 epochs using the `Trainer` API
5. Record the final test accuracy

Expected result: **~92-93% accuracy**

## Part 2: Fine-tune on a Harder Task (Multi-class)

IMDB is binary (2 classes). Now fine-tune on a 6-class emotion classification task.

```python
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np

# The "emotion" dataset: 6 emotions — sadness, joy, love, anger, fear, surprise
dataset = load_dataset("dair-ai/emotion")
print("Classes:", dataset["train"].features["label"].names)
print("Training samples:", len(dataset["train"]))  # 16,000

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")

def tokenize(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized = dataset.map(tokenize, batched=True)
tokenized.set_format("torch", columns=["input_ids", "attention_mask", "label"])
tokenized = tokenized.rename_column("label", "labels")

# Fine-tune for 6 classes (change num_labels!)
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=6
)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": (preds == labels).mean()}

args = TrainingArguments(
    output_dir               = "./bert-emotion",
    num_train_epochs         = 4,
    per_device_train_batch_size = 32,
    per_device_eval_batch_size  = 64,
    learning_rate            = 2e-5,
    weight_decay             = 0.01,
    evaluation_strategy      = "epoch",
    save_strategy            = "epoch",
    load_best_model_at_end   = True,
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized["train"],
    eval_dataset=tokenized["validation"],
    compute_metrics=compute_metrics,
)

trainer.train()
```

## Part 3: DistilBERT — Speed vs Accuracy Tradeoff

DistilBERT is BERT distilled into 6 layers (instead of 12) — 40% fewer parameters and 60% faster, while retaining 97% of BERT's performance. Repeat Part 1 using `distilbert-base-uncased` instead of `bert-base-uncased`.

```python
# Only change this one line — everything else is identical!
model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2
)
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
```

## Part 4: Head-to-Head Comparison

Fill out this table and answer the questions:

| Model | Task | Params | Train Time / Epoch | Test Accuracy |
|---|---|---|---|---|
| LSTM (Phase 5) | IMDB sentiment | ~2M | | |
| DistilBERT | IMDB sentiment | 66M | | |
| BERT-base | IMDB sentiment | 110M | | |
| BERT-base | Emotion (6-class) | 110M | | |

**Questions:**
1. BERT has ~55× more parameters than your LSTM but achieves only ~5-8% higher accuracy. Is this tradeoff worth it? When would you prefer the LSTM?
2. How much accuracy did you lose going from BERT-base to DistilBERT on IMDB? Was it worth the speed gain?
3. On the 6-class emotion task, BERT likely struggles more. Why is a 6-class problem harder than a 2-class problem beyond just having more output neurons?
