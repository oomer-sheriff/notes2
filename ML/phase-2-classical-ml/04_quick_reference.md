# Phase 2: Quick Reference & Cheat Sheet

## Supervised Learning (scikit-learn)
```python
# 1. Import Model
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

# 2. Instantiate Model
model = RandomForestClassifier(n_estimators=100, max_depth=5)

# 3. Fit (Train) Model
model.fit(X_train, y_train)

# 4. Predict
predictions = model.predict(X_test)
probabilities = model.predict_proba(X_test) # For classifiers only
```

## Unsupervised Learning
```python
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# K-Means Clustering
kmeans = KMeans(n_clusters=3)
cluster_labels = kmeans.fit_predict(X)

# PCA Dimensionality Reduction
pca = PCA(n_components=2)
X_reduced = pca.fit_transform(X)
```

## Model Evaluation
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score

# Classification
acc = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')

# Regression
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# Cross Validation
scores = cross_val_score(model, X, y, cv=5)
```
