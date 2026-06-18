# Phase 3: Quick Reference & Cheat Sheet

## PyTorch Tensor Basics
```python
import torch

# Creation
x = torch.zeros(3, 3)
y = torch.randn(3, 3)
z = torch.tensor([[1.0, 2.0], [3.0, 4.0]])

# Device (GPU usage)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
x = x.to(device)

# Reshaping (view)
flattened = x.view(-1) # Flattens into 1D
```

## The Standard PyTorch Training Loop
Memorize this pattern. You will write it hundreds of times.

```python
import torch.nn as nn
import torch.optim as optim

# 1. Setup
model = MyModel().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 2. Loop over epochs
epochs = 10
for epoch in range(epochs):
    
    # 3. Put model in training mode (enables Dropout/BatchNorm)
    model.train()
    
    # 4. Loop over batches
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        # A. Zero the gradients (CRITICAL!)
        optimizer.zero_grad()
        
        # B. Forward pass
        outputs = model(inputs)
        
        # C. Calculate Loss
        loss = criterion(outputs, labels)
        
        # D. Backward pass (calculate gradients)
        loss.backward()
        
        # E. Update weights
        optimizer.step()
        
    print(f"Epoch {epoch+1}, Loss: {loss.item():.4f}")
```

## The Evaluation Loop
```python
# 1. Put model in evaluation mode (disables Dropout, freezes BatchNorm)
model.eval()

correct = 0
total = 0

# 2. Disable gradient tracking (saves memory and speeds up computation)
with torch.no_grad():
    for inputs, labels in test_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        outputs = model(inputs)
        
        # Get the index of the highest probability (for classification)
        _, predicted = torch.max(outputs.data, 1)
        
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(f'Test Accuracy: {100 * correct / total:.2f}%')
```
