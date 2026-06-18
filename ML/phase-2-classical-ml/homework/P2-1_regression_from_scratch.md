# Task P2-1: Linear & Logistic Regression from Scratch

**Goal:** Prove you understand gradient descent by implementing Linear Regression using pure NumPy, then verifying it against `scikit-learn`.

Create a Jupyter Notebook in `homework/lab-files/` and implement the following.

### 1. The NumPy Implementation

Implement the following class. The `fit` method should use Gradient Descent to update `self.w` and `self.b`.

```python
import numpy as np

class LinearRegression:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr = lr
        self.epochs = epochs
    
    def fit(self, X, y):
        # 1. Initialize weights (self.w) to zeros, shape should match number of features
        # 2. Initialize bias (self.b) to 0
        # 3. Loop for self.epochs:
        #      a. Calculate predictions: y_pred = X @ w + b
        #      b. Calculate gradients:
        #         dw = (2 / N) * X.T @ (y_pred - y)
        #         db = (2 / N) * sum(y_pred - y)
        #      c. Update weights: w = w - lr * dw, b = b - lr * db
        pass
    
    def predict(self, X):
        # Return predictions using the trained weights
        pass
```

### 2. Testing and Comparison

1. Generate a dataset using `sklearn.datasets.make_regression`:
   ```python
   from sklearn.datasets import make_regression
   X, y = make_regression(n_samples=200, n_features=3, noise=15, random_state=42)
   ```
2. Train your custom `LinearRegression` model on this data. Print the final weights and bias.
3. Train `sklearn.linear_model.LinearRegression` on the same data. Print its weights (`coef_`) and bias (`intercept_`).
4. **Verification:** Your weights and the sklearn weights should be nearly identical.

### 3. Challenge: Logistic Regression
Duplicate your class and rename it `LogisticRegression`.
Modify the `predict` method to pass the output through a sigmoid function: `1 / (1 + np.exp(-z))`.
Modify the gradients (the formulas are actually the same, but `y_pred` is now the sigmoid output).
Test it on `sklearn.datasets.make_classification`.
