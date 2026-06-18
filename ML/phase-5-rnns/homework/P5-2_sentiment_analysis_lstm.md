# Task P5-2: Sentiment Analysis with IMDB (RNN vs LSTM vs GRU)

**Goal:** Compare the three sequence architectures (RNN, LSTM, GRU) on a real binary classification task using real movie review data. You will be able to directly measure the performance gap between them.

Create a Jupyter Notebook in `homework/lab-files/`.

---

## Step 1: Load Real Data

We use the IMDB sentiment dataset, which contains 25,000 movie reviews labeled Positive or Negative. We'll use the Hugging Face `datasets` library to load it, then tokenize it ourselves.

```python
# pip install datasets
from datasets import load_dataset
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from collections import Counter

# Load the dataset — downloads automatically (~80MB)
raw = load_dataset("imdb")
train_raw = raw["train"]
test_raw  = raw["test"]

print(f"Training samples: {len(train_raw)}")
print(f"An example review: {train_raw[0]['text'][:200]}...")
print(f"Label (0=neg, 1=pos): {train_raw[0]['label']}")
```

## Step 2: Preprocessing — Building a Vocabulary

Unlike image data which arrives as numbers, text must be converted to integers. We build a vocabulary: a mapping from each word to a unique integer ID.

```python
MAX_VOCAB  = 10000   # Keep only the 10,000 most frequent words
MAX_LEN    = 200     # Truncate all reviews to 200 words
PAD_IDX    = 0       # Index used to pad short sequences to MAX_LEN

def tokenize(text):
    """Simple whitespace tokenizer. For production, use a proper tokenizer."""
    return text.lower().split()

# Count word frequencies across all training reviews
counter = Counter()
for sample in train_raw:
    counter.update(tokenize(sample["text"]))

# Build vocabulary: most frequent words get small indices (1 = most common)
# Reserve index 0 for padding, 1 for unknown words
vocab = {"<PAD>": 0, "<UNK>": 1}
for word, _ in counter.most_common(MAX_VOCAB - 2):
    vocab[word] = len(vocab)

def encode(text, max_len=MAX_LEN):
    """Converts a text string to a fixed-length list of integer IDs."""
    tokens = tokenize(text)
    ids    = [vocab.get(w, 1) for w in tokens[:max_len]]  # 1 = <UNK> for rare words
    # Pad with zeros if the review is shorter than max_len
    ids   += [PAD_IDX] * (max_len - len(ids))
    return ids

print(f"Vocabulary size: {len(vocab)}")
print(f"Encoded sample: {encode(train_raw[0]['text'])[:20]}...")


class IMDBDataset(Dataset):
    def __init__(self, data):
        self.x = torch.tensor([encode(s["text"]) for s in data], dtype=torch.long)
        self.y = torch.tensor([s["label"]        for s in data], dtype=torch.long)
    
    def __len__(self):
        return len(self.y)
    
    def __getitem__(self, idx):
        return self.x[idx], self.y[idx]

train_dataset = IMDBDataset(train_raw)
test_dataset  = IMDBDataset(test_raw)

train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
test_loader  = DataLoader(test_dataset,  batch_size=64, shuffle=False)
```

## Step 3: The Flexible Classifier

Build one model class that accepts a `cell_type` argument so you can easily swap between `'rnn'`, `'lstm'`, and `'gru'` without duplicating code.

```python
class SentimentClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_size, num_classes=2, 
                 num_layers=2, cell_type='lstm'):
        super().__init__()
        
        # Embedding: turns integer token IDs into dense vectors
        # padding_idx=0 ensures padding tokens don't contribute to learning
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        
        rnn_kwargs = dict(
            input_size=embed_dim, hidden_size=hidden_size, 
            num_layers=num_layers, batch_first=True, dropout=0.3
        )
        
        # Select the recurrent layer based on cell_type argument
        if cell_type == 'rnn':
            self.rnn = nn.RNN(**rnn_kwargs)
        elif cell_type == 'lstm':
            self.rnn = nn.LSTM(**rnn_kwargs)
        elif cell_type == 'gru':
            self.rnn = nn.GRU(**rnn_kwargs)
        else:
            raise ValueError(f"Unknown cell_type: {cell_type}")
        
        self.cell_type = cell_type
        self.dropout   = nn.Dropout(0.5)
        self.fc        = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        # x: (batch, seq_len)
        x = self.embedding(x)  # (batch, seq_len, embed_dim)
        
        if self.cell_type == 'lstm':
            out, (h_n, _) = self.rnn(x)  # LSTM returns (output, (h_n, c_n))
        else:
            out, h_n = self.rnn(x)        # RNN and GRU return (output, h_n)
        
        # Take the last layer's final hidden state
        last = h_n[-1]              # (batch, hidden_size)
        last = self.dropout(last)
        return self.fc(last)        # (batch, num_classes)
```

## Step 4: Train and Compare All Three

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def train_and_eval(cell_type, epochs=5):
    model = SentimentClassifier(
        vocab_size=len(vocab), embed_dim=64, hidden_size=128, cell_type=cell_type
    ).to(device)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    for epoch in range(epochs):
        model.train()
        for x_batch, y_batch in train_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            optimizer.zero_grad()
            output = model(x_batch)
            loss   = criterion(output, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
    
    # Evaluate on test set
    model.eval()
    correct, total = 0, 0
    with torch.no_grad():
        for x_batch, y_batch in test_loader:
            x_batch, y_batch = x_batch.to(device), y_batch.to(device)
            preds   = model(x_batch).argmax(dim=1)
            correct += (preds == y_batch).sum().item()
            total   += y_batch.size(0)
    
    return correct / total

# Run the comparison
for cell in ['rnn', 'gru', 'lstm']:
    acc = train_and_eval(cell, epochs=5)
    print(f"{cell.upper():<8} Test Accuracy: {acc:.1%}")
```

## Your Tasks

1. **Record the results table**: Which architecture achieved highest accuracy? By how much?
2. **Increase `MAX_LEN` to 500** — do longer sequences change the ranking between RNN and LSTM/GRU?
3. **Try `bidirectional=True`** — add it to the LSTM and see if it improves accuracy. (Remember to double the `nn.Linear` input size!)
4. **Plot the wrong predictions**: Find 5 reviews that the model got wrong. Can you understand why?
