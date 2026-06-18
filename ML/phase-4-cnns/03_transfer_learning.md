# Transfer Learning: Full Implementation

Transfer Learning is one of the most practically useful techniques in computer vision. Instead of training a model from random weights (which requires millions of images and hours of GPU time), you start from a model that already knows how to see.

---

## Why It Actually Works

When a CNN is trained on ImageNet's 1.2 million photos, its layers don't just memorize those images — they build up a hierarchy of visual understanding. The early layers learn things like edge detectors and color gradients. These aren't "ImageNet features," they are **universal visual primitives** that appear in every photograph ever taken. The middle layers combine those into textures and shapes. Only the deepest layers become truly task-specific (detecting "dog fur" vs "car wheel").

This hierarchy means that if your task involves any kind of natural image, you can reuse the first 95% of the network completely as-is. You only need to replace and re-train the final few layers.

---

## 1. Loading and Inspecting a Pre-trained Model

The first thing to do before any transfer learning is to actually look at the model's structure. `print(model)` shows you the exact layer names, which you'll need when you want to freeze or unfreeze specific ones.

```python
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
from torch.utils.data import DataLoader

# Download pre-trained ResNet18. PyTorch downloads the weights (~45MB) automatically.
# These weights were trained on ImageNet for ~90 epochs on 8 GPUs.
model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
print(model)
```

When you run `print(model)`, you'll see the full architecture. Pay attention to the very last line:
```
(fc): Linear(in_features=512, out_features=1000, bias=True)
```
This final `fc` (fully connected) layer maps the 512 learned features to 1000 ImageNet class scores. We're going to cut this off and replace it with our own layer that outputs the number of classes *we* care about.

---

## 2. Setting Up the Data

Before we touch the model, we need our data. When using a pre-trained model, it's important to apply the **same normalization the model was trained with**. ResNet was trained on ImageNet, so we normalize with ImageNet's mean and standard deviation. Applying different normalization would be like handing someone food using the wrong measuring units — the numbers look similar but the model interprets them completely differently.

The training transform includes `RandomHorizontalFlip` and `RandomCrop` — these are **data augmentation** techniques that randomly modify training images to artificially expand your dataset and prevent overfitting. The test transform never augments, because you want consistent, reproducible test results.

```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# For ResNet, images must be resized to 224×224 pixels.
# The model was designed for this exact size; other sizes produce wrong feature shapes.
train_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.RandomHorizontalFlip(),   # Augmentation: mirror image 50% of the time
    transforms.ToTensor(),               # Converts PIL image → tensor with values 0.0 to 1.0
    transforms.Normalize(               # Shift to match what ImageNet training used
        mean=[0.485, 0.456, 0.406],     # Mean of each R, G, B channel on ImageNet
        std=[0.229, 0.224, 0.225]       # Std dev of each channel
    )
])
# Test transform: same formatting steps, but NO augmentation
test_transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# CIFAR-10: 60,000 photos in 10 classes (airplane, car, bird, cat, deer, dog, etc.)
# torchvision will download it automatically on first run (~162MB)
train_set = torchvision.datasets.CIFAR10('./data', train=True,  download=True, transform=train_transform)
test_set  = torchvision.datasets.CIFAR10('./data', train=False, download=True, transform=test_transform)

# DataLoader wraps the datasets and handles batching, shuffling, and parallel loading
train_loader = DataLoader(train_set, batch_size=64, shuffle=True,  num_workers=2)
test_loader  = DataLoader(test_set,  batch_size=64, shuffle=False, num_workers=2)

print(f"Training samples: {len(train_set)}, Test samples: {len(test_set)}")
```

---

## 3. Reusable Training and Evaluation Functions

Rather than duplicating the training loop for each strategy, we write helper functions once. The key distinction is `model.train()` vs `model.eval()`. In train mode, Dropout randomly deactivates neurons. In eval mode, it passes everything through unchanged. If you forget to switch, your evaluation results will be wrong and inconsistent every time you run them.

```python
def train_epoch(model, loader, optimizer, criterion):
    """Runs one full pass through the training data. Returns avg loss and accuracy."""
    model.train()  # Enable dropout, update BatchNorm running stats
    total_loss, correct, total = 0, 0, 0
    
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        
        optimizer.zero_grad()           # Clear last step's gradients
        outputs = model(imgs)           # Forward pass: (batch, 10) logits
        loss = criterion(outputs, labels)  # Compare logits to true class indices
        loss.backward()                 # Compute gradients
        optimizer.step()               # Update all trainable weights
        
        total_loss += loss.item()
        correct += (outputs.argmax(1) == labels).sum().item()
        total += labels.size(0)
    
    return total_loss / len(loader), correct / total  # avg loss, accuracy


def eval_model(model, loader, criterion):
    """Runs one full pass through evaluation data. No weight updates."""
    model.eval()   # Disable dropout, freeze BatchNorm stats
    total_loss, correct, total = 0, 0, 0
    
    with torch.no_grad():  # Don't build computation graph — saves memory and time
        for imgs, labels in loader:
            imgs, labels = imgs.to(device), labels.to(device)
            outputs = model(imgs)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
    
    return total_loss / len(loader), correct / total
```

---

## 4. Strategy A: Feature Extraction (Freeze Everything)

**When to use:** Small dataset (< 5,000 samples) that is similar to ImageNet photos.

The idea is to use the entire pretrained network as a fixed "feature extractor." The convolutional layers are locked — their weights never change. Only the final classification layer gets trained. Since we're only updating 5,130 weights instead of 11 million, each epoch is much faster and we're far less likely to overfit on a small dataset.

Setting `requires_grad = False` on a parameter tells PyTorch's autograd engine to skip computing gradients for that parameter during `.backward()`. The optimizer can only update parameters it is explicitly given — so passing only `model.fc.parameters()` ensures everything else stays frozen even if gradients were somehow computed.

```python
model_fe = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

# Step 1: Freeze every parameter in the entire network
for param in model_fe.parameters():
    param.requires_grad = False

# Verify that nothing is trainable yet
trainable_before = sum(p.numel() for p in model_fe.parameters() if p.requires_grad)
print(f"Trainable params before replacing head: {trainable_before}")  # Should be 0

# Step 2: Replace the final layer.
# The new nn.Linear has requires_grad=True by default.
# in_features=512 is the number of features ResNet18 produces — check model.fc before replacing.
model_fe.fc = nn.Linear(512, 10)

# Verify only the new head is trainable
trainable_after = sum(p.numel() for p in model_fe.parameters() if p.requires_grad)
total           = sum(p.numel() for p in model_fe.parameters())
print(f"Trainable: {trainable_after:,} / Total: {total:,}")
# Only 5,130 parameters trainable (512 weights + 10 biases for 10 classes)!

model_fe = model_fe.to(device)

# Step 3: Optimizer only sees the head's parameters.
# Even if a frozen layer somehow accumulated a gradient, the optimizer wouldn't touch it.
optimizer_fe = optim.Adam(model_fe.fc.parameters(), lr=1e-3)
criterion     = nn.CrossEntropyLoss()

print("\n--- Feature Extraction Training ---")
for epoch in range(5):
    train_loss, train_acc = train_epoch(model_fe, train_loader, optimizer_fe, criterion)
    val_loss,   val_acc   = eval_model(model_fe, test_loader, criterion)
    print(f"Epoch {epoch+1}: Train Acc={train_acc:.3f}, Val Acc={val_acc:.3f}")
# You should reach ~70-75% in just 5 epochs, training only 5,130 parameters total!
```

---

## 5. Strategy B: Fine-Tuning (Unfreeze Later Layers)

**When to use:** Medium-large dataset (5,000+ samples), or images that look somewhat different from standard photos.

Here we unfreeze the last convolutional block (`layer4`) in addition to the new head. `layer4` is responsible for detecting the most task-specific high-level features (like "fur texture" or "wheel shape"). By allowing these to adapt, the model can shift its high-level understanding toward your specific domain. However, we keep the early layers frozen because things like edge detection are universal — there's nothing about your dataset that requires relearning edges from scratch.

The most important detail is using **different learning rates for different layers**. PyTorch's optimizer accepts a list of "parameter groups," each with its own `lr`. We use a *much* smaller learning rate for `layer4` than for the new `fc` layer. This is because `layer4` already has good weights — we want to nudge them slightly, not overwrite them. The new `fc` starts from random weights and needs a full-sized learning rate to converge.

```python
model_ft = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

# Step 1: Freeze everything
for param in model_ft.parameters():
    param.requires_grad = False

# Step 2: Selectively unfreeze layer4 — the last convolutional block
# These weights detect high-level features and benefit from domain adaptation
for param in model_ft.layer4.parameters():
    param.requires_grad = True

# Step 3: Replace the head (unfrozen by default)
model_ft.fc = nn.Linear(512, 10)

model_ft = model_ft.to(device)

# Step 4: Optimizer with different learning rates per group
# layer4 already has good weights → very small lr (gentle nudge, don't destroy them)
# fc is brand new → normal lr (needs to learn from random init)
optimizer_ft = optim.Adam([
    {'params': model_ft.layer4.parameters(), 'lr': 1e-4},  # 10× smaller!
    {'params': model_ft.fc.parameters(),     'lr': 1e-3},
])

print("\n--- Fine-Tuning Training ---")
for epoch in range(5):
    train_loss, train_acc = train_epoch(model_ft, train_loader, optimizer_ft, criterion)
    val_loss,   val_acc   = eval_model(model_ft, test_loader, criterion)
    print(f"Epoch {epoch+1}: Train Acc={train_acc:.3f}, Val Acc={val_acc:.3f}")
# Fine-tuning should outperform feature extraction by a few percentage points
```

---

## 6. Inspect What's Frozen

Any time you're doing transfer learning, it's good practice to print out exactly which layers are trainable. This catches bugs where you accidentally freeze something you meant to train, or vice versa.

```python
print(f"\n{'Layer':<30} {'Trainable?':<15} {'Params':>12}")
print("-" * 60)
for name, module in model_ft.named_children():
    # A module is "trainable" if ANY of its parameters have requires_grad=True
    trainable = any(p.requires_grad for p in module.parameters())
    n_params   = sum(p.numel()       for p in module.parameters())
    status     = "✅ YES" if trainable else "❌ Frozen"
    print(f"{name:<30} {status:<15} {n_params:>12,}")
```

This will print a table like:
```
Layer                          Trainable?      Params
------------------------------------------------------------
conv1                          ❌ Frozen          9,408
bn1                            ❌ Frozen              64
relu                           ❌ Frozen               0
...
layer4                         ✅ YES         2,099,712
fc                             ✅ YES             5,130
```

---
## References
*   [PyTorch Official Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
*   [Fast.ai: Practical Deep Learning — Transfer Learning](https://course.fast.ai/)
