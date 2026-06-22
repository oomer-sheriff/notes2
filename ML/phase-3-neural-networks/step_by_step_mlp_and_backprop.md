# Step-by-Step: MLP Forward Pass + Backpropagation

**Network:** 2 inputs → 2 hidden neurons (ReLU) → 1 output (Sigmoid for binary classification).

---

## 1. Network Structure

```
Input layer:   x = [x1, x2] = [2.0, 3.0]
True label:    y = 1.0  (positive class)

Hidden layer:  2 neurons with ReLU activation
Output layer:  1 neuron with Sigmoid activation
```

## 2. Initialized Weights

```
Hidden layer weights (W1): shape (2 inputs × 2 hidden)
  W1 = [[0.5,  -0.2],
        [0.3,   0.8]]

Hidden layer biases (b1): shape (2,)
  b1 = [0.1, -0.1]

Output layer weights (W2): shape (2 hidden × 1 output)
  W2 = [[0.7],
        [-0.4]]

Output layer bias (b2): shape (1,)
  b2 = [0.2]
```

---

## 3. Forward Pass

### Layer 1: Compute Pre-activation z1 = W1.T @ x + b1

```
z1[0] = x1*W1[0,0] + x2*W1[1,0] + b1[0]
      = 2.0*0.5  +  3.0*0.3  + 0.1
      = 1.0 + 0.9 + 0.1
      = 2.0

z1[1] = x1*W1[0,1] + x2*W1[1,1] + b1[1]
      = 2.0*(-0.2) + 3.0*0.8  + (-0.1)
      = -0.4 + 2.4 - 0.1
      = 1.9

z1 = [2.0, 1.9]
```

### Layer 1: Apply ReLU activation a1 = max(0, z1)

```
a1[0] = max(0, 2.0)  = 2.0   (positive → unchanged)
a1[1] = max(0, 1.9)  = 1.9   (positive → unchanged)

a1 = [2.0, 1.9]
```

*(If z1[0] were -2.0, ReLU would output 0.0 — the neuron "dies" for this input)*

### Output Layer: Compute z2 = W2.T @ a1 + b2

```
z2 = a1[0]*W2[0,0] + a1[1]*W2[1,0] + b2[0]
   = 2.0*0.7  + 1.9*(-0.4)  + 0.2
   = 1.4 - 0.76 + 0.2
   = 0.84

z2 = 0.84
```

### Output Layer: Apply Sigmoid activation ŷ = σ(z2)

```
σ(x) = 1 / (1 + e^(-x))

ŷ = σ(0.84) = 1 / (1 + e^(-0.84))
             = 1 / (1 + 0.4317)
             = 1 / 1.4317
             ≈ 0.699
```

**Prediction: 0.699 (69.9% probability of class 1) — correct direction! (true label = 1)**

---

## 4. Compute Binary Cross-Entropy Loss

```
BCE Loss = -[y * log(ŷ) + (1-y) * log(1-ŷ)]
         = -[1.0 * log(0.699) + 0.0 * log(0.301)]
         = -[1.0 * (-0.358)  + 0]
         = 0.358
```

---

## 5. Backward Pass (Backpropagation)

We compute gradients using the **Chain Rule**, flowing backwards from the loss.

### Step 1: Gradient of Loss w.r.t. Output Neuron

For Sigmoid + BCE, the gradient simplifies beautifully to:

```
∂Loss/∂z2 = ŷ - y = 0.699 - 1.0 = -0.301
```

*(This elegant simplification is why Sigmoid+BCE and Softmax+CrossEntropy are paired together)*

### Step 2: Gradient w.r.t. Output Weights W2

```
∂Loss/∂W2[0] = (∂Loss/∂z2) * a1[0] = (-0.301) * 2.0 = -0.602
∂Loss/∂W2[1] = (∂Loss/∂z2) * a1[1] = (-0.301) * 1.9 = -0.572
∂Loss/∂b2    = (∂Loss/∂z2) * 1     = -0.301
```

### Step 3: Gradient w.r.t. Hidden Activations a1

```
∂Loss/∂a1[0] = (∂Loss/∂z2) * W2[0,0] = (-0.301) * 0.7  = -0.211
∂Loss/∂a1[1] = (∂Loss/∂z2) * W2[1,0] = (-0.301) * (-0.4) = 0.120
```

### Step 4: Gradient Through ReLU (∂a1/∂z1)

ReLU derivative: 1 if z > 0, else 0. Since both z1 values were positive:

```
∂a1[0]/∂z1[0] = 1   (z1[0]=2.0 > 0)
∂a1[1]/∂z1[1] = 1   (z1[1]=1.9 > 0)

∂Loss/∂z1[0] = ∂Loss/∂a1[0] * ∂a1[0]/∂z1[0] = -0.211 * 1 = -0.211
∂Loss/∂z1[1] = ∂Loss/∂a1[1] * ∂a1[1]/∂z1[1] =  0.120 * 1 =  0.120
```

### Step 5: Gradient w.r.t. Hidden Weights W1

```
∂Loss/∂W1[0,0] = (∂Loss/∂z1[0]) * x1 = (-0.211) * 2.0 = -0.422
∂Loss/∂W1[1,0] = (∂Loss/∂z1[0]) * x2 = (-0.211) * 3.0 = -0.633

∂Loss/∂W1[0,1] = (∂Loss/∂z1[1]) * x1 = (0.120) * 2.0  =  0.240
∂Loss/∂W1[1,1] = (∂Loss/∂z1[1]) * x2 = (0.120) * 3.0  =  0.360

∂Loss/∂b1[0]   = -0.211
∂Loss/∂b1[1]   =  0.120
```

---

## 6. Weight Update (Learning Rate = 0.1)

```
W2 updated:
  W2[0] = 0.7  - 0.1*(-0.602) = 0.7  + 0.060  = 0.760
  W2[1] = -0.4 - 0.1*(-0.572) = -0.4 + 0.057  = -0.343
  b2    = 0.2  - 0.1*(-0.301) = 0.2  + 0.030  = 0.230

W1 updated:
  W1[0,0] = 0.5  - 0.1*(-0.422) = 0.542
  W1[1,0] = 0.3  - 0.1*(-0.633) = 0.363
  W1[0,1] = -0.2 - 0.1*(0.240)  = -0.224
  W1[1,1] = 0.8  - 0.1*(0.360)  = 0.764
```

---

## 7. Verify: Forward Pass with Updated Weights

```
z1[0] = 2.0*0.542 + 3.0*0.363 + 0.1 = 1.084 + 1.089 + 0.1 = 2.273
z1[1] = 2.0*(-0.224) + 3.0*0.764 - 0.1 = -0.448 + 2.292 - 0.1 = 1.744

a1 = [2.273, 1.744]

z2 = 2.273*0.760 + 1.744*(-0.343) + 0.230
   = 1.727 - 0.598 + 0.230 = 1.359

ŷ = σ(1.359) = 1/(1+e^(-1.359)) ≈ 0.796
```

**Prediction improved from 0.699 → 0.796 (closer to true label 1.0)**

Loss = -log(0.796) ≈ 0.228 **(down from 0.358)**

---

## Key Takeaways

| Step | What we compute | Direction |
|---|---|---|
| z = Wx + b | Linear transform (pre-activation) | Forward |
| a = activation(z) | Non-linearity | Forward |
| Loss = BCE(ŷ, y) | How wrong are we? | Forward |
| ∂Loss/∂z2 = ŷ - y | Output gradient (free shortcut) | Backward |
| ∂Loss/∂a1 = dz2 · W2 | Propagate gradient to hidden | Backward |
| ∂Loss/∂z1 = da1 · ReLU' | Kill gradient if neuron was dead | Backward |
| ∂Loss/∂W1 = dz1 · x | How each weight contributed | Backward |
| w -= lr · ∂Loss/∂w | Gradient descent step | Update |
