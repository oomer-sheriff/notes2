# Task P3-2: PyTorch Fundamentals

**Goal:** Recreate the network from P3-1, but this time use PyTorch. See how much easier life is when you don't have to write the backward pass yourself.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. PyTorch Setup

Use the same Digits dataset from P3-1. But now, convert the NumPy arrays into PyTorch Tensors.

```python
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

digits = load_digits()
X = digits.data / 16.0
y = digits.target # Notice we don't need one-hot encoding for PyTorch!

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Convert to Tensors
X_train_t = torch.tensor(X_train, dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.long) # CrossEntropyLoss requires long targets
X_test_t = torch.tensor(X_test, dtype=torch.float32)
y_test_t = torch.tensor(y_test, dtype=torch.long)
```

### 2. Build the Model
Create an `nn.Module` class that has exactly the same architecture: 
Linear(64 -> 32) -> ReLU -> Linear(32 -> 10).

*(Note: Do NOT put a Softmax layer at the end. PyTorch's `CrossEntropyLoss` does it automatically).*

### 3. The Training Loop
Write the standard PyTorch training loop:
1. Initialize the model, `nn.CrossEntropyLoss()`, and `optim.Adam(model.parameters(), lr=0.01)`.
2. Loop for 1000 epochs.
3. Zero gradients, forward pass, calculate loss, backward pass, optimizer step.
4. Every 100 epochs, calculate and print the accuracy on the test set.

### 4. GPU Challenge
Modify your code so that the Model and the Tensors are moved to the GPU (if available in Colab) using `.to('cuda')` or `.cuda()`. Does it run faster?
