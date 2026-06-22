# Step-by-Step: Linear Regression & Gradient Descent

**Input:** 3 training samples, 2 features, 1 output (house price in $100k).

---

## 1. The Data

```
Sample   Area (x1)   Rooms (x2)   Price (y)
  1        1.0          1.0          2.0
  2        2.0          1.0          3.0
  3        3.0          2.0          5.0
```

In matrix form:

```
X = [[1.0, 1.0],    y = [[2.0],
     [2.0, 1.0],         [3.0],
     [3.0, 2.0]]         [5.0]]
```

We add a **bias column of 1s** to X so the bias weight `b` is included naturally in the dot product:

```
X_aug = [[1, 1.0, 1.0],
         [1, 2.0, 1.0],
         [1, 3.0, 2.0]]
```

Our model: `ŷ = X_aug @ w`  
Weights to learn: `w = [b, w1, w2]` (bias + weight for each feature)

---

## 2. Initialize Weights

Start with all zeros:

```
w = [0.0, 0.0, 0.0]   (bias=0, w1=0, w2=0)
```

---

## 3. Forward Pass (Step 1)

Compute prediction `ŷ = X_aug @ w`:

```
Sample 1: 1*0 + 1.0*0 + 1.0*0 = 0.0    (true: 2.0)
Sample 2: 1*0 + 2.0*0 + 1.0*0 = 0.0    (true: 3.0)
Sample 3: 1*0 + 3.0*0 + 2.0*0 = 0.0    (true: 5.0)

ŷ = [0.0, 0.0, 0.0]
```

Compute **MSE Loss**:

```
errors   = ŷ - y     = [0-2, 0-3, 0-5] = [-2, -3, -5]
errors²  = [4, 9, 25]
MSE Loss = mean([4, 9, 25]) = 38/3 ≈ 12.67
```

---

## 4. Compute the Gradient

The gradient of MSE loss w.r.t. weights `w` is:

```
∂Loss/∂w = (2/n) * X_aug.T @ (ŷ - y)
```

Step-by-step:

```
(ŷ - y) = [-2, -3, -5]          (error vector, shape 3×1)

X_aug.T:                          (shape 3×3 transposed to 3×3)
col 0: [1,   1,   1  ]  ← bias terms
col 1: [1.0, 2.0, 3.0]  ← x1 (area)
col 2: [1.0, 1.0, 2.0]  ← x2 (rooms)

X_aug.T @ (ŷ - y):
 Row 0 (bias): 1*(-2) + 1*(-3) + 1*(-5) = -10
 Row 1 (w1):  1*(-2) + 2*(-3) + 3*(-5)  = -2-6-15 = -23
 Row 2 (w2):  1*(-2) + 1*(-3) + 2*(-5)  = -2-3-10 = -15

Result = [-10, -23, -15]

Gradient = (2/3) * [-10, -23, -15] = [-6.67, -15.33, -10.0]
```

---

## 5. Update Weights (Gradient Descent)

Learning rate `lr = 0.1`. Update rule: `w ← w - lr * gradient`

```
w[0] (bias) = 0.0 - 0.1 * (-6.67)  = 0.0 + 0.667  =  0.667
w[1] (w1)   = 0.0 - 0.1 * (-15.33) = 0.0 + 1.533  =  1.533
w[2] (w2)   = 0.0 - 0.1 * (-10.0)  = 0.0 + 1.0    =  1.0

w_new = [0.667, 1.533, 1.0]
```

---

## 6. Forward Pass (Step 2 — After 1 Update)

```
Sample 1: 1*0.667 + 1.0*1.533 + 1.0*1.0 = 3.2    (true: 2.0)
Sample 2: 1*0.667 + 2.0*1.533 + 1.0*1.0 = 4.73   (true: 3.0)
Sample 3: 1*0.667 + 3.0*1.533 + 2.0*1.0 = 6.27   (true: 5.0)

ŷ = [3.2, 4.73, 6.27]
errors   = [1.2, 1.73, 1.27]
MSE Loss = mean([1.44, 2.99, 1.61]) = 2.01
```

**Loss dropped from 12.67 → 2.01 in a single update!**

---

## 7. What Converged Weights Should Look Like

After many iterations (true relationship: price ≈ 1.5*area + 0.5*rooms):

```
w ≈ [0.0, 1.5, 0.5]

Prediction for sample 3: 0 + 3.0*1.5 + 2.0*0.5 = 4.5 + 1.0 = 5.5 ≈ 5.0 ✓
```

---

## Key Takeaways

| Concept | What it does |
|---|---|
| `X_aug @ w` | Each sample's prediction: weighted sum of features |
| `ŷ - y` | Error: how wrong each prediction is |
| `X_aug.T @ errors` | How much each weight contributed to total error |
| `w -= lr * gradient` | Move weights in the direction that reduces error |
| Loss decreasing | The model is learning the true relationship |
