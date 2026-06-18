# Object Detection and Segmentation

Image Classification asks: *"What is the main subject of this image?"*
Real-world applications usually require much more than that.

## 1. Object Detection

Object Detection asks: *"Where are all the objects in this image, and what are they?"*
The model must output a list of **Bounding Boxes** (x, y, width, height) and the predicted class for each box.

*   **R-CNN Family (Faster R-CNN):** A two-stage process. First, it proposes regions that might contain an object. Second, it classifies those regions. Very accurate, but historically slower.
*   **YOLO (You Only Look Once):** A single-stage process. It divides the image into a grid and predicts bounding boxes and classes for the grid cells all at once in a single forward pass. Incredibly fast, enabling real-time detection on video.

**Evaluation Metric: mAP (Mean Average Precision)**
To know if a predicted bounding box is correct, we calculate the **IoU (Intersection over Union)** between the predicted box and the ground-truth box. If the overlap is > 50%, it's considered a True Positive. mAP averages the precision across all classes and IoU thresholds.

## 2. Image Segmentation

Image Segmentation asks: *"Which specific pixels belong to which object?"*

*   **Semantic Segmentation:** Classifies every pixel into a category (e.g., road, sky, car). It does not distinguish between *different* cars. They are all just "car pixels."
*   **Instance Segmentation:** Identifies individual objects and their pixel masks (e.g., Car 1, Car 2). Mask R-CNN is the classic architecture for this.

**Architecture: U-Net**
Standard CNNs shrink the spatial dimensions down to a 1D vector to make a classification. For segmentation, the output must be the exact same height and width as the input image.

U-Net solves this with an Encoder-Decoder structure:
1.  **Encoder:** Standard CNN that shrinks dimensions and extracts deep features.
2.  **Decoder:** Transposed Convolutions (up-sampling) that blow the dimensions back up to the original size.
3.  **Skip Connections:** Directly connects high-resolution features from the encoder to the decoder so fine details aren't lost.

```python
# Pseudo-code for a Semantic Segmentation output
import torch

# Batch of 1 image, 3 classes (background, road, car), 256x256 resolution
segmentation_output = torch.randn(1, 3, 256, 256) 

# For every pixel, find the index of the class with the highest score
# output shape: (1, 256, 256) - Each pixel now contains an integer 0, 1, or 2
predicted_mask = torch.argmax(segmentation_output, dim=1) 
```

---
## References
*   [Ultralytics YOLO (The standard library for Object Detection)](https://docs.ultralytics.com/)
*   [PapersWithCode: U-Net Architecture](https://paperswithcode.com/method/u-net)
