# Phase 2: Classical Machine Learning

> **Goal:** Understand non-deep-learning models. They are often faster, cheaper, and more interpretable than neural nets.
> **Duration:** 2-3 weeks

## Core Concepts

### Supervised Learning
Learning a mapping from inputs $X$ to outputs $y$ using labeled data.
- **Regression:** Predict continuous values (e.g., house price).
  - *Models:* Linear Regression, Ridge, Lasso.
- **Classification:** Predict discrete categories (e.g., spam vs. not spam).
  - *Models:* Logistic Regression, Decision Trees, Random Forests, XGBoost, SVMs.

### Unsupervised Learning
Finding patterns in unlabeled data.
- **Clustering:** Grouping similar data points.
  - *Models:* K-Means, DBSCAN.
- **Dimensionality Reduction:** Compressing features while retaining information.
  - *Models:* PCA, t-SNE.

## Key Terminology
- **Overfitting:** Model memorizes training data, performs poorly on new data. (High variance).
- **Underfitting:** Model is too simple to capture patterns. (High bias).
- **Cross-Validation:** Splitting data into $k$ folds to robustly evaluate model performance.

## The King of Tabular Data: XGBoost
For structured/tabular data (CSV files, SQL tables), **Gradient Boosted Trees (XGBoost, LightGBM)** usually beat deep neural networks.

## Homework
- Complete `homework/P2-1_xgboost_pipeline.md`
