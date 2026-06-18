# Task P4-1: Convolution from Scratch

**Goal:** Remove the magic from `nn.Conv2d` by writing a convolution function yourself using raw NumPy loops.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. Load a Real Image
We will use a built-in image from `scikit-image`.
```python
import numpy as np
import matplotlib.pyplot as plt
from skimage import data
from skimage.color import rgb2gray

# Load a picture of a cat!
image = data.chelsea() 
# Convert to grayscale to keep it simple (1 channel instead of 3 RGB channels)
image_gray = rgb2gray(image) 

plt.imshow(image_gray, cmap='gray')
plt.show()
```

### 2. The Convolution Function
Implement the following function. Do not use PyTorch or SciPy's convolution functions! Use standard Python/NumPy nested `for` loops.

```python
def conv2d(image, kernel, stride=1, padding=0):
    """
    Applies a 2D convolution to a 2D NumPy array.
    """
    # 1. Pad the image with zeros if padding > 0
    if padding > 0:
        image = np.pad(image, padding, mode='constant')
    
    # 2. Calculate the output dimensions
    img_h, img_w = image.shape
    kernel_h, kernel_w = kernel.shape
    
    out_h = (img_h - kernel_h) // stride + 1
    out_w = (img_w - kernel_w) // stride + 1
    
    # 3. Create an empty output array of zeros
    output = np.zeros((out_h, out_w))
    
    # 4. Slide the kernel over the image
    # Hint: Loop over out_h and out_w. 
    # For each position, slice a region from the image, 
    # multiply it element-wise with the kernel, and sum the result!
    # Remember to multiply your indices by the stride!
    
    return output
```

### 3. Edge Detection
Create two different 3x3 kernels (filters):
```python
# Detects Horizontal Edges
sobel_y = np.array([[-1, -2, -1],
                    [ 0,  0,  0],
                    [ 1,  2,  1]])

# Detects Vertical Edges
sobel_x = np.array([[-1,  0,  1],
                    [-2,  0,  2],
                    [-1,  0,  1]])
```

Apply your `conv2d` function to the cat image using both kernels separately (use `stride=1, padding=1`).
Plot the original image, the horizontal edge image, and the vertical edge image side-by-side using `plt.subplots`.

*Question:* Can you explain mathematically why `sobel_x` creates bright pixels where there is a vertical edge in the image?
