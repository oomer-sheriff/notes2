# Step-by-Step: CNN Forward Pass (Convolution + Pooling + Classification)

**Input:** 4×4 grayscale image, 1 filter (3×3), then MaxPool, then classify.

---

## 1. The Input Image

```
Raw pixel values (4×4):

X = [[1, 0, 1, 0],
     [0, 1, 0, 1],
     [1, 1, 0, 0],
     [0, 0, 1, 1]]
```

Think of this as a tiny pattern — the 1s trace a checkerboard.

---

## 2. The Convolutional Filter

We use a **3×3 Sobel-like filter** for detecting vertical edges:

```
K = [[-1,  0,  1],
     [-2,  0,  2],
     [-1,  0,  1]]
```

This filter outputs a **large positive number** where the image goes dark→bright left-to-right (vertical edge), and a **large negative number** where it goes bright→dark.

**Stride = 1, Padding = 0** → output size: `(4-3)/1 + 1 = 2`

So the output feature map is **2×2**.

---

## 3. The Convolution Operation (Element-Wise Multiply + Sum)

The filter slides over every valid 3×3 region in the input.

**Position (0,0) — Top-left 3×3 region:**
```
Region:     Filter:         Product:
[[1, 0, 1],   [[-1, 0, 1],   [[-1, 0, 1],
 [0, 1, 0], ×  [-2, 0, 2], =  [ 0, 0, 0],
 [1, 1, 0]]    [-1, 0, 1]]    [-1, 0, 0]]

Sum all products: -1+0+1 + 0+0+0 + -1+0+0 = -1
Output[0,0] = -1
```

**Position (0,1) — Top-right 3×3 region:**
```
Region:     Filter:         Product:
[[0, 1, 0],   [[-1, 0, 1],   [[ 0, 0, 0],
 [1, 0, 1], ×  [-2, 0, 2], =  [-2, 0, 2],
 [1, 0, 0]]    [-1, 0, 1]]    [-1, 0, 0]]

Sum: 0+0+0 + -2+0+2 + -1+0+0 = -1
Output[0,1] = -1
```

**Position (1,0) — Bottom-left 3×3 region:**
```
Region:     Filter:         Product:
[[0, 1, 0],   [[-1, 0, 1],   [[ 0, 0, 0],
 [1, 1, 0], ×  [-2, 0, 2], =  [-2, 0, 0],
 [0, 0, 1]]    [-1, 0, 1]]    [ 0, 0, 1]]

Sum: 0+0+0 + -2+0+0 + 0+0+1 = -1
Output[1,0] = -1
```

**Position (1,1) — Bottom-right 3×3 region:**
```
Region:     Filter:         Product:
[[1, 0, 1],   [[-1, 0, 1],   [[-1, 0, 1],
 [1, 0, 0], ×  [-2, 0, 2], =  [-2, 0, 0],
 [0, 1, 1]]    [-1, 0, 1]]    [ 0, 0, 1]]

Sum: -1+0+1 + -2+0+0 + 0+0+1 = -1
Output[1,1] = -1
```

**Feature Map after Convolution:**
```
F = [[-1, -1],
     [-1, -1]]
```

This is the raw output before ReLU. The negative values tell us this filter found no strong left→right brightness increase in any region (makes sense for a checkerboard).

---

## 4. Apply ReLU

```
ReLU(x) = max(0, x)

ReLU(F) = [[max(0,-1), max(0,-1)],
           [max(0,-1), max(0,-1)]]
         = [[0, 0],
            [0, 0]]
```

All values are killed by ReLU because all convolution outputs were negative.

**What would activate this filter?** An image patch where the RIGHT side is brighter than the LEFT, like:

```
[[0, 0, 1],
 [0, 0, 1],
 [0, 0, 1]]
```

That would give: (-1×0)+(0×0)+(1×1) + (-2×0)+(0×0)+(2×1) + (-1×0)+(0×0)+(1×1) = 0+0+2+1 = ... = 4 → Strong activation!

---

## 5. Max Pooling

**2×2 MaxPool on a 4×4 map** (using the unfiltered image itself for a better demo):

Let's say after a different filter we got this 4×4 feature map:

```
F_raw = [[1, 3, 2, 4],
         [5, 6, 1, 2],
         [3, 2, 0, 1],
         [1, 2, 2, 3]]
```

Apply **2×2 MaxPool, stride 2** → splits into four 2×2 quadrants, takes max:

```
Top-left quadrant:     Top-right quadrant:
[[1, 3],               [[2, 4],
 [5, 6]]  → max = 6    [1, 2]]  → max = 4

Bottom-left quadrant:  Bottom-right quadrant:
[[3, 2],               [[0, 1],
 [1, 2]]  → max = 3    [2, 3]]  → max = 3

Pooled output (2×2):
[[6, 4],
 [3, 3]]
```

MaxPool halved the spatial size (4×4 → 2×2) while keeping the strongest activations.

---

## 6. Full CNN Forward Pass Summary

```
Input image: (1, 4, 4)      ← 1 channel, 4×4 pixels

    ↓ Conv2d (1→8 filters, 3×3, pad=0)
    
Feature maps: (8, 2, 2)     ← 8 filters each produce a 2×2 map
                               (in real networks with padding=1: still (8, 4, 4))
    ↓ ReLU

Feature maps: (8, 2, 2)     ← Negative values zeroed out

    ↓ MaxPool2d (2×2, stride=2)

Feature maps: (8, 1, 1)     ← Halved spatial dims: 2→1

    ↓ Flatten

Vector: (8,)                 ← 8 numbers, one per filter

    ↓ Linear (8 → 2)

Logits: (2,)                 ← One score per class

    ↓ Softmax

Probabilities: [0.7, 0.3]   ← 70% class 0, 30% class 1
```

---

## 7. What Different Filters Learn to Detect

In a real trained CNN:

```
Layer 1 filters detect:        Layer 2 filters detect:
  - Horizontal edges            - Corners (H-edge + V-edge)
  - Vertical edges              - Curves
  - Color gradients             - Textures
  - Diagonal edges

Layer 3+ filters detect:        Final layers detect:
  - Fur texture                 - "Dog face"
  - Wheel shapes                - "Car body"
  - Eye patterns                - "Building"
```

The early filters are **universal** (appear in all networks trained on images). The deeper filters are **task-specific** (what makes your dataset unique).

---

## Key Takeaways

| Operation | Shape change | What it does |
|---|---|---|
| Conv2d (no pad) | (H,W) → (H-F+1, W-F+1) | Detect local spatial patterns |
| Conv2d (pad=1) | (H,W) → (H, W) | Same, but preserves spatial size |
| ReLU | unchanged | Kill negative (absent) activations |
| MaxPool 2×2 | (H,W) → (H/2, W/2) | Downsample: keep strongest activation |
| Flatten | (C,H,W) → (C×H×W,) | Convert spatial map to 1D vector |
| Linear | (N,) → (num_classes,) | Final classification decision |
