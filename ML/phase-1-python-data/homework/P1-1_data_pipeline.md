# Task P1-1: ML Data Pipeline

**Goal:** Take a raw, messy dataset and prepare it so it is ready to be fed into a Machine Learning model.

Create a Jupyter Notebook in `homework/lab-files/` and implement the following pipeline.

### Prerequisites
You will need `pandas`, `numpy`, and `scikit-learn`. If you are using the local virtual environment, make sure they are installed: `pip install pandas numpy scikit-learn`.

### The Task

We will use the famous Titanic dataset (predicting who survived based on passenger data).
You can load it directly from the internet using Pandas:
```python
import pandas as pd
url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df = pd.read_csv(url)
```

**Step 1: Exploration**
1. Print the first 5 rows of the dataset.
2. Use `.info()` to identify which columns have missing values.
3. Identify which columns are numerical and which are categorical (text).

**Step 2: Cleaning (Imputation)**
1. The `Age` column has missing values. Fill the missing ages with the *median* age of all passengers.
2. The `Cabin` column is mostly missing. Drop the entire `Cabin` column.
3. The `Embarked` column has 2 missing values. Fill them with the *mode* (most frequent value).

**Step 3: Feature Engineering (Encoding)**
1. The `Sex` column is 'male'/'female'. Use Pandas `get_dummies` or scikit-learn's `LabelEncoder` to convert this to 1s and 0s.
2. One-hot encode the `Embarked` column.

**Step 4: Splitting**
1. Separate the features (`X`) from the target variable (`y`). In this case, `y` is the `Survived` column.
2. Drop columns that are obviously not useful for prediction: `PassengerId`, `Name`, `Ticket`.
3. Use `train_test_split` from `sklearn.model_selection` to split the data into 80% training data and 20% testing data.

**Step 5: Scaling**
1. Use `StandardScaler` from `sklearn.preprocessing` to scale the numerical features (`Age`, `Fare`).
2. **Crucial Rule:** You must `fit_transform` on the training data, but ONLY `transform` the testing data.

At the end of this notebook, you should have `X_train_scaled` and `X_test_scaled` arrays ready for Phase 2!
