# Task P1-2: Visualization Portfolio

**Goal:** Practice creating the standard set of ML visualizations to understand your data before modeling.

Create a Jupyter Notebook in `homework/lab-files/` and implement the following.

### Prerequisites
You will need `matplotlib` and `seaborn`. (`pip install matplotlib seaborn`)

### The Task

We will use the classic Iris dataset, which is built into seaborn. It contains measurements of different species of iris flowers.

```python
import seaborn as sns
import matplotlib.pyplot as plt

# Load the dataset
df = sns.load_dataset('iris')
```

**Plot 1: Feature Distribution (Histograms)**
Create a grid of 4 histograms showing the distribution of `sepal_length`, `sepal_width`, `petal_length`, and `petal_width`.
*Hint: Look up `plt.subplots()`.*

**Plot 2: Box Plots for Outliers**
Create a box plot for `sepal_width`. Box plots are the standard way to visually identify outliers in a feature. 
*Hint: `sns.boxplot()`.*

**Plot 3: Scatter Plot with Classes**
Create a scatter plot plotting `sepal_length` against `petal_length`. Color the dots based on the `species` column.
This is exactly how you determine if a simple linear model can separate your classes, or if you need a complex non-linear neural network.
*Hint: `sns.scatterplot(..., hue='species')`.*

**Plot 4: The Correlation Heatmap**
Calculate the correlation matrix for the 4 numerical features and plot it using a heatmap.
*Question to answer:* Which two features are the most highly correlated? If two features have a correlation of 0.96, do you need to feed both of them into your model?

**Plot 5: The Pair Plot (The "Cheat Code")**
Seaborn has a built-in function that plots the relationship between *every single feature* against *every other feature* in one line of code.
Run `sns.pairplot(df, hue='species')`.
Observe how powerful this single line is for EDA (Exploratory Data Analysis).
