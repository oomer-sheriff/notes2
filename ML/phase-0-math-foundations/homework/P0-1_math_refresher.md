# Task P0-1: Math Refresher (NumPy Basics)

**Goal:** Translate math formulas into fast NumPy operations.

Create a Jupyter Notebook or Python script in `homework/lab-files/` and implement the following.

### 1. Matrix Multiplication Without Loops
Given two matrices:
```python
import numpy as np

A = np.random.rand(100, 50)
B = np.random.rand(50, 10)
```
1. Compute the matrix product $C = A \cdot B$ using NumPy.
2. Verify the shape of $C$ is `(100, 10)`.

### 2. Implement Softmax
The Softmax function turns an array of raw scores (logits) into a valid probability distribution (all values between 0 and 1, summing to 1).
Formula: $\sigma(z)_i = \frac{e^{z_i}}{\sum e^{z_j}}$

```python
def softmax(logits):
    # YOUR CODE HERE
    # Hint: use np.exp() and np.sum()
    pass

logits = np.array([2.0, 1.0, 0.1])
probabilities = softmax(logits)
print(probabilities) # Should sum to 1.0
```

### 3. Implement Binary Cross Entropy Loss
Given true labels ($y$) and predicted probabilities ($\hat{y}$):
Formula: $L = -\frac{1}{N} \sum [y \log(\hat{y}) + (1-y) \log(1-\hat{y})]$

```python
def bce_loss(y_true, y_pred):
    # YOUR CODE HERE
    # Hint: use np.log() and np.mean()
    # Note: Add a tiny value (like 1e-15) to y_pred before taking the log to prevent log(0) errors.
    pass

y_true = np.array([1, 0, 1, 1])
y_pred = np.array([0.9, 0.1, 0.8, 0.4])
print("BCE Loss:", bce_loss(y_true, y_pred))
```
