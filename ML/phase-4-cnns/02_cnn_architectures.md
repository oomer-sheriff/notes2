# CNN Architectures: Under the Hood

Understanding CNN architectures isn't just about knowing "ResNet uses skip connections." You need to be able to *build* them. That's what this file covers.

---

## 1. VGG-Style: Stacking 3x3 Convolutions

VGG's key insight was deceptively simple: **don't use big filters, just stack small ones deeper**. Two stacked 3×3 conv layers see the same "receptive field" (area of the original image) as one 5×5 conv, but they use fewer parameters and have *two* ReLU non-linearities instead of one. More non-linearities = the network can learn more complex functions.

We'll create a reusable `VGGBlock` class that represents this repeating pattern. The class takes `in_channels` (how many feature maps are coming in) and `out_channels` (how many feature maps we want to output). The `num_convs` argument controls how many of those 3×3 convolutions get stacked.

```python
import torch
import torch.nn as nn

class VGGBlock(nn.Module):
    """Two 3x3 Conv layers stacked together — the VGG pattern."""
    def __init__(self, in_channels, out_channels, num_convs=2):
        super().__init__()
        layers = []
        for i in range(num_convs):
            # First conv changes the channel count; subsequent ones keep it constant.
            in_c = in_channels if i == 0 else out_channels
            layers += [
                nn.Conv2d(in_c, out_channels, kernel_size=3, padding=1),
                nn.ReLU(inplace=True)
            ]
        # Max pooling halves the spatial resolution (H and W both ÷2)
        layers.append(nn.MaxPool2d(kernel_size=2, stride=2))
        self.block = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.block(x)
```

Now we assemble a full mini-VGG by stacking three of these blocks. Notice how the channel count doubles at each block (32 → 64 → 128) while the spatial resolution halves (32 → 16 → 8 → 4). This is the classic CNN trade-off: as you go deeper, you trade spatial precision for richer feature representations. The final classifier flattens the remaining 128×4×4 spatial tensor into a 2048-long vector, then uses two linear layers to arrive at the 10 class scores.

```python
class MiniVGG(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            VGGBlock(3, 32, num_convs=2),   # 3ch, 32x32 → 32ch, 16x16
            VGGBlock(32, 64, num_convs=2),  # 32ch, 16x16 → 64ch, 8x8
            VGGBlock(64, 128, num_convs=2), # 64ch, 8x8   → 128ch, 4x4
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),                   # 128 * 4 * 4 = 2048
            nn.Linear(128*4*4, 256),
            nn.ReLU(),
            nn.Dropout(0.5),               # Drop 50% of neurons to fight overfitting
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Instantiate and do a quick sanity check.
# A batch of 8 fake CIFAR-10 images (3 channels, 32×32 pixels).
model = MiniVGG()
dummy = torch.randn(8, 3, 32, 32)
out = model(dummy)
print("Output shape:", out.shape)  # Expect (8, 10) — 8 samples, 10 class scores

total_params = sum(p.numel() for p in model.parameters())
print(f"Total Parameters: {total_params:,}")
```

---

## 2. ResNet: Skip Connections in Full Detail

### The Problem ResNet Solved

Before ResNet (2015), training CNNs with more than ~20 layers was nearly impossible. Counterintuitively, adding more layers made the network perform *worse*, even on training data. The culprit was **vanishing gradients**.

During backpropagation, the gradient is repeatedly multiplied by numbers less than 1 (the derivatives of ReLU and the weights themselves). After passing through 50 layers worth of chain-rule multiplications, those gradients shrink to numbers like `0.000001`. The early layers receive almost zero gradient signal and effectively stop learning.

### The Solution: A Highway for Gradients

ResNet's fix is elegant. Instead of the signal having to pass through every non-linear operation on its way back, a **skip connection** (also called a residual connection) adds a shortcut that bypasses those operations:

```
Normal block:  x → Conv → BN → ReLU → Conv → BN → output
Skip:          x ─────────────────────────────────────► +  →  ReLU  →  output
```

The final output is `F(x) + x`. During backpropagation, the gradient of `F(x) + x` with respect to `x` is `F'(x) + 1`. That **`+1`** means the gradient can *never* fully vanish — there is always a direct path back. This is what made training 100+ layer networks possible.

We need two versions of this block. The first keeps spatial dimensions identical (used repeatedly inside a "stage" of the network). The second halves the spatial size and doubles the channels when transitioning between stages.

```python
class ResidualBlock(nn.Module):
    """A residual block that preserves spatial size and channel count.
    Used inside a network stage where resolution stays the same."""
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1   = nn.BatchNorm2d(channels)
        self.relu  = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2   = nn.BatchNorm2d(channels)
        
    def forward(self, x):
        # Save the input. This is what gets added back at the end.
        identity = x
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        # The skip connection: add the original input to the processed output.
        # Both tensors have identical shapes here, so this is a simple element-wise add.
        out = out + identity
        out = self.relu(out)
        return out
```

The `DownsampleBlock` is trickier. If we halve the spatial size in the main path (`stride=2`), the shortcut `x` has the wrong shape to add — it's still the old, larger size. We fix this with a **projection shortcut**: a simple 1×1 convolution with `stride=2` that also halves the size and changes the channel count, making it exactly the right shape to add.

```python
class DownsampleBlock(nn.Module):
    """A residual block that halves spatial size and doubles channels.
    Used when transitioning between network stages."""
    def __init__(self, in_channels, out_channels, stride=2):
        super().__init__()
        # Main path: stride=2 in the first conv halves H and W
        self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, 
                               stride=stride, padding=1, bias=False)
        self.bn1   = nn.BatchNorm2d(out_channels)
        self.relu  = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(out_channels, out_channels, kernel_size=3,
                               padding=1, bias=False)
        self.bn2   = nn.BatchNorm2d(out_channels)
        
        # Projection shortcut: a 1×1 conv that reshapes x to match the main path's output.
        # Without this, the shapes don't match and you can't do the addition.
        self.shortcut = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride, bias=False),
            nn.BatchNorm2d(out_channels)
        )
        
    def forward(self, x):
        # Project x BEFORE saving it as identity, so shapes will match later
        identity = self.shortcut(x)
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        
        # Now both tensors are the same shape — the addition works!
        out = out + identity
        out = self.relu(out)
        return out
```

Now we assemble the full network. The `stem` is a single conv layer that processes the raw image. Then we have three "stages" (`layer1`, `layer2`, `layer3`). Each stage starts with a `DownsampleBlock` to change resolution/channels, then applies one or more `ResidualBlock`s. The final `AdaptiveAvgPool2d(1)` performs **Global Average Pooling** — it collapses each feature map into a single number by averaging all its pixels, regardless of the spatial size. This means the network can handle any input resolution.

```python
class SmallResNet(nn.Module):
    """A small ResNet for CIFAR-10 (32x32 input, 10 classes)."""
    def __init__(self, num_classes=10):
        super().__init__()
        # The stem processes the raw 3-channel input into 32 feature maps.
        # We don't pool here — CIFAR images are only 32x32, too small to shrink yet.
        self.stem = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True)
        )
        # Layer 1: two ResidualBlocks. Channels stay at 32. Spatial stays at 32x32.
        self.layer1 = nn.Sequential(ResidualBlock(32), ResidualBlock(32))
        # Layer 2: DownsampleBlock takes 32ch→64ch AND 32x32→16x16.
        self.layer2 = nn.Sequential(DownsampleBlock(32, 64), ResidualBlock(64))
        # Layer 3: DownsampleBlock takes 64ch→128ch AND 16x16→8x8.
        self.layer3 = nn.Sequential(DownsampleBlock(64, 128), ResidualBlock(128))
        
        # Global Average Pooling: 128ch × 8×8 → 128ch × 1×1
        self.pool = nn.AdaptiveAvgPool2d(1)
        # Final classifier: 128 features → 10 class scores
        self.fc   = nn.Linear(128, num_classes)
        
    def forward(self, x):
        x = self.stem(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.pool(x)
        x = x.view(x.size(0), -1)  # Flatten from (B, 128, 1, 1) to (B, 128)
        x = self.fc(x)
        return x

resnet = SmallResNet()
dummy = torch.randn(8, 3, 32, 32)
out = resnet(dummy)
print("ResNet output shape:", out.shape)  # Expect (8, 10)

total_params = sum(p.numel() for p in resnet.parameters())
print(f"ResNet Parameters: {total_params:,}")
# ResNet achieves better accuracy than VGG with fewer parameters — efficiency wins!
```

---

## 3. Batch Normalization: Why it Matters

Without Batch Normalization, activations can shift dramatically as training progresses. The output distribution of layer 5 keeps changing as layers 1-4 update their weights, so layer 6 has to constantly re-adapt to a moving target. This is called **Internal Covariate Shift** and it's why training deep networks without BatchNorm requires very careful learning rate tuning.

BatchNorm fixes this by normalizing each feature to have mean=0 and std=1 within a batch, then *learning* an optimal scale (`gamma`) and shift (`beta`) for each feature. This means the network gets normalized inputs to each layer without losing the ability to represent arbitrary scales.

The code below demonstrates what the normalization step actually does to the numbers. Notice how the two samples have wildly different raw activation values — one column has values of 1/2 and another has 100/200. After BatchNorm, every column is re-centered around zero with consistent scale.

```python
# Two samples, three features — notice how the scale is wildly different per feature
x = torch.tensor([[1.0, 100.0, 5.0],
                  [2.0, 200.0, 10.0]])

print("Before BatchNorm:")
print(x)
print(f"Column means: {x.mean(dim=0).tolist()}")  # [1.5, 150.0, 7.5]
print(f"Column stds:  {x.std(dim=0).tolist()}")   # [0.5, 50.0, 2.5]

bn = nn.BatchNorm1d(3)
bn.eval()  # Use exact stats from this batch (not running stats)
with torch.no_grad():
    normed = bn(x)

print("\nAfter BatchNorm:")
print(normed.detach())
print(f"Column means: {normed.mean(dim=0).tolist()}")  # Approximately [0, 0, 0]
print(f"Column stds:  {normed.std(dim=0).tolist()}")   # Approximately [1, 1, 1]
# Every column now has consistent scale — this is what each subsequent layer "sees"
```

---
## References
*   [Papers with Code: ResNet (He et al., 2015)](https://paperswithcode.com/method/resnet)
*   [Batch Normalization Original Paper (Ioffe & Szegedy, 2015)](https://arxiv.org/abs/1502.03167)
*   [Stanford CS231n: CNN Architectures](http://cs231n.stanford.edu/slides/2022/lecture_9_kangxue.pdf)
