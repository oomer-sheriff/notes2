# Phase 4: Quick Reference & Cheat Sheet

## Essential PyTorch CNN Layers

```python
import torch.nn as nn

# 2D Convolution
# in_channels: 3 for RGB images, 1 for Grayscale
# out_channels: Number of filters (feature maps) you want
# kernel_size: Usually 3 (3x3 grid)
conv = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, stride=1, padding=1)

# Max Pooling (Halves the image dimensions)
pool = nn.MaxPool2d(kernel_size=2, stride=2)

# Batch Normalization (Must match the out_channels of the previous conv layer)
batch_norm = nn.BatchNorm2d(32)

# Global Average Pooling (Used at the end of modern CNNs instead of Flattening)
# Reduces a (Batch, Channels, Height, Width) tensor to (Batch, Channels, 1, 1)
gap = nn.AdaptiveAvgPool2d(1)
```

## Typical CNN Block
```python
class CNNBlock(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_c, out_c, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_c),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )
    def forward(self, x):
        return self.block(x)
```

## Torchvision Image Transforms
Transforms are required to get raw images into the exact tensor format the network expects, and to perform Data Augmentation (making your dataset artificially larger by modifying the images).

```python
from torchvision import transforms

# Typical setup for training Data Augmentation + Formatting
train_transform = transforms.Compose([
    transforms.Resize((224, 224)),       # Standard ResNet size
    transforms.RandomHorizontalFlip(),   # Augmentation
    transforms.RandomRotation(10),       # Augmentation
    transforms.ToTensor(),               # Converts PIL Image to PyTorch Tensor (0 to 1 scale)
    # Normalize with ImageNet standard mean and std dev
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                         std=[0.229, 0.224, 0.225]) 
])

# Test transforms DO NOT include data augmentation!
test_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```
