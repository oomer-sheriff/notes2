# Probability & Statistics for Machine Learning

Machine learning models don't just output absolute truths; they output probabilities. A classification model doesn't say "This is a cat," it says "There is a 95% probability this is a cat."

## 1. Probability Distributions

A probability distribution describes how likely different outcomes are.
*   **Bernoulli/Categorical:** Used for discrete choices. E.g., coin flips (Binary Classification) or rolling a die (Multi-class Classification).
*   **Gaussian (Normal) Distribution:** The classic bell curve. It appears everywhere in nature due to the Central Limit Theorem. In ML, we often assume errors or noise follow a Gaussian distribution.

```python
import numpy as np

# Simulate 10 coin flips (Bernoulli/Categorical)
# 1 = Heads (60% chance), 0 = Tails (40% chance)
coin_flips = np.random.choice([0, 1], size=10, p=[0.4, 0.6])
print("Coin flips:", coin_flips)

# Sample from a Gaussian (Normal) Distribution
# Mean = 0, Standard Deviation = 1, sample size = 5
gaussian_samples = np.random.normal(loc=0.0, scale=1.0, size=5)
print("Gaussian samples:", np.round(gaussian_samples, 2))
```

## 2. Maximum Likelihood Estimation (MLE)

MLE is the core statistical engine behind how most models learn. 
*   **The Idea:** Given a set of observed data, MLE asks: *"What parameters (weights) of my model make this observed data the most likely to have occurred?"*
*   **Log-Likelihood:** Multiplying probabilities together often results in tiny numbers (underflow). To fix this, we take the log of the probabilities (turning products into sums).
*   **Connection to Loss:** Maximizing the Log-Likelihood is mathematically identical to minimizing the **Negative Log-Likelihood (NLL)**. This is why loss functions exist! Minimizing Mean Squared Error (MSE) is exactly the same as performing MLE assuming the data has Gaussian noise.

```python
# Negative Log-Likelihood (NLL) Example
# Imagine a model predicting if an image is a Dog (1) or Cat (0)
# The model outputs these probabilities that the image is a Dog:
predicted_probs = np.array([0.9, 0.8, 0.1, 0.3])
# The actual ground truth (1=Dog, 0=Cat)
actual_labels = np.array([1, 1, 0, 0])

# To find how "likely" this data is given our model, we multiply the probabilities of the correct events happening.
# For the first two, probability is just predicted_probs. For the last two, it's (1 - predicted_probs)
likelihoods = np.where(actual_labels == 1, predicted_probs, 1 - predicted_probs)
print("Likelihood of each event:", likelihoods)

# Total likelihood is the product (0.9 * 0.8 * 0.9 * 0.7 = 0.4536)
# But multiplying many small probabilities leads to underflow in computers.
# So we use Negative Log-Likelihood: -sum(log(likelihoods))
nll = -np.sum(np.log(likelihoods))
print("Negative Log-Likelihood (Loss):", round(nll, 4))
```

## 3. Information Theory: Entropy and Cross-Entropy

### Entropy ($H$)
Entropy measures the inherent uncertainty or randomness in a probability distribution.
*   A coin with two heads has 0 entropy (no uncertainty).
*   A fair coin has high entropy (maximum uncertainty).

### Cross-Entropy
Cross-Entropy measures the "distance" or difference between two probability distributions:
1.  The true distribution (the actual label, usually a 100% probability on the correct class).
2.  The predicted distribution (the model's output, e.g., 80% class A, 20% class B).

*   **As a Loss Function:** This is the default loss function for classification in PyTorch (`nn.CrossEntropyLoss`). By minimizing the cross-entropy between the predictions and the true labels, you are forcing the model's predicted distribution to match the true distribution.

```python
# Cross-Entropy Example (Multi-class)
# Suppose we have 3 classes: [Dog, Cat, Bird]
# True label: It's a Cat. So the true distribution is [0, 1, 0]
true_distribution = np.array([0.0, 1.0, 0.0])

# Model's predicted probabilities
predicted_distribution = np.array([0.1, 0.8, 0.1])

# Cross-Entropy formula: -sum( true * log(predicted) )
# Notice that because the true distribution is mostly 0s, 
# this just becomes -1 * log(predicted_probability_of_the_correct_class)
cross_entropy_loss = -np.sum(true_distribution * np.log(predicted_distribution))

print(f"Cross-Entropy Loss: {cross_entropy_loss:.4f}") 
# If prediction was 0.99 for Cat, loss would be near 0.
# If prediction was 0.01 for Cat, loss would be very high (4.6).
```

---
## References
*   [Towards AI: Probability and Statistics for Machine Learning](https://towardsai.net/p/machine-learning/probability-and-statistics-for-machine-learning)
*   [Machine Learning Mastery: A Gentle Introduction to Maximum Likelihood Estimation](https://machinelearningmastery.com/what-is-maximum-likelihood-estimation-in-machine-learning/)
*   [Machine Learning Mastery: A Gentle Introduction to Cross-Entropy](https://machinelearningmastery.com/cross-entropy-for-machine-learning/)
