# Task P4-2: Build a CNN for CIFAR-10

**Goal:** Build, train, and evaluate a Convolutional Neural Network from scratch on a real dataset using PyTorch.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. Load the CIFAR-10 Dataset
CIFAR-10 contains 60,000 32x32 color images in 10 classes (airplanes, cars, birds, cats, deer, dogs, frogs, horses, ships, trucks).

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader

# 1. Define Transforms (Data Augmentation for Training!)
train_transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

# 2. Download and Load Data
train_dataset = torchvision.datasets.CIFAR10(root='./data', train=True, download=True, transform=train_transform)
test_dataset = torchvision.datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transform)

train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True, num_workers=2)
test_loader = DataLoader(test_dataset, batch_size=128, shuffle=False, num_workers=2)
```

### 2. Build the Network Architecture
Create an `nn.Module` class named `SimpleCNN`. Use the following architecture pattern:

*   **Block 1:**
    *   Conv2d: 3 in_channels, 32 out_channels, kernel 3, padding 1
    *   BatchNorm2d(32)
    *   ReLU
    *   MaxPool2d: kernel 2, stride 2
*   **Block 2:**
    *   Conv2d: 32 in_channels, 64 out_channels, kernel 3, padding 1
    *   BatchNorm2d(64)
    *   ReLU
    *   MaxPool2d: kernel 2, stride 2
*   **Block 3:**
    *   Conv2d: 64 in_channels, 128 out_channels, kernel 3, padding 1
    *   BatchNorm2d(128)
    *   ReLU
    *   AdaptiveAvgPool2d(1) -> *This handles any spatial dimension size and flattens it for the linear layer!*
*   **Classifier:**
    *   Linear: 128 in_features, 10 out_features

### 3. The Training Loop
Write a standard PyTorch training loop.
1. Use `nn.CrossEntropyLoss()` and `optim.Adam(model.parameters(), lr=0.001)`.
2. Move the model and data to the GPU (`.to('cuda')`).
3. Train for 15 epochs.
4. Record the training loss and validation accuracy at the end of each epoch.

### 4. Evaluation
1. Plot the training loss curve.
2. What is your final accuracy on the test set? (Target: > 75%).
3. *Challenge:* Print the accuracy *per class*. Is the model better at identifying Cars or Cats?
