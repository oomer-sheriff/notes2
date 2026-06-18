# Calculus for Machine Learning

Calculus in machine learning is primarily about optimization: finding the minimum of a function (the loss function). To minimize the error of a model, we need to know which direction to change the weights, and calculus provides exactly that information.

## 1. Derivatives

A derivative measures the rate of change of a function at a specific point. 
*   If the derivative is positive, increasing the input increases the output.
*   If the derivative is negative, increasing the input decreases the output.
*   In ML, if the derivative of the loss with respect to a weight is positive, we should *decrease* that weight to lower the loss.

```python
import numpy as np

# A simple function: f(x) = x^2
def f(x):
    return x**2

# Numerical derivative (approximation)
def numerical_derivative(f, x, h=1e-5):
    return (f(x + h) - f(x - h)) / (2 * h)

x_val = 3.0
deriv = numerical_derivative(f, x_val)
print(f"Derivative of x^2 at x={x_val} is approx: {deriv:.2f}") 
# Matches analytical derivative: 2*x = 6.0
```

## 2. Partial Derivatives and Gradients

Neural networks don't have just one variable; they have millions of parameters (weights and biases).

### Partial Derivatives
A partial derivative ($\frac{\partial L}{\partial w_1}$) measures how the loss ($L$) changes when we slightly change *one specific weight* ($w_1$), assuming all other weights remain constant.

### Gradients
The **gradient** ($\nabla$) is simply a vector containing all the partial derivatives of the function.
*   $\nabla L = [\frac{\partial L}{\partial w_1}, \frac{\partial L}{\partial w_2}, ..., \frac{\partial L}{\partial w_n}]$
*   **Crucial Concept:** The gradient vector always points in the direction of the *steepest ascent* (the fastest way to increase the loss).
*   **Gradient Descent:** Since we want to minimize the loss, we take a step in the *opposite* direction of the gradient: $W_{new} = W_{old} - \text{learning\_rate} \times \nabla L$.

```python
# A simple Gradient Descent step
weight = 5.0
learning_rate = 0.1

# Let's say our loss function is L(w) = w^2
# The gradient (derivative) is dL/dw = 2*w
gradient = 2 * weight

print(f"Old weight: {weight}, Gradient: {gradient}")
# Take a step opposite to the gradient
weight = weight - (learning_rate * gradient)
print(f"New weight (moved downhill): {weight}") # Moved from 5.0 to 4.0
```

## 3. The Chain Rule and Backpropagation

The most important concept in deep learning is how to calculate the gradients for weights that are buried deep within multiple layers.

### The Chain Rule
If you have nested functions, like $y = f(g(x))$, the chain rule tells us how to find the derivative:
$$ \frac{dy}{dx} = \frac{dy}{dg} \cdot \frac{dg}{dx} $$

### Backpropagation
A neural network is a giant nested function: `Loss = LossFunction(Layer3(Layer2(Layer1(Input))))`.
**Backpropagation** is just the chain rule applied systematically from the output layer back to the input layer.

1.  Calculate how much the final prediction contributed to the loss.
2.  Calculate how much Layer 3 contributed to that prediction.
3.  Calculate how much Layer 2 contributed to Layer 3's output.
4.  ...and so on.

By multiplying these partial derivatives together backward through the network, we can find exactly how much a tiny weight in Layer 1 contributed to the final loss.

## 4. Why Does This Matter to a Practitioner?

When you call `loss.backward()` in PyTorch:
1.  PyTorch looks at the computational graph it built during the forward pass.
2.  It applies the chain rule backward from the `loss` variable.
3.  It populates the `.grad` attribute of every tensor (weight) that had `requires_grad=True`.

```python
import torch

# 1. Define our parameters (requires_grad=True tells PyTorch to track operations on them)
w = torch.tensor(2.0, requires_grad=True)
b = torch.tensor(-1.0, requires_grad=True)

# 2. Forward pass (build the computational graph)
x = torch.tensor(3.0) # Input
y_pred = w * x + b    # Prediction = 2.0*3.0 + (-1.0) = 5.0
y_true = torch.tensor(4.0) # Target

# Let's use simple squared error loss
loss = (y_pred - y_true)**2 # (5.0 - 4.0)^2 = 1.0

# 3. Backward pass (Calculates all gradients using the chain rule!)
loss.backward()

# 4. View the gradients computed for our weights
print(f"dL/dw: {w.grad}") # How much a change in 'w' affects the 'loss'
print(f"dL/db: {b.grad}")

# In a real training loop, you'd now use an optimizer to update the weights:
# optimizer.step()
```

---
## References
*   [GeeksforGeeks: Mathematics for Machine Learning - Calculus](https://www.geeksforgeeks.org/mathematics-for-machine-learning-calculus/)
*   [Medium: Calculus in Machine Learning](https://medium.com/@amansingh_27218/calculus-in-machine-learning-e5088eb48a31)
*   [Machine Learning Mastery: A Gentle Introduction to the Chain Rule](https://machinelearningmastery.com/a-gentle-introduction-to-the-chain-rule-of-calculus/)
