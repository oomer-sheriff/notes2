# Phase 1: Quick Reference & Cheat Sheet

## NumPy Basics
```python
import numpy as np

# Creation
arr = np.array([1, 2, 3])
zeros = np.zeros((3, 3))
random_nums = np.random.randn(3, 3) # Standard normal distribution

# Properties
print(arr.shape)
print(arr.dtype)

# Reshaping & Stacking
reshaped = arr.reshape(1, 3)
stacked = np.vstack([arr, arr])   # Stack vertically
concat = np.concatenate([arr, arr]) # Combine arrays
```

## Pandas Basics
```python
import pandas as pd

# Loading
df = pd.read_csv('data.csv')

# Exploration
df.head()        # First 5 rows
df.info()        # Datatypes and non-null counts
df.describe()    # Summary statistics (mean, min, max, etc.)
df.isnull().sum() # Count missing values per column

# Manipulation
df.dropna()                       # Drop rows with missing values
df.fillna(df['col'].mean())       # Fill missing values
df_encoded = pd.get_dummies(df)   # One-hot encode categorical columns
```

## Scikit-Learn Preprocessing
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Splitting
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train) # FIT and transform train data
X_test_scaled = scaler.transform(X_test)       # ONLY transform test data
```

## Matplotlib / Seaborn
```python
import matplotlib.pyplot as plt
import seaborn as sns

# Histogram
sns.histplot(data=df, x='age', kde=True)

# Scatter Plot
sns.scatterplot(data=df, x='feature1', y='feature2', hue='class_label')

# Heatmap (Correlation)
sns.heatmap(df.corr(), annot=True, cmap='coolwarm')

plt.show() # Display the plot
```
