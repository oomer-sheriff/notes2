# Pandas for Machine Learning

While NumPy handles the heavy mathematical lifting, **Pandas** is used for data manipulation and exploratory data analysis (EDA). Before you train a model, you must load, clean, and format your data. In the real world, this takes up 80% of an ML engineer's time.

## 1. Data Cleaning

Machine learning models cannot handle missing values (`NaN`) or raw text strings. Data must be cleaned and numericalized.

```python
import pandas as pd
import numpy as np

# Create a messy sample dataset
data = {
    'Age': [25, np.nan, 30, 22],
    'Salary': [50000, 60000, np.nan, 45000],
    'City': ['New York', 'London', 'London', 'Paris']
}
df = pd.DataFrame(data)
print("--- Raw Data ---")
print(df)

# Check for missing values
print("\n--- Missing Values ---")
print(df.isnull().sum())

# Strategy 1: Drop missing rows (often bad if you lose too much data)
# df_clean = df.dropna()

# Strategy 2: Imputation (Fill missing values with mean or median)
df['Age'] = df['Age'].fillna(df['Age'].mean())
df['Salary'] = df['Salary'].fillna(df['Salary'].median())

print("\n--- After Imputation ---")
print(df)
```

## 2. Feature Engineering (Encoding)

Models require numbers. Categorical features (like "City" or "Color") must be converted.

*   **Label Encoding:** Converts categories to integers (0, 1, 2). Bad for unordered categories because the model might assume 2 is "greater" than 0.
*   **One-Hot Encoding:** Creates a new binary column for every category. The preferred method for unordered categories.

```python
# One-Hot Encode the 'City' column using Pandas
df_encoded = pd.get_dummies(df, columns=['City'], drop_first=False)

print("\n--- After One-Hot Encoding ---")
print(df_encoded)
# Output will have columns like 'City_London', 'City_New York', 'City_Paris' 
# filled with True/False (or 1/0).
```

## 3. Scaling and Splitting

Features with large numbers (Salary: 50,000) will dominate features with small numbers (Age: 25) during gradient descent. You must scale your features so they are on a similar range (e.g., mean of 0, standard deviation of 1). 

Furthermore, you must NEVER train on your test data.

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Assume df_encoded is our final clean dataset
X = df_encoded.drop('Salary', axis=1) # Features
y = df_encoded['Salary']              # Target variable

# 1. Split the data (80% train, 20% test)
# random_state ensures reproducibility
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Scale the data
scaler = StandardScaler()

# CRITICAL: Only 'fit' the scaler on the training data to prevent data leakage!
X_train_scaled = scaler.fit_transform(X_train)

# Use the rules learned from the train set to transform the test set
X_test_scaled = scaler.transform(X_test)

print("\n--- Scaled Training Data ---")
print(np.round(X_train_scaled, 2))
```

---
## References
*   [Pandas Official Guide: 10 Minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)
*   [Scikit-Learn: Importance of Feature Scaling](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html)
