# Linear Algebra for Machine Learning

Linear algebra is the "mathematics of data." In machine learning, almost everything is represented as a matrix or a vector, and training a model is essentially applying a series of linear algebra transformations.

## 1. The Basics: Scalars, Vectors, Matrices, and Tensors

*   **Scalar:** A single number (e.g., `x = 5`). In ML, a loss value or learning rate is a scalar.
*   **Vector:** A 1D array of numbers. Represents a single data point (e.g., a house's features: `[size, bedrooms, age]`) or a set of weights.
*   **Matrix:** A 2D grid of numbers. Typically represents a whole dataset, where rows are individual samples (houses) and columns are features (size, bedrooms). Neural network weights for a single layer are also stored in a matrix.
*   **Tensor:** A generalization of vectors and matrices to higher dimensions. An RGB image is a 3D tensor `[height, width, color_channels]`. A batch of images is a 4D tensor `[batch_size, height, width, color_channels]`.

```python
import numpy as np

# Scalar
loss = 0.5

# Vector (1D tensor)
house_features = np.array([1200.0, 3.0, 15.0]) # [size, bedrooms, age]
print(f"Vector shape: {house_features.shape}")

# Matrix (2D tensor) - 2 houses, 3 features each
dataset = np.array([
    [1200.0, 3.0, 15.0],
    [2500.0, 4.0, 2.0]
])
print(f"Matrix shape: {dataset.shape}")

# 3D Tensor (e.g., a tiny 2x2 RGB image)
image = np.array([
    [[255, 0, 0], [0, 255, 0]], # Row 1
    [[0, 0, 255], [255, 255, 255]] # Row 2
])
print(f"Tensor shape: {image.shape}") # (2, 2, 3) -> Height, Width, Channels
```

## 2. Core Operations

### Dot Product
The dot product of two vectors is a scalar. It measures how "aligned" two vectors are.
$$ a \cdot b = \sum_{i=1}^{n} a_i b_i $$
*   **ML Application:** Used everywhere, from calculating the weighted sum of inputs in a neuron to computing Attention scores in Transformers (where Query and Key vectors are dot-producted to find similarity).

```python
# Dot Product Example
weights = np.array([0.5, -0.2, 0.1])
inputs = np.array([1.0, 2.0, 3.0])

# Calculated as: (0.5*1.0) + (-0.2*2.0) + (0.1*3.0)
neuron_output = np.dot(weights, inputs) 
print(f"Dot product: {neuron_output}") # Output: 0.4
```

### Matrix Multiplication
Multiplying two matrices (or a matrix and a vector) is the core computational bottleneck in deep learning.
*   If you have a layer of 100 neurons, and an input vector of 50 features, calculating the output is a matrix multiplication: $W \cdot x + b$, where $W$ is a $(100 \times 50)$ matrix and $x$ is a $(50 \times 1)$ vector.
*   **Why GPUs?** GPUs are specifically designed to perform thousands of simple matrix multiplications in parallel, making them vastly superior to CPUs for ML.

```python
# Matrix Multiplication Example (Forward Pass of a Linear Layer)
# Let's say we have 2 samples (batch size = 2), and 3 features per sample
X = np.array([
    [1.0, 2.0, 3.0], # Sample 1
    [4.0, 5.0, 6.0]  # Sample 2
]) # Shape: (2, 3)

# We want to output 2 predictions per sample (e.g., probability of Cat vs Dog)
# Our weights matrix must be shape (3, 2) to align the dimensions.
W = np.array([
    [0.1, 0.2],
    [0.3, 0.4],
    [0.5, 0.6]
]) # Shape: (3, 2)

# Matrix multiplication: (2x3) @ (3x2) -> (2x2) output
predictions = np.matmul(X, W) # or simply X @ W in Python 3.5+
print("Predictions matrix:\n", predictions)
```

### Transpose ($A^T$)
Flipping a matrix over its diagonal (rows become columns, columns become rows).
*   **ML Application:** Essential for making dimensions align before matrix multiplication. If $X$ is $(N \times M)$ and weights $W$ are $(N \times M)$, you might need to compute $X \cdot W^T$.

```python
# Transpose Example
A = np.array([
    [1, 2, 3],
    [4, 5, 6]
]) # Shape: (2, 3)

A_T = A.T # Shape: (3, 2)
print("Original:\n", A)
print("Transposed:\n", A_T)

# Why it's useful: if weights are shape (3, 2) but you need them to be (2, 3) to multiply with an input
```

## 3. Advanced Concepts: Eigenvalues and SVD

### Eigenvectors and Eigenvalues
If you think of a matrix as a transformation (like stretching or rotating space), an **eigenvector** is a direction that doesn't change when that transformation is applied; it only gets scaled. The **eigenvalue** is the factor by which it scales.
*   $A \cdot v = \lambda \cdot v$ (where $A$ is a matrix, $v$ is the eigenvector, $\lambda$ is the eigenvalue)
*   **ML Application:** Used extensively in **Principal Component Analysis (PCA)** for dimensionality reduction. By finding the eigenvectors of a dataset's covariance matrix with the largest eigenvalues, we find the directions of maximum variance in the data.

### Singular Value Decomposition (SVD)
SVD is a way to factorize *any* matrix (unlike eigendecomposition, which requires square matrices). It breaks a matrix $A$ down into three simpler matrices: $A = U \Sigma V^T$.
*   **ML Application:**
    *   Dimensionality reduction (Truncated SVD is often used on sparse data like TF-IDF text representations).
    *   Recommendation systems (Collaborative filtering).
    *   Compressing large weight matrices in neural networks to speed up inference or reduce memory.

```python
# SVD Example (Dimensionality Reduction / Compression)
# Let's create a fake user-item rating matrix (users x movies)
ratings = np.array([
    [5, 5, 0, 0], # User 1 likes Sci-Fi
    [4, 5, 0, 0], # User 2 likes Sci-Fi
    [0, 0, 4, 5], # User 3 likes Romance
    [0, 0, 5, 4]  # User 4 likes Romance
], dtype=float)

# Perform SVD
U, Sigma, VT = np.linalg.svd(ratings)

print("Original singular values (Sigma):", np.round(Sigma, 2))
# Notice the first two singular values are large, the rest are near zero.
# This means the data actually only has 2 underlying "latent features" (Sci-Fi and Romance)!

# We can compress the matrix by keeping only the top 2 singular values
k = 2
Sigma_k = np.diag(Sigma[:k])
U_k = U[:, :k]
VT_k = VT[:k, :]

# Reconstruct the matrix from the compressed version
compressed_ratings = U_k @ Sigma_k @ VT_k
print("\nReconstructed from 2 latent features:\n", np.round(compressed_ratings, 1))
```

---
## References
*   [GeeksforGeeks: Linear Algebra for Machine Learning](https://www.geeksforgeeks.org/linear-algebra-for-machine-learning/)
*   [Towards AI: Essential Linear Algebra for Machine Learning](https://towardsai.net/p/machine-learning/essential-linear-algebra-for-machine-learning)
*   [IBM: Linear Algebra](https://www.ibm.com/topics/linear-algebra)
