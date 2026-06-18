# The Evolution of CNN Architectures

The history of Deep Learning is largely the history of CNN architectures competing on the **ImageNet** dataset (1.2 million training images, 1,000 classes). Understanding how these architectures evolved tells you *why* modern networks are designed the way they are.

## 1. LeNet-5 (1998)
The grandfather of CNNs. Developed by Yann LeCun to recognize handwritten digits on bank checks.
*   **Innovation:** Proved that convolutions + pooling + fully connected layers worked.
*   **Scale:** ~60,000 parameters. Trained on 32x32 pixel images.

## 2. AlexNet (2012)
The network that sparked the Deep Learning revolution. It crushed the ImageNet competition, beating traditional ML by a massive margin.
*   **Innovation:** Used **ReLU** instead of Tanh/Sigmoid (which solved vanishing gradients and sped up training 6x). Used **Dropout** to prevent overfitting. Most importantly, it was trained on **GPUs**.
*   **Scale:** 60 million parameters.

## 3. VGG-16 (2014)
AlexNet used a messy mix of filter sizes (11x11, 5x5, 3x3). VGG proved that simplicity was better.
*   **Innovation:** Exclusively used small 3x3 filters. To see larger patterns, it just stacked the layers deeper. A stack of two 3x3 layers has the same "receptive field" as a 5x5 layer, but uses fewer parameters and has more non-linearities (ReLUs).
*   **Scale:** 138 million parameters (very heavy/slow).

## 4. ResNet (2015)
The most important architecture in modern computer vision.
Before ResNet, if you stacked more than 20 layers, training error actually *increased* because gradients vanished during backprop. 
*   **Innovation: Skip Connections (Residual Blocks).** The input to a layer is added to its output: $F(x) + x$. This gives gradients a "highway" to flow backwards perfectly, preventing the vanishing gradient problem.
*   **Scale:** Allowed networks to be 100+ or even 1000+ layers deep!

```python
import torch
import torch.nn as nn

# A simplified Residual Block from ResNet
class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        # Two 3x3 convolutions
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(channels)
        self.relu = nn.ReLU()
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(channels)
        
    def forward(self, x):
        identity = x # Save the original input!
        
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        
        out = self.conv2(out)
        out = self.bn2(out)
        
        # THE MAGIC TRICK: Add the original input back before the final ReLU
        out += identity 
        out = self.relu(out)
        
        return out

# Test it
x = torch.randn(1, 64, 32, 32) # Batch of 1, 64 channels, 32x32 image
block = ResidualBlock(64)
output = block(x)
print("ResNet Block Output Shape:", output.shape) # Notice shape doesn't change
```

## 5. Modern Era (EfficientNet & ViT)
*   **EfficientNet (2019):** Used algorithms to discover the optimal way to balance network depth (layers), width (channels), and image resolution. Achieved state-of-the-art accuracy with 10x fewer parameters than competitors.
*   **Vision Transformers (ViT) (2020):** Ditched convolutions entirely! Treated an image as a sequence of 16x16 "patches" and fed them into a Transformer (the architecture behind ChatGPT). Requires massive amounts of data to beat ResNet, but scales better.

---
## References
*   [Yannic Kilcher: ResNet Paper Explained](https://www.youtube.com/watch?v=GWt6Fu05voI)
*   [PapersWithCode: ImageNet Leaderboard](https://paperswithcode.com/sota/image-classification-on-imagenet)
