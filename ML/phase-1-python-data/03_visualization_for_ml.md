# Visualization for Machine Learning

You cannot build a good model if you do not understand your data. Visualization is how you find outliers, discover correlations, and debug your model's performance.

The standard stack is **Matplotlib** (the foundational library) and **Seaborn** (a high-level wrapper around Matplotlib that looks better by default).

## 1. Feature Distributions

Before doing anything, you should look at the distribution of your features. Are they normally distributed? Are they skewed?

```python
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Generate fake age data (normal distribution)
ages = np.random.normal(loc=35, scale=10, size=1000)

plt.figure(figsize=(8, 4))
# sns.histplot automatically creates a histogram and a Kernel Density Estimate (KDE) curve
sns.histplot(ages, kde=True, bins=30, color='blue')
plt.title("Distribution of User Ages")
plt.xlabel("Age")
plt.ylabel("Count")
# plt.show() # Uncomment to render in a notebook
```

## 2. Finding Correlations

If two features are highly correlated (e.g., "House Square Footage" and "Number of Rooms"), they provide redundant information. A correlation heatmap quickly shows these relationships.

```python
import pandas as pd

# Create fake dataset
df = pd.DataFrame({
    'Size': np.random.rand(100),
    'Rooms': np.random.rand(100) * 2, # Weak correlation to size
    'Price': np.random.rand(100) * 5  # Strong correlation to size
})
# Force a strong correlation for demonstration
df['Rooms'] = df['Size'] * 1.5 + np.random.rand(100)*0.2
df['Price'] = df['Size'] * 10 + np.random.rand(100)*0.5

# Calculate the correlation matrix (-1 to 1)
corr_matrix = df.corr()

plt.figure(figsize=(6, 5))
# annot=True puts the numbers in the squares
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title("Feature Correlation Heatmap")
# plt.show()
```

## 3. Training Debugging: Learning Curves

When training neural networks, you MUST plot your training loss and validation loss over time (epochs). This is how you diagnose overfitting.

```python
# Fake loss data
epochs = np.arange(1, 21)
train_loss = np.exp(-0.2 * epochs) + 0.1 # Exponential decay
# Validation loss decreases then starts increasing (overfitting!)
val_loss = np.exp(-0.2 * epochs) + 0.1 + 0.01 * (epochs - 10)**2 * (epochs > 10) 

plt.figure(figsize=(8, 5))
plt.plot(epochs, train_loss, label='Training Loss', marker='o')
plt.plot(epochs, val_loss, label='Validation Loss', marker='x', color='red')

plt.axvline(x=10, color='gray', linestyle='--', label='Overfitting Starts Here')

plt.title("Learning Curve (Loss vs Epochs)")
plt.xlabel("Epoch")
plt.ylabel("Loss (MSE)")
plt.legend()
plt.grid(True)
# plt.show()
```

---
## References
*   [Seaborn Official Gallery](https://seaborn.pydata.org/examples/index.html)
*   [Machine Learning Mastery: How to Use Learning Curves to Diagnose ML Models](https://machinelearningmastery.com/learning-curves-for-diagnosing-machine-learning-model-performance/)
