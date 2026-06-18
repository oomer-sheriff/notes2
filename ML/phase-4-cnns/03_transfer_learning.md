# Transfer Learning

Training a CNN like ResNet from scratch takes weeks on hundreds of GPUs and requires millions of images. 

**Transfer Learning** allows you to download a pre-trained model (usually trained on ImageNet) and adapt it to your specific problem using only a few hundred or thousand images. It works because the early layers of CNNs learn generic features (edges, textures, colors) that are useful for *any* vision task.

There are two main ways to do this:

## 1. Feature Extraction (Fast)
You freeze the weights of all the convolutional layers. They become a fixed "feature extractor." You only replace the final, fully connected "classifier" layer and train *only* those new weights.

Use this when your dataset is small and similar to ImageNet (e.g., classifying breeds of dogs).

```python
import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

# 1. Download pre-trained model (weights downloaded from internet)
model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

# 2. FREEZE the convolutional layers
for param in model.parameters():
    param.requires_grad = False

# 3. Replace the final classifier layer
# The original ResNet18 outputs 1000 classes. Let's say we only have 3 classes.
num_features = model.fc.in_features # This is 512 for ResNet18
model.fc = nn.Linear(num_features, 3)

# Note: The new layer (model.fc) has requires_grad=True by default!

# 4. Train
# Pass ONLY the parameters that require gradients to the optimizer!
optimizer = torch.optim.Adam(model.fc.parameters(), lr=0.001)

# Now, during the training loop, only the final layer will be updated.
```

## 2. Fine-Tuning (Slower, More Accurate)
Instead of freezing the entire convolutional base, you freeze the early layers (which detect generic edges) and unfreeze the later layers (which detect more specific shapes). You then train the unfreezed layers alongside your new classifier.

Use this when you have a medium/large dataset.

**CRITICAL RULE:** When fine-tuning, you must use a *very small* learning rate (e.g., `1e-4` or `1e-5`). If you use a standard learning rate, you will destroy the carefully calibrated weights the model already learned.

```python
# Assuming 'model' from above

# 1. Unfreeze the last "block" of convolutional layers
for param in model.layer4.parameters():
    param.requires_grad = True

# 2. Pass all unfrozen parameters to the optimizer
# We can use different learning rates for different parts of the network!
optimizer = torch.optim.Adam([
    {'params': model.layer4.parameters(), 'lr': 1e-5}, # Very small LR for Conv layers
    {'params': model.fc.parameters(), 'lr': 1e-3}      # Normal LR for new Classifier
])
```

---
## References
*   [PyTorch: Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
*   [Hugging Face: Using Pretrained Models](https://huggingface.co/docs/transformers/training)
