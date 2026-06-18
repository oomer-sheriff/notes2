# Task P2-3: Unsupervised Learning Lab

**Goal:** Practice K-Means, DBSCAN, and PCA on unstructured data.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. K-Means vs DBSCAN

Use sklearn to generate a dataset that is *not* composed of circular blobs.
```python
from sklearn.datasets import make_moons
import matplotlib.pyplot as plt

X, y = make_moons(n_samples=300, noise=0.05, random_state=42)
plt.scatter(X[:, 0], X[:, 1])
```
1. Run K-Means on this data with `n_clusters=2`. Plot the result. Notice how it draws a straight line through the middle, completely failing to capture the "moon" shapes.
2. Run DBSCAN on this data (`eps=0.2`, `min_samples=5`). Plot the result. Notice how it perfectly captures the density of the two moons.

### 2. PCA Dimensionality Reduction

We will use the digits dataset (8x8 pixel images of numbers 0-9).
```python
from sklearn.datasets import load_digits
digits = load_digits()
X = digits.data # Shape (1797, 64) - 64 dimensions!
y = digits.target
```

1. Train a `PCA` model on `X` to reduce the 64 dimensions down to just **2 dimensions**.
2. Create a scatter plot of the resulting 2D data. Color the points using the target labels `y` (`c=y`, `cmap='jet'`).
3. *Observe:* Even though you compressed 64 pixels into just 2 numbers, you should be able to see distinct clusters of colors where the different digits naturally group together.

### 3. Variance Explained
1. Train another PCA model, but don't specify `n_components`.
2. Plot the cumulative sum of `pca.explained_variance_ratio_`.
3. *Question:* How many components (dimensions) do you need to keep to retain 90% of the original variance (information)?
