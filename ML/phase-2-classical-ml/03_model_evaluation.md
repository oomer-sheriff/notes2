# Model Evaluation & Validation

A model is useless if you can't measure how well it performs on data it has *never seen before*.

## 1. Train / Validation / Test Splits

Never train and evaluate on the same data.
*   **Train Set (~70%):** The data the model learns from.
*   **Validation Set (~15%):** Used during training to tune hyperparameters (like learning rate or maximum tree depth).
*   **Test Set (~15%):** Kept completely secret until the very end. This gives you the final, unbiased accuracy metric.

## 2. Classification Metrics

Accuracy (correct predictions / total predictions) is often misleading. If 99% of emails are normal and 1% are spam, a model that *always* guesses "normal" has 99% accuracy but is completely useless.

**The Confusion Matrix:**
*   **True Positives (TP):** Predicted Spam, actually Spam.
*   **True Negatives (TN):** Predicted Normal, actually Normal.
*   **False Positives (FP):** Predicted Spam, actually Normal (Type I error).
*   **False Negatives (FN):** Predicted Normal, actually Spam (Type II error).

```python
from sklearn.metrics import confusion_matrix, classification_report
import numpy as np

# Fake data
y_true = np.array([0, 1, 0, 1, 1, 0])
y_pred = np.array([0, 1, 0, 0, 1, 1])

cm = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:\n", cm)
# [[TN  FP]
#  [FN  TP]]

# The classification report gives Precision, Recall, and F1-Score
print("\nClassification Report:\n", classification_report(y_true, y_pred))
```

*   **Precision:** Out of all the emails the model flagged as spam, how many were actually spam? $\frac{TP}{TP + FP}$
*   **Recall:** Out of all the actual spam emails in the dataset, how many did the model find? $\frac{TP}{TP + FN}$
*   **F1-Score:** The harmonic mean of Precision and Recall.

## 3. Regression Metrics

*   **Mean Squared Error (MSE):** Averages the squared differences between predictions and actuals. Penalizes large errors heavily.
*   **Mean Absolute Error (MAE):** Averages the absolute differences. Easier to interpret than MSE.
*   **R² (Coefficient of Determination):** How much of the variance in the target variable is explained by the model (1.0 is perfect, 0.0 is predicting the mean every time).

```python
from sklearn.metrics import mean_squared_error, r2_score

y_true_reg = np.array([3.0, -0.5, 2.0, 7.0])
y_pred_reg = np.array([2.5, 0.0, 2.0, 8.0])

print(f"MSE: {mean_squared_error(y_true_reg, y_pred_reg):.2f}")
print(f"R2 Score: {r2_score(y_true_reg, y_pred_reg):.2f}")
```

## 4. Cross-Validation

Instead of doing a single Train/Test split, K-Fold Cross Validation splits the data into $K$ chunks (folds). It trains on $K-1$ folds and tests on the remaining fold. It repeats this $K$ times and averages the performance. This gives a much more robust estimate of model performance, especially on small datasets.

```python
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

X, y = load_iris(return_X_y=True)
clf = RandomForestClassifier(n_estimators=50)

# Perform 5-fold cross validation
scores = cross_val_score(clf, X, y, cv=5)
print(f"Cross-Validation Scores: {scores}")
print(f"Average Accuracy: {scores.mean():.2f}")
```

---
## References
*   [Scikit-Learn: Model Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
*   [Towards Data Science: Precision vs Recall](https://towardsdatascience.com/precision-vs-recall-386cf9f89488)
