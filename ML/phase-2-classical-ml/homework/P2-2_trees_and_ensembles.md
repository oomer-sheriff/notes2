# Task P2-2: Decision Trees & Ensembles

**Goal:** Understand how tree-based models make decisions and observe how Random Forests and XGBoost prevent overfitting.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. Setup
Load the built-in breast cancer dataset from sklearn (a binary classification problem). Split it into 80% train and 20% test sets.
```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split

data = load_breast_cancer()
X_train, X_test, y_train, y_test = train_test_split(data.data, data.target, test_size=0.2, random_state=42)
```

### 2. The Single Decision Tree
1. Import `DecisionTreeClassifier`.
2. Train the model *without* setting a `max_depth` (let it grow as deep as it wants).
3. Print the training accuracy and the testing accuracy.
   *Observe:* Training accuracy should be 100% (or very close), while testing accuracy is significantly lower. This is textbook overfitting.
4. Use `sklearn.tree.plot_tree(model)` to visualize the tree (it will look massive and messy).

### 3. The Random Forest
1. Import `RandomForestClassifier`.
2. Train it with `n_estimators=100`.
3. Print the training and testing accuracy.
   *Observe:* The testing accuracy should be noticeably higher than the single tree. The ensemble has generalized better.

### 4. XGBoost
1. Install xgboost if you haven't (`pip install xgboost`).
2. Import `xgboost as xgb`.
3. Train an `xgb.XGBClassifier`.
4. Compare its test accuracy to the Random Forest.

### 5. Feature Importance
Tree models inherently calculate which features were most useful for splitting the data.
1. Extract `rf_model.feature_importances_`.
2. Create a Pandas DataFrame matching the feature names (`data.feature_names`) to their importance scores.
3. Sort the dataframe and plot the top 5 most important features using a Seaborn barplot.
