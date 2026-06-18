# Object Detection and Segmentation: Full Implementation

---

## Part 1: Object Detection with YOLO

### Classification vs Detection — The Key Difference

A classification model sees an image and outputs one answer: *"this is a dog."* That's useful, but most real-world applications need more. A self-driving car needs to know *where* every pedestrian is. A security camera needs to track multiple people simultaneously. This is the job of **Object Detection**: find every object in the image, draw a tight bounding box around it, and label it.

The output of a detection model isn't a single class label — it's a list of detected objects, each represented as:
- `(class_label, confidence_score, x1, y1, x2, y2)` — the class, how confident the model is, and the box's top-left and bottom-right pixel coordinates.

### How YOLO Works

YOLO (You Only Look Once) divides the image into an **S×S grid**. Each grid cell simultaneously predicts:
1. **B bounding boxes**, each described by (x_center, y_center, width, height) relative to that cell, plus a confidence score of how likely it is that a real object is centered there.
2. **C class probabilities** — what object is this if there is one?

The key word is *simultaneously*. Unlike older two-stage detectors (like Faster R-CNN) that first find candidate regions then classify them in a second pass, YOLO does everything in one single forward pass of the network. This makes it fast enough for real-time video detection.

### Running YOLOv8 on a Real Image

```python
# Install the ultralytics library which provides the modern YOLOv8 model
# pip install ultralytics

from ultralytics import YOLO
from PIL import Image
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Download a test image
url = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"
urllib.request.urlretrieve(url, "test_dog.jpg")

# YOLOv8 comes in 5 sizes: nano (n), small (s), medium (m), large (l), extra-large (x)
# Nano is fastest and smallest (good for testing), x is most accurate (needs more GPU memory)
# The weights are downloaded automatically from the internet on first use
model = YOLO('yolov8n.pt')

# Running inference is a single line. It returns a list (one result per image)
results = model('test_dog.jpg')
```

When you call `model('test_dog.jpg')`, YOLOv8 resizes the image, runs it through the network, and applies Non-Maximum Suppression (NMS) to remove duplicate boxes (when two boxes overlap heavily, keep only the most confident one). The `result.boxes` attribute gives you structured access to all the detected objects.

```python
result = results[0]  # Get the result for our single image

# Iterate through each detected object
for box in result.boxes:
    class_id    = int(box.cls[0])         # Integer index into the class list
    class_name  = model.names[class_id]  # Human-readable label from the model's dict
    confidence  = float(box.conf[0])     # Confidence score between 0 and 1
    x1, y1, x2, y2 = box.xyxy[0].tolist()  # Box coords in absolute pixel values

    print(f"Detected: {class_name:<15} Confidence: {confidence:.1%}  "
          f"Box: ({x1:.0f}, {y1:.0f}) → ({x2:.0f}, {y2:.0f})")
```

Now let's draw those detections on the image using matplotlib. Matplotlib's `patches.Rectangle` lets us draw a box by specifying the top-left corner and the width/height. We calculate width and height from the YOLO output's `x1,y1,x2,y2` format.

```python
img = Image.open("test_dog.jpg")
fig, ax = plt.subplots(1, figsize=(10, 8))
ax.imshow(img)

for box in result.boxes:
    class_id   = int(box.cls[0])
    class_name = model.names[class_id]
    conf       = float(box.conf[0])
    x1, y1, x2, y2 = box.xyxy[0].tolist()
    
    width  = x2 - x1
    height = y2 - y1
    
    # Draw a red rectangle — facecolor='none' means transparent fill
    rect = patches.Rectangle(
        (x1, y1), width, height,
        linewidth=2, edgecolor='red', facecolor='none'
    )
    ax.add_patch(rect)
    
    # Add a label above the box
    ax.text(x1, y1 - 5, f'{class_name} {conf:.0%}',
            color='white', fontsize=12, backgroundcolor='red')

ax.axis('off')
plt.title("YOLOv8 Object Detection")
# plt.show()
```

---

### IoU: Measuring Detection Accuracy

To evaluate whether a detection is "correct," we need to measure how well the predicted box overlaps with the human-labeled ground-truth box. This metric is called **Intersection over Union (IoU)**:

```
         Area of Intersection
IoU = ──────────────────────────
          Area of Union
```

An IoU of 1.0 means perfect overlap. An IoU below 0.5 is typically considered a failed detection. The calculation works by first finding the coordinates of the overlapping rectangle (the intersection), then computing areas using simple width × height math.

```python
def calculate_iou(box1, box2):
    """
    Calculates IoU between two bounding boxes in [x1, y1, x2, y2] format.
    box1 = predicted box, box2 = ground truth box
    """
    # The intersection rectangle starts at the rightmost left edge and
    # the bottommost top edge, and ends at the leftmost right edge and 
    # the topmost bottom edge.
    x_left   = max(box1[0], box2[0])
    y_top    = max(box1[1], box2[1])
    x_right  = min(box1[2], box2[2])
    y_bottom = min(box1[3], box2[3])
    
    # If the right edge is to the left of the left edge, they don't overlap at all
    if x_right < x_left or y_bottom < y_top:
        return 0.0
    
    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    
    # Union = total area covered by both boxes, minus the overlapping part counted twice
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
    union_area = box1_area + box2_area - intersection_area
    
    return intersection_area / union_area

# Test it
predicted = [50, 50, 200, 200]   # Model's predicted box
truth     = [60, 60, 210, 210]   # Human-labeled ground truth

iou = calculate_iou(predicted, truth)
print(f"IoU: {iou:.4f}")  # High number = good detection
```

---

## Part 2: Semantic Segmentation with U-Net

### Moving Beyond Bounding Boxes

Object detection gives us boxes around objects, but sometimes we need pixel-perfect boundaries. In medical imaging, you need to know exactly which pixels are tumor tissue. In autonomous driving, you need the exact shape of the road ahead. This is **Semantic Segmentation**: classifying every single pixel in the image into a category.

The challenge is that standard CNNs shrink spatial dimensions down to a small feature vector for classification. Segmentation needs the *opposite* — the output must be the same height and width as the input. U-Net solves this with a clever encoder-decoder structure.

### The U-Net Architecture

```
Encoder Path (going down):      Decoder Path (going back up):
Input [3, H, W]                 Output [num_classes, H, W]
   │                                         ↑
 ConvBlock → 64 ──────── skip ──────────► Concat → ConvBlock
   │                                         ↑
 ConvBlock → 128 ─────── skip ──────────► Concat → ConvBlock
   │                                         ↑
 ConvBlock → 256 ─────── skip ──────────► Concat → ConvBlock
   │                                         ↑
 ConvBlock → 512 ─────── skip ──────────► Concat → ConvBlock
   │                                         ↑
   └──── Bottleneck [1024] ─────────────────┘
```

The encoder (left side) is a standard CNN that shrinks spatial size at each level while extracting richer features. But instead of discarding the intermediate feature maps, U-Net **saves them** (the "skip connections"). The decoder (right side) uses Transposed Convolutions to upscale the spatial size back to the original, and at each step it **concatenates** the saved encoder feature map of the same scale. This gives the decoder access to both high-level semantic understanding (from the bottleneck) and precise spatial detail (from the skip connections).

### Building the U-Net from Scratch

First, the basic building block — two convolutions that form each level of the U:

```python
import torch
import torch.nn as nn

class ConvBlock(nn.Module):
    """Two sequential Conv → BN → ReLU operations. This is the core U-Net unit.
    Each level of both the encoder and decoder uses one of these blocks."""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.block = nn.Sequential(
            # First conv may change the channel count
            nn.Conv2d(in_channels,  out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            # Second conv keeps channel count the same, refines the features
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )
    def forward(self, x):
        return self.block(x)
```

Now the full U-Net. The encoder uses `MaxPool2d` to halve spatial resolution after each `ConvBlock`. The decoder uses `ConvTranspose2d` — the learnable inverse of convolution — to double the spatial size. After each upsampling, the decoder concatenates the skip connection along the channel dimension (hence `in_channels * 2` in the decoder blocks), then runs a `ConvBlock` to fuse that combined information.

```python
class UNet(nn.Module):
    def __init__(self, in_channels=3, num_classes=2, features=[64, 128, 256, 512]):
        super().__init__()
        
        # --- ENCODER ---
        # We'll build these dynamically so the feature sizes can be customized
        self.encoder_blocks = nn.ModuleList()
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)  # Halves H and W each time
        
        current_channels = in_channels
        for feature in features:
            self.encoder_blocks.append(ConvBlock(current_channels, feature))
            current_channels = feature  # Track what channel count we're at
        
        # --- BOTTLENECK ---
        # The deepest point: features[-1] channels go in, features[-1]*2 come out
        self.bottleneck = ConvBlock(features[-1], features[-1] * 2)
        
        # --- DECODER ---
        # Built in reverse: from deepest to shallowest
        self.decoder_upsamples = nn.ModuleList()
        self.decoder_blocks    = nn.ModuleList()
        
        for feature in reversed(features):
            # ConvTranspose2d doubles H and W — it's the learnable upsampling layer
            # It takes (feature*2) channels in (from the previous level) and outputs (feature)
            self.decoder_upsamples.append(
                nn.ConvTranspose2d(feature * 2, feature, kernel_size=2, stride=2)
            )
            # After upsampling, we concatenate the skip connection.
            # The skip has (feature) channels, the upsampled also has (feature), 
            # so after cat we have (feature*2). The ConvBlock reduces back to (feature).
            self.decoder_blocks.append(ConvBlock(feature * 2, feature))
        
        # --- OUTPUT ---
        # A 1×1 conv maps the (features[0]=64) channels to (num_classes) output channels.
        # Each output "channel" becomes the score for one segmentation class per pixel.
        self.final_conv = nn.Conv2d(features[0], num_classes, kernel_size=1)
    
    def forward(self, x):
        skip_connections = []
        
        # --- Encoder pass ---
        # Run each ConvBlock, save the output as a skip connection, then pool
        for encoder_block in self.encoder_blocks:
            x = encoder_block(x)
            skip_connections.append(x)  # Save BEFORE pooling (full resolution)
            x = self.pool(x)            # Pool AFTER saving
        
        # --- Bottleneck ---
        x = self.bottleneck(x)
        
        # Reverse the list so skip_connections[0] matches the first decoder level
        skip_connections = skip_connections[::-1]
        
        # --- Decoder pass ---
        for i, (upsample, decoder_block) in enumerate(
                zip(self.decoder_upsamples, self.decoder_blocks)):
            
            x = upsample(x)           # Double spatial size via transposed conv
            skip = skip_connections[i] # Get the matching-resolution encoder feature map
            
            # Concatenate along channels (dim=1). This is the crucial U-Net connection.
            # The decoder now sees both: the coarse features from deep in the network,
            # AND the fine spatial features from the corresponding encoder level.
            x = torch.cat([skip, x], dim=1)
            x = decoder_block(x)      # Fuse and refine the combined features
        
        # Final 1×1 conv to get per-pixel class scores
        return self.final_conv(x)
```

Let's verify the shapes flow correctly — the output must have the same H and W as the input:

```python
model = UNet(in_channels=3, num_classes=2)  # 2 classes: background and foreground
dummy_image = torch.randn(1, 3, 256, 256)
output = model(dummy_image)

print(f"Input shape:           {dummy_image.shape}")  # (1, 3, 256, 256)
print(f"Output shape:          {output.shape}")       # (1, 2, 256, 256) — same H, W!
# For each of the 256x256 = 65,536 pixels, we have 2 class scores (one per class)

# The final prediction for each pixel: take the class with the highest score
predicted_mask = output.argmax(dim=1)   # (1, 256, 256) — integer class index per pixel
print(f"Predicted mask shape:  {predicted_mask.shape}")

total_params = sum(p.numel() for p in model.parameters())
print(f"Total Parameters:      {total_params:,}")
```

### Training the Segmentation Model

The segmentation loss works identically to classification loss — it's `CrossEntropyLoss` — but it's applied to every single pixel independently. The key difference is the shape of the target: instead of a 1D vector of class indices `(Batch,)`, the segmentation target is a 2D map of class indices `(Batch, Height, Width)`.

```python
criterion = nn.CrossEntropyLoss()  # Works on any spatial size

# Target mask: each element is an integer class label (0=background, 1=foreground)
# Shape is (Batch, Height, Width) — NO channel dimension here!
target_mask = torch.zeros(1, 256, 256, dtype=torch.long)

# Simulate a foreground region: mark a 50x50 square as class 1 (foreground)
target_mask[0, 100:150, 100:150] = 1

# CrossEntropyLoss automatically computes the loss for each of the 65,536 pixels,
# then averages them into a single scalar loss value we can backpropagate
loss = criterion(output, target_mask)
print(f"Segmentation Loss: {loss.item():.4f}")

# During training, this loss flows back through the decoder and encoder,
# adjusting every weight to better predict the correct class for each pixel
```

---
## References
*   [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/)
*   [U-Net Original Paper: Convolutional Networks for Biomedical Image Segmentation](https://arxiv.org/abs/1505.04597)
*   [Papers with Code: Semantic Segmentation Leaderboard](https://paperswithcode.com/task/semantic-segmentation)
