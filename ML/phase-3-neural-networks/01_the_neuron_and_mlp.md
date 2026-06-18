# The Neuron and Multi-Layer Perceptrons (MLPs)

Welcome to Deep Learning! We start with the fundamental building block: the artificial neuron (or Perceptron).

## 1. The Artificial Neuron

A neuron does exactly two things:
1.  Computes a **weighted sum** of its inputs and adds a **bias**.
2.  Passes that sum through an **activation function** to introduce non-linearity.

Mathematically:
$$ z = w_1x_1 + w_2x_2 + ... + w_nx_n + b $$
$$ \text{output} = \text{Activation}(z) $$

Or, using linear algebra (vector dot product):
$$ z = W \cdot X + b $$

```python
import numpy as np

# A single neuron with 3 inputs
inputs = np.array([1.2, 0.5, -1.0])
weights = np.array([0.5, -0.2, 0.1])
bias = 0.1

# Step 1: Weighted sum + bias
z = np.dot(weights, inputs) + bias
print(f"Raw output (z): {z:.4f}")

# Step 2: Activation function (e.g., ReLU)
def relu(x):
    return np.maximum(0, x)

output = relu(z)
print(f"Neuron output: {output:.4f}")
```

## 2. Multi-Layer Perceptrons (MLPs)

A single neuron can only draw a straight line (it's essentially linear regression). To solve complex, non-linear problems, we stack them.
*   **Layer:** A collection of neurons operating in parallel.
*   **MLP:** Input Layer $\rightarrow$ Hidden Layer(s) $\rightarrow$ Output Layer.

When we group neurons into a layer, the weights become a **Matrix** instead of a vector.

```python
# A simple MLP (1 Hidden layer with 4 neurons, Output layer with 2 neurons)
# Let's say we have 1 sample with 3 features
X = np.array([[1.2, 0.5, -1.0]]) # Shape: (1, 3)

# Hidden Layer (4 neurons)
W1 = np.random.randn(3, 4) # 3 inputs, 4 neurons
b1 = np.zeros(4)           # 4 biases

# Output Layer (2 neurons)
W2 = np.random.randn(4, 2) # 4 inputs from hidden layer, 2 outputs
b2 = np.zeros(2)

# Forward Pass!
# Layer 1
z1 = np.dot(X, W1) + b1
a1 = relu(z1) # Shape: (1, 4)

# Layer 2 (Output)
z2 = np.dot(a1, W2) + b2
# (No activation here assuming we want raw logits, or we could use Softmax)
output = z2 # Shape: (1, 2)

print("MLP Output:\n", output)
```

## 3. Why Deep > Wide?

You could theoretically have a network with 1 hidden layer containing 1,000,000 neurons (Universal Approximation Theorem).
However, **deep** networks (many layers) are vastly superior to **wide** networks (one massive layer).
*   Deep networks learn **hierarchical / compositional features**. 
*   In image processing: Layer 1 learns edges. Layer 2 combines edges into shapes. Layer 3 combines shapes into faces.
*   A shallow network would have to memorize every possible face from scratch.

---
## References
*   [3Blue1Brown: What is a Neural Network?](https://www.youtube.com/watch?v=aircAruvnKk)
*   [Stanford CS231n: Neural Networks Part 1](https://cs231n.github.io/neural-networks-1/)
