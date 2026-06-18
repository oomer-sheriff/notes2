# Task P2-4: Full ML Pipeline on Kaggle

**Goal:** Build a complete, end-to-end ML pipeline on a real dataset and submit it to Kaggle.

### The Challenge
Go to Kaggle.com and choose either:
1. **Titanic: Machine Learning from Disaster** (Classification)
2. **House Prices: Advanced Regression Techniques** (Regression)

Download the `train.csv` and `test.csv` data to your `lab-files` folder.

### The Pipeline Requirements
Create a Jupyter notebook that executes the following steps in order:

1. **EDA (Exploratory Data Analysis)**
   - Plot distributions of target variable and key features.
   - Plot a correlation heatmap.
2. **Data Cleaning & Feature Engineering**
   - Handle missing values logically.
   - Encode categorical variables.
   - *Optional:* Create a new feature (e.g., "Family Size" on Titanic = SibSp + Parch).
3. **Preprocessing**
   - Split `train.csv` into training and validation sets.
   - Scale numerical features using `StandardScaler`.
4. **Modeling (Train at least 3 models)**
   - For Titanic: Logistic Regression, Random Forest, XGBoost.
   - For Housing: Ridge Regression, Random Forest, XGBoost.
5. **Evaluation & Tuning**
   - Use Cross-Validation to evaluate the models.
   - Pick the best one and use `GridSearchCV` to tune its hyperparameters (e.g., test different tree depths).
6. **Submission**
   - Train your tuned model on the *entire* `train.csv` dataset.
   - Generate predictions for `test.csv`.
   - Format the output as requested by Kaggle and upload your submission file!
