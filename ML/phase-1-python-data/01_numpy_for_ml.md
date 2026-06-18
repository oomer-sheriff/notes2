# NumPy for Machine Learning

While standard Python is great for backend web development, it is too slow for machine learning. Loops in Python carry too much overhead. **NumPy** is the foundation of scientific computing in Python because it executes operations in highly optimized C code under the hood.

In ML, you must train yourself to stop writing `for` loops and start writing **vectorized operations**.

## 1. Vectorization

Vectorization is the process of performing operations on entire arrays at once, rather than iterating through individual elements.

```python
import numpy as np
import time

# Create a large array of 10 million random numbers
data = np.random.rand(10000000)

# The bad way (Python loop)
start_time = time.time()
squared_loop = [x**2 for x in data]
print(f"Loop time: {time.time() - start_time:.4f} seconds")

# The right way (NumPy Vectorization)
start_time = time.time()
squared_vectorized = data ** 2
print(f"Vectorized time: {time.time() - start_time:.4f} seconds")
# Result: Vectorization is typically 50x to 100x faster!
```

## 2. Broadcasting

Broadcasting is how NumPy handles mathematical operations between arrays of different shapes. Instead of forcing you to manually duplicate arrays to match shapes, NumPy "broadcasts" the smaller array across the larger one.

```python
import numpy as np

# Suppose we have a matrix of 3 houses, each with 2 features (e.g., size, age)
houses = np.array([
    [1000, 10],
    [2000, 5],
    [1500, 2]
]) # Shape: (3, 2)

# We want to add a base value of 50 to size, and 1 to age for ALL houses.
# We can just add a 1D vector!
adjustments = np.array([50, 1]) # Shape: (2,)

# NumPy automatically "broadcasts" the (2,) vector to (3, 2) to perform the addition.
new_houses = houses + adjustments

print(new_houses)
# [[1050   11]
#  [2050    6]
#  [1550    3]]
```
*Rule of Broadcasting:* Two dimensions are compatible if they are equal, or if one of them is 1.

## 3. Reshaping and Stacking

In neural networks, you constantly need to change the shape of your data (e.g., flattening a 2D image into a 1D vector before passing it to a linear layer).

```python
import numpy as np

# Imagine a tiny 2x2 image with 3 color channels (RGB)
image = np.random.randint(0, 255, size=(2, 2, 3))
print("Original shape:", image.shape)

# Flatten it into a 1D vector (shape 12) for an MLP
flattened = image.reshape(-1) # -1 means "calculate this dimension automatically"
print("Flattened shape:", flattened.shape)

# Stacking batches
sample_1 = np.array([1, 2, 3])
sample_2 = np.array([4, 5, 6])

# Stack rows to create a dataset matrix
batch = np.vstack((sample_1, sample_2))
print("\nBatched:\n", batch)
print("Batch shape:", batch.shape) # (2, 3)
```

## 4. Reproducibility (Seeding)

Machine learning involves a lot of randomness (weight initialization, data shuffling). To debug effectively, you need your "random" numbers to be identical every time you run the script.

```python
import numpy as np

# Set the seed
np.random.seed(42)

print(np.random.rand(2)) # Always outputs: [0.37454012 0.95071431]
```

---
## References
*   [NumPy Official Documentation: Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)
*   [Python Data Science Handbook: Computation on NumPy Arrays](https://jakevdp.github.io/PythonDataScienceHandbook/02.03-computation-on-arrays-ufuncs.html)
