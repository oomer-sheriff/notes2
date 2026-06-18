# 🧠 Machine Learning Mastery — Complete Learning Plan

> **Philosophy:** Understand what's under the hood. You already build AI apps — now learn why they work.  
> **Approach:** "Intuition → Math → Code" — understand the concept, see the math, then implement it.  
> **Benchmark:** Can you implement it from scratch in a blank notebook? Can you explain it to a junior dev? That's mastery.  
> **Framework:** PyTorch on Google Colab (free GPU/TPU)

---

## 🏁 Prerequisites Checklist

You already have most of these. Quick sanity check:

| Skill | Why It Matters | Your Level |
|-------|---------------|------------|
| Python (3.10+) | All ML is Python | ✅ Strong (FastAPI dev) |
| Docker | Containerize models | ✅ Strong |
| Git/GitHub | Version code + models | ✅ Strong |
| Linear algebra basics | Everything in ML is matrix ops | ⚠️ To learn/refresh |
| Calculus basics | Backprop = chain rule | ⚠️ To learn/refresh |
| Probability & stats | Every model is a probability machine | ⚠️ To learn/refresh |

**You're already ahead of 90% of ML learners. Your bottleneck is the math + DL theory, not the tooling.**

---

## 📐 Environment Setup

### Google Colab (Primary — Free GPU)
```
1. Go to https://colab.research.google.com
2. New Notebook → Runtime → Change runtime type → T4 GPU
3. PyTorch comes pre-installed. Verify:
```
```python
import torch
print(torch.__version__)
print(torch.cuda.is_available())  # Should be True on GPU runtime
print(torch.cuda.get_device_name(0))  # Should show Tesla T4
```

### Local Setup (Optional — for larger experiments)
```bash
# Create a conda environment
conda create -n ml python=3.11 -y
conda activate ml

# Install PyTorch with CUDA (check https://pytorch.org for your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Essential libraries
pip install numpy pandas matplotlib seaborn scikit-learn jupyter
pip install transformers datasets accelerate  # Hugging Face ecosystem
pip install wandb  # Experiment tracking
```

### Verify Your Setup
```python
import torch
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt

print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"NumPy: {np.__version__}")
print(f"scikit-learn: {sklearn.__version__}")
```

---

# PHASE 0 — Math for ML (Weeks 1-3)
**Goal:** Build the mathematical intuition needed for ML. Not abstract math — applied, visual, "why does this matter for ML" math.

## 🧠 Concepts to Learn

### Linear Algebra (The Language of ML)
- **Vectors & matrices** — data is matrices, weights are matrices, everything is matrix multiplication
- **Matrix operations** — transpose, inverse, dot product, element-wise ops
- **Eigenvalues & eigenvectors** — PCA, covariance matrices, understanding data directions
- **Singular Value Decomposition (SVD)** — dimensionality reduction, recommendation systems
- **Norms** — L1 (Manhattan), L2 (Euclidean), Frobenius — used in regularization

### Calculus (The Engine of Learning)
- **Derivatives** — rate of change, slope of the loss function
- **Partial derivatives** — how each weight affects the loss independently
- **Chain rule** — THE core of backpropagation, this is how neural nets learn
- **Gradients** — vector of partial derivatives, points in steepest ascent direction
- **Jacobians & Hessians** — advanced optimization, second-order methods

### Probability & Statistics (The Framework of Uncertainty)
- **Probability distributions** — Gaussian, Bernoulli, Categorical, Uniform
- **Bayes' theorem** — posterior ∝ likelihood × prior, the foundation of probabilistic ML
- **Maximum Likelihood Estimation (MLE)** — finding parameters that best explain data
- **Expectation, variance, covariance** — summarizing distributions
- **Information theory basics** — entropy, cross-entropy (your loss function!), KL divergence

### Optimization (How Models Learn)
- **Gradient descent** — walk downhill on the loss surface
- **Learning rate** — step size, too big = overshoot, too small = slow
- **Convexity** — convex = one minimum (easy), non-convex = many (hard, real world)
- **Stochastic gradient descent (SGD)** — use mini-batches, not the full dataset
- **Loss functions** — MSE (regression), cross-entropy (classification), why each one

## 📚 Resources
- 📺 **3Blue1Brown — Essence of Linear Algebra** (YouTube, 16 videos, free) — the BEST visual intro
- 📺 **3Blue1Brown — Essence of Calculus** (YouTube, 12 videos, free) — equally excellent
- 📺 **StatQuest — Probability & Statistics** (YouTube, free) — intuitive, no-nonsense
- 📖 **Mathematics for Machine Learning** — Deisenroth et al. (free PDF: mml-book.github.io) — comprehensive textbook
- 📖 **Khan Academy** (khanacademy.org) — fill gaps in specific topics as needed
- 📺 **3Blue1Brown — Neural Networks** series (YouTube) — preview of how math connects to DL

## 🏠 Homework — Phase 0

### Task P0-1: Linear Algebra Essentials (3 hrs)
```python
import numpy as np

# 1. Create vectors and matrices, practice operations
a = np.array([1, 2, 3])
B = np.array([[1, 2], [3, 4], [5, 6]])

# 2. Implement dot product from scratch (no np.dot)
def dot_product(v1, v2):
    return sum(x * y for x, y in zip(v1, v2))

# 3. Implement matrix multiplication from scratch (no np.matmul)
def matmul(A, B):
    # Your code here
    pass

# 4. Compute eigenvalues of a covariance matrix
data = np.random.randn(100, 3)
cov = np.cov(data.T)
eigenvalues, eigenvectors = np.linalg.eig(cov)
# Q: What do the eigenvalues tell you about the data?
```
**Done when:** You can explain what matrix multiplication does geometrically (linear transformation).

### Task P0-2: Calculus for Backprop (2 hrs)
```python
# 1. Implement the derivative of common functions
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def sigmoid_derivative(x):
    s = sigmoid(x)
    return s * (1 - s)  # Why does this work? Prove it on paper.

# 2. Implement the chain rule manually
# Given: f(x) = sigmoid(3x² + 2x)
# Compute df/dx using the chain rule
# Verify with numerical differentiation:
def numerical_derivative(f, x, h=1e-7):
    return (f(x + h) - f(x - h)) / (2 * h)

# 3. Compute the gradient of MSE loss
# L = (1/n) * Σ(y_pred - y_true)²
# Derive ∂L/∂y_pred on paper, then implement it
```
**Done when:** You can trace the chain rule through a 3-layer computation graph on paper.

### Task P0-3: Probability & Information Theory (2 hrs)
```python
# 1. Implement cross-entropy loss from scratch
def cross_entropy(y_true, y_pred):
    """Binary cross-entropy. y_pred are probabilities."""
    epsilon = 1e-15  # prevent log(0)
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))

# 2. Implement KL divergence
def kl_divergence(p, q):
    """KL(P || Q) — how different Q is from P"""
    pass

# 3. Generate samples from different distributions, plot them
# Gaussian, Uniform, Bernoulli — understand their shapes
# Q: Why is the Gaussian so common in ML?
```
**Done when:** You can explain why cross-entropy is used instead of MSE for classification.

### Task P0-4: Gradient Descent from Scratch (3 hrs)
```python
# Implement gradient descent to find the minimum of f(x) = x² + 3x + 2
def gradient_descent(f, df, x0, lr=0.1, steps=100):
    x = x0
    history = [x]
    for _ in range(steps):
        x = x - lr * df(x)
        history.append(x)
    return x, history

# 1. Run with different learning rates: 0.01, 0.1, 0.5, 1.5
# 2. Plot the convergence — what happens when lr is too high?
# 3. Extend to 2D: minimize f(x,y) = x² + y² (gradient is [2x, 2y])
# 4. Visualize the path on a contour plot
```
**Done when:** You can explain why learning rate matters and what "loss landscape" means.

---

# PHASE 1 — Data Toolkit Refresher (Week 4)
**Goal:** Quick refresher on NumPy/Pandas/Matplotlib for ML-specific patterns. You know Python — this is about ML data workflows.

## 🧠 Concepts to Learn

### NumPy for ML
- Broadcasting rules (critical for vectorized ops)
- Reshaping, stacking, splitting tensors
- Random number generation for reproducibility (`np.random.seed`)
- Vectorized operations vs loops (10-100x speed difference)

### Pandas for ML
- Loading and exploring datasets (CSV, JSON, Parquet)
- Handling missing data, outliers
- Feature engineering: encoding categoricals, scaling numerics
- Train/test splitting strategies

### Visualization for ML
- Distribution plots (histograms, KDE)
- Correlation heatmaps
- Learning curves, loss curves
- Confusion matrices, ROC curves

## 📚 Resources
- 📖 **Python Data Science Handbook** — Jake VanderPlas (free online: jakevdp.github.io)
- 📺 **Corey Schafer — Pandas tutorials** (YouTube, free)
- 📖 NumPy docs — broadcasting rules: numpy.org/doc/stable/user/basics.broadcasting.html
- 🔧 Google Colab — your primary notebook environment

## 🏠 Homework — Phase 1

### Task P1-1: ML Data Pipeline (2 hrs)
```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

# 1. Load a real dataset (Titanic or Housing Prices from Kaggle)
# 2. Explore: df.describe(), df.info(), df.isnull().sum()
# 3. Handle missing values (strategy: mean, median, mode, or drop)
# 4. Encode categoricals (OneHotEncoder, LabelEncoder)
# 5. Scale numeric features (StandardScaler, MinMaxScaler)
# 6. Split: train/val/test (70/15/15)
# 7. Verify no data leakage (fit scaler on train only!)
```
**Done when:** You have a clean, split dataset ready for modeling.

### Task P1-2: Visualization Portfolio (1 hr)
Create a single notebook with all these plots using any dataset:
1. Distribution of each feature (histograms)
2. Correlation heatmap
3. Scatter plot with color-coded classes
4. Box plots for outlier detection
5. Pair plot for feature relationships

---

# PHASE 2 — Classical Machine Learning (Weeks 5-8)
**Goal:** Understand the core ML algorithms that everything else builds on. Know when to use what and why.

## 🧠 Concepts to Learn

### The ML Framework
- Supervised vs unsupervised vs self-supervised
- Training, validation, test sets — why three splits
- Bias-variance tradeoff — underfitting vs overfitting
- No Free Lunch theorem — no single best algorithm

### Supervised Learning — Regression
- **Linear Regression** — the simplest model, closed-form vs gradient descent
- **Polynomial Regression** — capturing non-linear relationships
- **Regularization** — Ridge (L2), Lasso (L1), ElasticNet — why and when

### Supervised Learning — Classification
- **Logistic Regression** — despite the name, it's a classifier (sigmoid + cross-entropy)
- **Decision Trees** — interpretable, greedy splitting, entropy/Gini impurity
- **Random Forests** — ensemble of trees, bagging, feature importance
- **Gradient Boosting** — XGBoost, LightGBM, sequential error correction
- **SVMs** — maximum margin classifier, kernel trick for non-linear boundaries
- **KNN** — lazy learning, distance metrics, curse of dimensionality

### Unsupervised Learning
- **K-Means** — centroid-based clustering, elbow method, k-means++
- **DBSCAN** — density-based, handles non-spherical clusters
- **PCA** — dimensionality reduction, variance explained, scree plot
- **t-SNE / UMAP** — non-linear embedding for visualization

### Model Evaluation (CRITICAL)
- **Regression:** MSE, RMSE, MAE, R²
- **Classification:** Accuracy, Precision, Recall, F1-Score
- **ROC-AUC** — when to use and what the curve actually shows
- **Confusion matrix** — TP, FP, TN, FN — the foundation of all metrics
- **Cross-validation** — k-fold, stratified k-fold, leave-one-out
- **Hyperparameter tuning** — GridSearch, RandomSearch, Optuna/Bayesian

## 📚 Resources
- 📺 **Andrew Ng — Machine Learning Specialization** (Coursera, free to audit) — best structured intro
- 📺 **StatQuest — Josh Starmer** (YouTube, free) — intuitive algorithm explanations, seriously watch these
- 📖 **Hands-On Machine Learning** — Aurélien Géron (3rd ed.) — Part 1
- 📖 **The Hundred-Page Machine Learning Book** — Andriy Burkov — fast overview
- 📖 scikit-learn documentation (excellent tutorials section)
- 🔧 Kaggle — Titanic (classification), Housing Prices (regression)

## 🏠 Homework — Phase 2

### Task P2-1: Linear & Logistic Regression from Scratch (3 hrs)
```python
import numpy as np

class LinearRegression:
    def __init__(self, lr=0.01, epochs=1000):
        self.lr = lr
        self.epochs = epochs
    
    def fit(self, X, y):
        self.w = np.zeros(X.shape[1])
        self.b = 0
        for _ in range(self.epochs):
            y_pred = X @ self.w + self.b
            # Compute gradients
            dw = (2 / len(y)) * X.T @ (y_pred - y)
            db = (2 / len(y)) * np.sum(y_pred - y)
            # Update weights
            self.w -= self.lr * dw
            self.b -= self.lr * db
    
    def predict(self, X):
        return X @ self.w + self.b

# 1. Test on sklearn's make_regression dataset
# 2. Compare your results with sklearn's LinearRegression
# 3. Now implement LogisticRegression (add sigmoid, use cross-entropy loss)
# 4. Plot the decision boundary on a 2D classification problem
```
**Done when:** Your from-scratch model matches sklearn within 1% accuracy.

### Task P2-2: Decision Trees & Ensembles (3 hrs)
```python
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
import xgboost as xgb
import matplotlib.pyplot as plt

# 1. Load the Iris dataset
# 2. Train a Decision Tree — visualize it with plot_tree()
# 3. Observe overfitting: train accuracy 100%, test accuracy lower
# 4. Train Random Forest — compare test accuracy
# 5. Train XGBoost — compare again
# 6. Extract feature importance from all 3 — do they agree?

# CHALLENGE: Implement a simple Decision Tree from scratch
# (just the splitting logic with Gini impurity)
```

### Task P2-3: Unsupervised Learning Lab (2 hrs)
```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# 1. Generate synthetic clusters: sklearn.datasets.make_blobs
# 2. Run K-Means with k=2,3,4,5 — plot the elbow curve
# 3. Run DBSCAN — does it find the same clusters?
# 4. Run PCA on a high-dimensional dataset (e.g., MNIST)
#    - How many components capture 95% of variance?
# 5. Visualize MNIST with t-SNE — colored by digit
#    - Q: Why can't you use t-SNE for actual dimensionality reduction?
```

### Task P2-4: Full ML Pipeline on Kaggle (4 hrs)
Pick ONE Kaggle competition (Titanic or Housing Prices) and build a complete pipeline:
1. EDA (exploratory data analysis)
2. Feature engineering
3. Train 3+ models (Logistic Regression, Random Forest, XGBoost)
4. Hyperparameter tuning with GridSearchCV
5. Compare results with a proper evaluation metric
6. Submit to Kaggle (even a late submission — just go through the flow)

**Done when:** You can explain why one model beat the others on YOUR specific dataset.

### Task P2-5: Bias-Variance Tradeoff Experiment (1 hr)
```python
# 1. Generate noisy data: y = sin(x) + noise
# 2. Fit polynomial regression with degrees 1, 3, 5, 10, 20
# 3. Plot all fits on the same chart
# 4. Compute train error and test error for each degree
# 5. Plot the classic bias-variance tradeoff curve
# Q: At what degree does overfitting start?
```

---

# PHASE 3 — Neural Network Fundamentals (Weeks 9-11)
**Goal:** Understand neural networks from the ground up. Build them from scratch before using PyTorch.

## 🧠 Concepts to Learn

### The Neuron
- Biological inspiration (loose analogy, don't take it too far)
- Perceptron: weighted sum + bias + activation = output
- Universal Approximation Theorem — a wide enough network can approximate any function

### Multi-Layer Perceptrons (MLPs)
- Input → Hidden → Output layers
- Width (neurons per layer) vs Depth (number of layers)
- Why deep > wide (compositional features)

### Forward Pass
- Matrix multiplication through layers: `Z = W @ X + b`
- Activation functions applied element-wise: `A = activation(Z)`
- Final output: softmax for classification, linear for regression

### Backpropagation (THE KEY CONCEPT)
```
Loss → ∂L/∂output → ∂L/∂W_last → ... → ∂L/∂W_first
          (chain rule applied repeatedly)
```
- Computational graph: represent the forward pass as a DAG
- Backward pass: traverse the graph in reverse, accumulating gradients
- Why it's efficient: each gradient computed once, reused downstream

### Activation Functions
| Function | Formula | Pros | Cons |
|----------|---------|------|------|
| Sigmoid | 1/(1+e⁻ˣ) | Output 0-1, interpretable | Vanishing gradients, slow |
| Tanh | (eˣ-e⁻ˣ)/(eˣ+e⁻ˣ) | Zero-centered | Still vanishing gradients |
| ReLU | max(0, x) | Fast, no vanishing grad | Dead neurons (output stuck at 0) |
| Leaky ReLU | max(0.01x, x) | Fixes dead ReLU | Leaky slope is arbitrary |
| GELU | x·Φ(x) | Smooth, used in Transformers | Slightly slower |
| Swish | x·σ(x) | Smooth, used in EfficientNet | Slightly slower |

### Optimizers
- **SGD** — basic, noisy, needs momentum to work well
- **SGD + Momentum** — accelerates SGD, dampens oscillations
- **Adam** — adaptive learning rate per parameter, the default choice
- **AdamW** — Adam with proper weight decay, used in Transformers
- Learning rate schedulers: warmup, cosine annealing, step decay

### Regularization
- **Dropout** — randomly zero out neurons during training (prevents co-adaptation)
- **Batch Normalization** — normalize activations, speeds up training
- **Layer Normalization** — normalize per-sample (used in Transformers instead of BatchNorm)
- **Weight Decay** — L2 regularization on weights
- **Early Stopping** — stop when validation loss stops improving
- **Data Augmentation** — artificially increase dataset size

## 📚 Resources
- 📺 **Andrej Karpathy — Neural Networks: Zero to Hero** (YouTube, free) — THE series to follow
- 📺 **3Blue1Brown — Neural Networks** (YouTube, free) — visual intuition for backprop
- 📖 **Deep Learning with Python** — François Chollet (2nd ed.) — intuitive DL
- 📖 **Dive into Deep Learning** — d2l.ai (free, interactive, PyTorch) — code-first textbook
- 📺 **MIT 6.S191** — Introduction to Deep Learning (YouTube, free) — fast-paced, modern

## 🏠 Homework — Phase 3

### Task P3-1: Neural Network from Scratch — NumPy Only (4 hrs) 🔥
```python
import numpy as np

class NeuralNetwork:
    """2-layer neural network from scratch. No PyTorch, no autograd."""
    
    def __init__(self, input_size, hidden_size, output_size):
        # Xavier initialization
        self.W1 = np.random.randn(input_size, hidden_size) * np.sqrt(2 / input_size)
        self.b1 = np.zeros(hidden_size)
        self.W2 = np.random.randn(hidden_size, output_size) * np.sqrt(2 / hidden_size)
        self.b2 = np.zeros(output_size)
    
    def relu(self, x):
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        return (x > 0).astype(float)
    
    def softmax(self, x):
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / exp_x.sum(axis=1, keepdims=True)
    
    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
    
    def backward(self, X, y, output, lr=0.01):
        m = X.shape[0]
        # TODO: Implement backpropagation
        # 1. Compute dL/dz2 (softmax + cross-entropy shortcut)
        # 2. Compute dL/dW2, dL/db2
        # 3. Compute dL/da1, then dL/dz1 (chain rule through ReLU)
        # 4. Compute dL/dW1, dL/db1
        # 5. Update all weights and biases
        pass

# Test on MNIST (sklearn.datasets.load_digits for a small version)
# Target: >90% accuracy on the test set
```
**Done when:** You can trace the gradient flow through each layer on paper AND your code works.

### Task P3-2: PyTorch Fundamentals (3 hrs)
```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

# 1. Tensors: create, reshape, slice, GPU transfer
x = torch.randn(3, 4)
x_gpu = x.cuda()  # Move to GPU
print(x.shape, x.dtype, x.device)

# 2. Autograd: automatic differentiation
x = torch.tensor(3.0, requires_grad=True)
y = x**2 + 2*x + 1
y.backward()
print(x.grad)  # dy/dx = 2x + 2 = 8.0

# 3. Build the same network using nn.Module
class MLP(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, num_classes)
        )
    
    def forward(self, x):
        return self.net(x)

# 4. Write the training loop
model = MLP(784, 128, 10)
optimizer = optim.Adam(model.parameters(), lr=1e-3)
criterion = nn.CrossEntropyLoss()

for epoch in range(10):
    for batch_X, batch_y in train_loader:
        optimizer.zero_grad()
        output = model(batch_X)
        loss = criterion(output, batch_y)
        loss.backward()
        optimizer.step()

# 5. Compare results with your NumPy implementation
```
**Done when:** You understand what `loss.backward()` does under the hood because you implemented it manually.

### Task P3-3: Autograd Deep Dive (2 hrs)
```python
# Trace the computational graph that PyTorch builds
# 1. Create a simple computation
x = torch.tensor(2.0, requires_grad=True)
y = torch.tensor(3.0, requires_grad=True)
z = x * y + x**2
z.backward()
# Verify x.grad and y.grad match your hand calculation

# 2. Implement a custom autograd Function
class MyReLU(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input):
        ctx.save_for_backward(input)
        return input.clamp(min=0)
    
    @staticmethod
    def backward(ctx, grad_output):
        input, = ctx.saved_tensors
        grad_input = grad_output.clone()
        grad_input[input < 0] = 0
        return grad_input

# 3. Use torchviz to visualize the computation graph
```

### Task P3-4: Optimizer Showdown (2 hrs)
```python
# Train the SAME network on the SAME data with different optimizers:
# 1. SGD (lr=0.01)
# 2. SGD + Momentum (lr=0.01, momentum=0.9)
# 3. Adam (lr=0.001)
# 4. AdamW (lr=0.001, weight_decay=0.01)
#
# Plot all 4 loss curves on the same chart.
# Q: Which converges fastest? Which gives lowest final loss?
# Q: Why is Adam not always the best choice?
```

---

# PHASE 4 — CNNs & Computer Vision (Weeks 12-14)
**Goal:** Understand how convolutions work, why they're powerful for spatial data, and the evolution of CNN architectures.

## 🧠 Concepts to Learn

### Why Convolutions?
- Fully connected layers don't understand spatial structure
- Convolutions exploit **local patterns** and **translation invariance**
- Parameter sharing: same filter applied everywhere → way fewer parameters

### Convolution Operations
```
Input (6×6)   *   Filter (3×3)   =   Output (4×4)
┌─────────┐       ┌─────┐           ┌───────┐
│ . . . . │       │ w w │           │ . . . │
│ . . . . │   *   │ w w │    →      │ . . . │
│ . . . . │       │ w w │           │ . . . │
│ . . . . │       └─────┘           └───────┘
└─────────┘
```
- **Stride** — how far the filter moves each step
- **Padding** — add zeros around the input to control output size
- **Feature maps** — each filter detects one type of pattern (edges, textures, etc.)
- **Pooling** — downsample: MaxPool (take max), AvgPool (take average)
- **Output size formula:** `(W - F + 2P) / S + 1`

### The CNN Architecture Evolution (Know This Timeline)
| Year | Architecture | Key Innovation | Params |
|------|-------------|----------------|--------|
| 1998 | LeNet-5 | First practical CNN (handwritten digits) | 60K |
| 2012 | AlexNet | ReLU, Dropout, GPU training — started the DL revolution | 62M |
| 2014 | VGG | Deep, simple: just stack 3×3 convolutions | 138M |
| 2014 | GoogLeNet/Inception | Multiple filter sizes in parallel (Inception module) | 5M |
| 2015 | ResNet | Skip connections — made >100 layers possible | 25M |
| 2019 | EfficientNet | Neural architecture search, compound scaling | 5-66M |
| 2020 | ViT | Ditched convolutions entirely — used Transformers | 86M |

### Transfer Learning
- Use a pre-trained model (trained on ImageNet: 14M images, 1000 classes)
- **Feature extraction:** freeze all layers, train only the final classifier
- **Fine-tuning:** unfreeze some layers, train with very small learning rate
- When to use what: small dataset → feature extraction, large dataset → fine-tuning

### Object Detection & Segmentation
- **Object Detection:** find objects + bounding boxes (YOLO, SSD, Faster R-CNN)
- **Image Segmentation:** classify every pixel (U-Net, Mask R-CNN)
- **Metric: mAP** (mean Average Precision) — IoU thresholds

## 📚 Resources
- 📺 **Stanford CS231n — CNNs for Visual Recognition** (YouTube, free) — the gold standard
- 📺 **3Blue1Brown — Convolutions in image processing** (YouTube, free)
- 📖 **Dive into Deep Learning** — Ch. 7-8 (d2l.ai, free)
- 📖 **Deep Learning** — Goodfellow et al., Ch. 9 (deeplearningbook.org, free)
- 📺 **Yannic Kilcher — ResNet paper explanation** (YouTube, free)

## 🏠 Homework — Phase 4

### Task P4-1: Convolution from Scratch (2 hrs)
```python
import numpy as np

def conv2d(image, kernel, stride=1, padding=0):
    """Implement 2D convolution from scratch."""
    if padding > 0:
        image = np.pad(image, padding, mode='constant')
    
    h, w = image.shape
    kh, kw = kernel.shape
    out_h = (h - kh) // stride + 1
    out_w = (w - kw) // stride + 1
    output = np.zeros((out_h, out_w))
    
    for i in range(out_h):
        for j in range(out_w):
            region = image[i*stride:i*stride+kh, j*stride:j*stride+kw]
            output[i, j] = np.sum(region * kernel)
    
    return output

# 1. Apply edge detection kernels to a real image
sobel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
sobel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

# 2. Visualize what different kernels "see"
# 3. Q: Why does the Sobel filter detect edges?
```

### Task P4-2: Build a CNN for CIFAR-10 (3 hrs)
```python
import torch
import torch.nn as nn
import torchvision
import torchvision.transforms as transforms

# Load CIFAR-10
transform = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(32, padding=4),
    transforms.ToTensor(),
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
])

trainset = torchvision.datasets.CIFAR10(root='./data', train=True,
                                         download=True, transform=transform)

# Build a CNN from scratch
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(32, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d(1),
        )
        self.classifier = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

# Target: >85% test accuracy
# Track: training loss, validation loss, validation accuracy per epoch
# Plot all curves
```

### Task P4-3: Transfer Learning with ResNet (2 hrs)
```python
from torchvision.models import resnet18, ResNet18_Weights

# 1. Load pretrained ResNet18
model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)

# 2. Freeze all layers
for param in model.parameters():
    param.requires_grad = False

# 3. Replace the last layer for your task
model.fc = nn.Linear(512, 10)  # 10 classes for CIFAR-10

# 4. Train ONLY the last layer — compare accuracy with your CNN
# 5. Now unfreeze the last 2 ResBlocks and fine-tune with lr=1e-4
# 6. Compare all 3 results: from-scratch CNN, frozen ResNet, fine-tuned ResNet
```

### Task P4-4: Visualize What CNNs See (2 hrs)
```python
# 1. Extract feature maps from each Conv layer of your trained CNN
# 2. Visualize them — what does layer 1 detect? Layer 2? Layer 3?
# 3. Use GradCAM to see what parts of the image the model focuses on
# 4. Find images your model gets WRONG — can you see why?
```

---

# PHASE 5 — Sequence Models & RNNs (Weeks 15-16)
**Goal:** Understand sequential data processing, the vanishing gradient problem, and how LSTMs solved it. This is the precursor to Transformers.

## 🧠 Concepts to Learn

### Why Sequences are Different
- Images have spatial structure → CNNs
- Text, audio, time series have **temporal/sequential** structure → need memory
- Variable-length inputs → can't use fixed-size MLPs

### Recurrent Neural Networks (RNNs)
```
x₁ → [RNN Cell] → h₁ → [RNN Cell] → h₂ → [RNN Cell] → h₃
         ↑                    ↑                    ↑
        h₀                  h₁                   h₂
```
- Hidden state: carries information from previous timesteps
- Same weights at every timestep (parameter sharing)
- **Vanishing gradient problem:** gradients shrink exponentially through long sequences
- **Exploding gradients:** gradients grow exponentially (fix: gradient clipping)

### LSTMs & GRUs
- **LSTM** — Long Short-Term Memory: solves vanishing gradients with gates
  - Forget gate: what to throw away from cell state
  - Input gate: what new info to store
  - Output gate: what to output from cell state
  - Cell state: the "conveyor belt" of information
- **GRU** — Gated Recurrent Unit: simplified LSTM (2 gates instead of 3)
  - Reset gate + Update gate
  - Often performs as well as LSTM with fewer parameters

### Sequence-to-Sequence (Seq2Seq)
- Encoder: processes input sequence → context vector
- Decoder: generates output sequence from context vector
- Problem: bottleneck! Entire input compressed into one vector
- Solution: **Attention** (coming in Phase 6!)

## 📚 Resources
- 📺 **Andrew Ng — Sequence Models** (Coursera DL Specialization, Course 5, free to audit)
- 📖 **Chris Olah — Understanding LSTMs** (colah.github.io, free) — the BEST LSTM explainer ever written
- 📖 **Dive into Deep Learning** — Ch. 9-10 (d2l.ai, free)
- 📺 **StatQuest — RNNs and LSTMs** (YouTube, free)

## 🏠 Homework — Phase 5

### Task P5-1: RNN from Scratch (3 hrs)
```python
import torch
import torch.nn as nn

# 1. Implement a character-level RNN that generates text
class CharRNN(nn.Module):
    def __init__(self, vocab_size, hidden_size, num_layers=1):
        super().__init__()
        self.hidden_size = hidden_size
        self.embedding = nn.Embedding(vocab_size, hidden_size)
        self.rnn = nn.RNN(hidden_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, vocab_size)
    
    def forward(self, x, hidden):
        x = self.embedding(x)
        output, hidden = self.rnn(x, hidden)
        output = self.fc(output)
        return output, hidden

# 2. Train on a text file (Shakespeare, your code, anything)
# 3. Generate text — it'll be garbage at first, then slowly improve
# 4. Replace nn.RNN with nn.LSTM — does it generate better text? Why?
```
**Done when:** You understand why LSTMs generate better text than vanilla RNNs on long sequences.

### Task P5-2: Sentiment Analysis with LSTM (2 hrs)
```python
# 1. Load the IMDB dataset (torchtext or Hugging Face datasets)
# 2. Build an LSTM-based classifier
# 3. Compare: RNN vs LSTM vs GRU (same architecture, different cell)
# 4. Plot validation accuracy vs sequence length — where does the RNN fail?
```

### Task P5-3: The Bottleneck Experiment (1 hr)
```python
# Build a seq2seq model for simple string reversal: "hello" → "olleh"
# 1. Train with short strings (length 5-10) — works great
# 2. Test with longer strings (length 20-30) — starts failing
# 3. Q: Why does performance degrade with length?
# 4. Q: What would fix this? (Hint: the answer is Phase 6)
```

---

# PHASE 6 — Transformers & Attention (Weeks 17-20) ⭐
**Goal:** Master the architecture that powers modern AI. Understand every component of a Transformer.

## 🧠 Concepts to Learn

### The Attention Mechanism
**The Core Idea:** Instead of compressing the entire input into one vector, let the model LOOK BACK at all input positions and decide what's relevant.

```
Query:  "What am I looking for?"
Key:    "What do I contain?"
Value:  "What do I actually give you?"

Attention(Q, K, V) = softmax(Q·Kᵀ / √d_k) · V
```

- **Scaled Dot-Product Attention:** dot product of Q and K, scaled, softmaxed, applied to V
- **Multi-Head Attention:** run attention in parallel with different learned projections
  - Each "head" can attend to different aspects (syntax, semantics, position)
- **Self-Attention:** Q, K, V all come from the same input (every token attends to every other token)
- **Cross-Attention:** Q from one source, K/V from another (decoder attending to encoder)

### The Transformer Architecture
```
┌──────────────────────────────────────────────────┐
│                  TRANSFORMER                      │
│                                                   │
│  ┌─────────────────┐    ┌──────────────────────┐ │
│  │    ENCODER       │    │      DECODER          │ │
│  │                  │    │                       │ │
│  │ ┌──────────────┐│    │ ┌───────────────────┐│ │
│  │ │ Multi-Head   ││    │ │ Masked Multi-Head ││ │
│  │ │ Self-Attn    ││    │ │ Self-Attention     ││ │
│  │ ├──────────────┤│    │ ├───────────────────┤│ │
│  │ │ Add & Norm   ││    │ │ Add & Norm        ││ │
│  │ ├──────────────┤│    │ ├───────────────────┤│ │
│  │ │ Feed Forward ││    │ │ Cross-Attention   ││ │
│  │ ├──────────────┤│    │ │ (from Encoder)    ││ │
│  │ │ Add & Norm   ││    │ ├───────────────────┤│ │
│  │ └──────────────┘│    │ │ Add & Norm        ││ │
│  │      × N        │    │ ├───────────────────┤│ │
│  └─────────────────┘    │ │ Feed Forward      ││ │
│                         │ ├───────────────────┤│ │
│                         │ │ Add & Norm        ││ │
│                         │ └───────────────────┘│ │
│                         │       × N            │ │
│                         └──────────────────────┘ │
└──────────────────────────────────────────────────┘
```

### Key Components
- **Positional Encoding** — Transformers have no sense of order, inject position info
  - Sinusoidal (original paper) or Learned embeddings (modern)
  - RoPE (Rotary Position Embeddings) — used in LLaMA, GPT-NeoX
- **Layer Normalization** — normalize per-sample (not per-batch like BatchNorm)
- **Residual Connections** — skip connections around each sub-layer
- **Feed-Forward Network** — 2-layer MLP applied independently to each position

### Encoder Models (BERT family)
- Bidirectional: see full context in both directions
- Pre-training: Masked Language Modeling (predict [MASK] tokens)
- Use case: classification, NER, sentence embeddings
- Models: BERT, RoBERTa, DeBERTa

### Decoder Models (GPT family)
- Autoregressive: generate one token at a time, left-to-right
- Causal masking: can only attend to previous tokens
- Pre-training: next-token prediction
- Use case: text generation, code generation, chatbots
- Models: GPT-2/3/4, LLaMA, Mistral, Claude

### Vision Transformers (ViT)
- Split image into patches → treat each patch as a "token"
- Same Transformer architecture — works surprisingly well
- CLIP: align image and text embeddings in the same space

## 📚 Resources
- 📺 **Andrej Karpathy — "Let's build GPT from scratch, in code, spelled out"** (YouTube, free) — THE must-watch
- 📺 **3Blue1Brown — "Attention in Transformers, Visually Explained"** (YouTube, free)
- 📺 **3Blue1Brown — "How might LLMs store facts"** (YouTube, free)
- 📖 **Jay Alammar — "The Illustrated Transformer"** (blog, free) — best visual breakdown
- 📖 **Jay Alammar — "The Illustrated GPT-2"** (blog, free)
- 📄 **"Attention Is All You Need"** — Vaswani et al. (2017) — the foundational paper, READ THIS
- 📺 **Stanford CS25 — Transformers United** (YouTube, free) — lectures by field experts
- 📖 **Hugging Face NLP Course** (huggingface.co/course, free) — practical Transformers
- 📖 **Build a Large Language Model (From Scratch)** — Sebastian Raschka — excellent book

## 🏠 Homework — Phase 6

### Task P6-1: Self-Attention from Scratch (3 hrs)
```python
import torch
import torch.nn.functional as F

def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Q, K, V: (batch, seq_len, d_k)
    Returns: attention output and attention weights
    """
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1)) / (d_k ** 0.5)
    
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))
    
    weights = F.softmax(scores, dim=-1)
    output = torch.matmul(weights, V)
    return output, weights

# 1. Implement the above, test with random tensors
# 2. Visualize the attention weights as a heatmap
# 3. Add causal masking (lower triangular) — verify future tokens are blocked
# 4. Q: What happens if you remove the √d_k scaling? Try it.
```

### Task P6-2: Multi-Head Attention (2 hrs)
```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_k = d_model // n_heads
        self.n_heads = n_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
    
    def forward(self, Q, K, V, mask=None):
        batch_size = Q.size(0)
        
        # 1. Linear projections
        Q = self.W_q(Q).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(K).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(V).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        # 2. Apply attention
        attn_output, attn_weights = scaled_dot_product_attention(Q, K, V, mask)
        
        # 3. Concatenate heads and project
        attn_output = attn_output.transpose(1, 2).contiguous().view(batch_size, -1, self.n_heads * self.d_k)
        return self.W_o(attn_output)

# Test it — verify shapes are correct
```

### Task P6-3: Build a Mini-GPT (Karpathy's nanoGPT) (5 hrs) 🔥🔥
```python
# Follow Karpathy's video and build a character-level GPT:
# 1. Tokenize Shakespeare text at character level
# 2. Build the full Transformer decoder:
#    - Token embedding + positional embedding
#    - N × (Masked Self-Attention → LayerNorm → FFN → LayerNorm)
#    - Final linear layer → logits over vocab
# 3. Train it on Shakespeare (~1M characters)
# 4. Generate text — it should produce semi-coherent Shakespeare
# 5. Experiment: vary n_layers, n_heads, d_model — what improves quality?
```
**Done when:** Your model generates text that looks vaguely Shakespearean and you understand every line of code.

### Task P6-4: Hugging Face Transformers (2 hrs)
```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import Trainer, TrainingArguments
from datasets import load_dataset

# 1. Fine-tune a pre-trained BERT on a classification task
dataset = load_dataset("imdb")
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained(
    "bert-base-uncased", num_labels=2
)

# 2. Tokenize, train, evaluate using the Trainer API
# 3. Compare with your Phase 5 LSTM — how much better is BERT?
# 4. Try a smaller model (DistilBERT) — accuracy vs speed tradeoff?
```

### Task P6-5: Vision Transformer (2 hrs)
```python
# 1. Implement patch embedding from scratch
class PatchEmbedding(nn.Module):
    def __init__(self, img_size, patch_size, in_channels, embed_dim):
        super().__init__()
        self.num_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_channels, embed_dim, 
                              kernel_size=patch_size, stride=patch_size)
    
    def forward(self, x):
        x = self.proj(x)  # (B, embed_dim, H', W')
        x = x.flatten(2).transpose(1, 2)  # (B, num_patches, embed_dim)
        return x

# 2. Add [CLS] token and positional embeddings
# 3. Feed through standard Transformer encoder
# 4. Compare ViT vs CNN on CIFAR-10 — which is better with limited data? Why?
```

---

# PHASE 7 — Generative Models (Weeks 21-24) ⭐
**Goal:** Understand the full spectrum of generative models — from GANs to the cutting-edge diffusion models powering modern image generation.

## 🧠 Concepts to Learn

### Generative vs Discriminative Models
- **Discriminative:** model P(y|x) — "given this image, what class is it?"
- **Generative:** model P(x) or P(x|y) — "generate a new image"
- Generative is harder — must understand the full data distribution

### Autoencoders & VAEs
- **Autoencoder:** compress input → latent code → reconstruct input
  - Encoder: data → bottleneck (smaller dimension)
  - Decoder: bottleneck → reconstruction
  - Use: denoising, anomaly detection, feature learning
- **Variational Autoencoder (VAE):** probabilistic version
  - Latent space is a distribution (mean + variance), not a point
  - Reparameterization trick: z = μ + σ·ε (makes it differentiable)
  - Loss = reconstruction loss + KL divergence (regularizes latent space)
  - Smooth latent space → can interpolate between samples

### GANs (Generative Adversarial Networks)
```
Random Noise z → [Generator] → Fake Image
                                    ↓
Real Image → ──────────────→ [Discriminator] → Real or Fake?
                                    ↓
              (Adversarial Loss feeds back to both)
```
- **Generator:** learns to produce realistic samples from noise
- **Discriminator:** learns to distinguish real from fake
- **Training:** min-max game — G tries to fool D, D tries to catch G
- **Challenges:** mode collapse, training instability, no good stopping criterion
- **Key architectures:** DCGAN, StyleGAN, StyleGAN2/3, ProGAN

### Diffusion Models (The Current SOTA for Image Generation)
```
Forward process (add noise):
x₀ → x₁ → x₂ → ... → x_T (pure noise)

Reverse process (learned denoising):
x_T → x_{T-1} → ... → x₁ → x₀ (clean image)
```
- **Forward process:** gradually add Gaussian noise over T timesteps
- **Reverse process:** train a neural network to predict and remove the noise
- **The model learns:** given noisy image xₜ and timestep t, predict the noise ε
- **Loss function:** simple MSE between predicted noise and actual noise
- **Sampling:** start from pure noise, iteratively denoise
- **Why better than GANs:** more stable training, better mode coverage, no adversarial games

### Diffusion Advanced Concepts
- **DDPM** — Denoising Diffusion Probabilistic Models (the foundational paper)
- **DDIM** — faster sampling (skip timesteps)
- **Classifier-Free Guidance** — trade off diversity for quality using a guidance scale
- **Latent Diffusion (Stable Diffusion)** — run diffusion in a compressed latent space (way faster)
  - Encode image → latent → add noise/denoise in latent → decode back to image
  - Uses a pretrained VAE for encoding/decoding
- **U-Net** — the backbone architecture (encoder-decoder with skip connections)
- **Diffusion Transformers (DiT)** — replacing U-Net with Transformers (used in DALL-E 3, Sora)
- **Flow Matching / Rectified Flow** — newer, simpler alternative to DDPM

### Conditioning & Control
- **Text-to-Image:** condition on text embeddings (CLIP text encoder)
- **ControlNet:** condition on spatial controls (edges, pose, depth)
- **Image-to-Image:** start from a noisy version of an existing image
- **Inpainting:** generate only masked regions

## 📚 Resources
- 📄 **"Denoising Diffusion Probabilistic Models"** — Ho et al. (2020) — foundational paper
- 📄 **"High-Resolution Image Synthesis with Latent Diffusion Models"** — Rombach et al. (2022) — Stable Diffusion paper
- 📖 **Lilian Weng — "What are Diffusion Models?"** (lilianweng.github.io, free) — best blog post on the topic
- 📺 **Hugging Face — Diffusion Models Course** (free) — hands-on with `diffusers` library
- 📺 **Yannic Kilcher — DDPM paper explanation** (YouTube, free)
- 📺 **Computerphile — "How AI Image Generators Work"** (YouTube, free)
- 📄 **"Generative Adversarial Networks"** — Goodfellow et al. (2014) — the GAN paper
- 📖 **Deep Learning** — Goodfellow et al., Ch. 20 (deeplearningbook.org, free)

## 🏠 Homework — Phase 7

### Task P7-1: Autoencoder & VAE (3 hrs)
```python
import torch
import torch.nn as nn

# 1. Build a standard autoencoder for MNIST
class Autoencoder(nn.Module):
    def __init__(self, latent_dim=32):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(784, 256), nn.ReLU(),
            nn.Linear(256, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 256), nn.ReLU(),
            nn.Linear(256, 784), nn.Sigmoid()
        )
    
    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

# 2. Train it, visualize original vs reconstructed digits
# 3. Now build a VAE: add mu, logvar, reparameterization trick, KL loss
# 4. Sample from the VAE's latent space — generate new digits
# 5. Interpolate between two digits in latent space — visualize the morph
```

### Task P7-2: Build a GAN (3 hrs)
```python
# 1. Implement DCGAN for MNIST/Fashion-MNIST
class Generator(nn.Module):
    def __init__(self, latent_dim=100):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 784),
            nn.Tanh()
        )
    
    def forward(self, z):
        return self.net(z).view(-1, 1, 28, 28)

class Discriminator(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),
            nn.Linear(784, 512),
            nn.LeakyReLU(0.2),
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Linear(256, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.net(x)

# 2. Train with the adversarial loss — alternate G and D updates
# 3. Generate a grid of fake digits every 5 epochs — watch quality improve
# 4. Intentionally cause mode collapse — how? What does it look like?
```

### Task P7-3: Diffusion Model from Scratch (5 hrs) 🔥🔥
```python
# Build DDPM from scratch on MNIST
# This is the boss fight of generative models

# 1. Forward process: q(x_t | x_0) = N(√ᾱ_t · x_0, (1-ᾱ_t) · I)
def add_noise(x_0, t, betas):
    """Add noise to x_0 according to the schedule at timestep t"""
    alphas = 1 - betas
    alpha_bar = torch.cumprod(alphas, dim=0)
    sqrt_alpha_bar = torch.sqrt(alpha_bar[t])
    sqrt_one_minus_alpha_bar = torch.sqrt(1 - alpha_bar[t])
    noise = torch.randn_like(x_0)
    x_t = sqrt_alpha_bar * x_0 + sqrt_one_minus_alpha_bar * noise
    return x_t, noise

# 2. Noise prediction network (simple U-Net or even an MLP for MNIST)
# 3. Training: sample t ~ Uniform(0, T), add noise, predict noise, MSE loss
# 4. Sampling: start from x_T ~ N(0, I), iteratively denoise
# 5. Generate a grid of digits — compare quality with your GAN

# Q: Why is diffusion training more stable than GAN training?
```

### Task P7-4: Stable Diffusion with Hugging Face (2 hrs)
```python
from diffusers import StableDiffusionPipeline
import torch

# 1. Load a pretrained Stable Diffusion model
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

# 2. Generate images with different prompts
image = pipe("a photo of a cat astronaut on the moon").images[0]

# 3. Experiment with guidance_scale (1.0 vs 7.5 vs 20.0) — what changes?
# 4. Experiment with num_inference_steps (10 vs 50 vs 100) — quality vs speed
# 5. Use img2img pipeline — start from an existing image
# 6. Look at the pipeline components: text encoder, U-Net, VAE, scheduler
#    Q: How does the text prompt actually affect the generated image?
```

---

# PHASE 8 — NLP & LLM Theory (Weeks 25-27)
**Goal:** You already USE RAG, agents, and chatbots. Now understand the ML theory behind them.

## 🧠 Concepts to Learn

### Tokenization (How Text Becomes Numbers)
- **Character-level:** simple but long sequences
- **Word-level:** vocabulary explosion, can't handle new words
- **Subword:** the sweet spot — BPE, WordPiece, SentencePiece, Unigram
  - BPE (Byte-Pair Encoding): merge most common pairs iteratively
  - "unhappiness" → "un" + "happiness" or "un" + "happ" + "iness"
- Vocabulary size tradeoff: too small = long sequences, too large = sparse embeddings

### Embeddings (How Tokens Become Vectors)
- **Word2Vec:** Skip-gram, CBOW — words with similar context → similar vectors
- **GloVe:** Global co-occurrence statistics → embeddings
- **Contextual embeddings:** same word, different vector depending on context (BERT, GPT)
- You use these in your vector DBs — now understand how they're made

### Language Modeling
- **Next-token prediction:** P(token_n | token_1, ..., token_{n-1})
- **Perplexity:** exponentiated average cross-entropy — lower = better
- **Scaling laws:** performance improves predictably with more data, compute, parameters
- **Emergent abilities:** capabilities that appear only at certain model scales

### The Theory Behind RAG (You Use It — Now Understand It)
- **Why RAG works:** LLMs have fixed knowledge cutoffs, RAG adds dynamic knowledge
- **Embedding models:** how bi-encoders create dense vectors (contrastive learning)
- **Retrieval:** nearest neighbor search in embedding space (FAISS, HNSW)
- **Chunking strategies:** why chunk size matters for retrieval quality
- **Reranking:** cross-encoders for higher-quality relevance scoring
- **Lost in the middle:** LLMs attend more to beginning/end of context

### Fine-Tuning (You Deploy Models — Now Understand Training Them)
- **Full fine-tuning:** update all parameters — expensive, risks catastrophic forgetting
- **LoRA:** Low-Rank Adaptation — add small trainable matrices, freeze original weights
- **QLoRA:** LoRA + 4-bit quantization — fine-tune 65B models on a single GPU
- **PEFT:** Parameter-Efficient Fine-Tuning — LoRA, adapters, prefix tuning
- **Instruction Tuning:** train on (instruction, response) pairs → model follows instructions
- **RLHF:** Reinforcement Learning from Human Feedback
  1. Train a reward model on human preference pairs
  2. Use PPO to optimize the LLM against the reward model
- **DPO:** Direct Preference Optimization — simpler alternative to RLHF, no reward model needed

## 📚 Resources
- 📺 **Andrej Karpathy — "State of GPT"** (YouTube, free) — how GPTs are trained in practice
- 📺 **Andrej Karpathy — "Let's build the GPT Tokenizer"** (YouTube, free)
- 📖 **Hugging Face NLP Course** (huggingface.co/course, free)
- 📖 **Build a Large Language Model (From Scratch)** — Sebastian Raschka
- 📄 **"Training language models to follow instructions with human feedback"** — Ouyang et al. (InstructGPT)
- 📄 **"LoRA: Low-Rank Adaptation of Large Language Models"** — Hu et al.
- 📄 **"Direct Preference Optimization"** — Rafailov et al.

## 🏠 Homework — Phase 8

### Task P8-1: Build a BPE Tokenizer from Scratch (3 hrs)
```python
# Implement Byte-Pair Encoding from scratch
# Follow Karpathy's tokenizer video

def train_bpe(text, vocab_size):
    """Train a BPE tokenizer on a text corpus."""
    # 1. Start with character-level vocabulary
    # 2. Count all adjacent pairs
    # 3. Merge the most frequent pair → add to vocabulary
    # 4. Repeat until vocab_size reached
    pass

def encode(text, merges):
    """Encode text using learned BPE merges."""
    pass

def decode(tokens, vocab):
    """Decode tokens back to text."""
    pass

# Test: train on a small corpus, verify encode/decode roundtrip
# Compare with tiktoken (OpenAI's tokenizer) on the same text
```

### Task P8-2: Embedding Space Exploration (2 hrs)
```python
from sentence_transformers import SentenceTransformer

# 1. Load a sentence embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Embed a list of sentences with varying semantic similarity
sentences = [
    "The cat sat on the mat",
    "A kitten rested on the rug",
    "The stock market crashed today",
    "Financial markets experienced a downturn",
    "I love programming in Python",
]

# 3. Compute cosine similarity matrix — visualize as heatmap
# 4. Q: Why are semantically similar sentences closer in embedding space?
# 5. Q: How does this relate to your vector DB work?

# 6. CHALLENGE: Implement cosine similarity from scratch
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
```

### Task P8-3: Fine-Tune a Small LLM with LoRA (3 hrs)
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model

# 1. Load a small model (GPT-2 or TinyLlama)
model = AutoModelForCausalLM.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# 2. Add LoRA adapters
lora_config = LoraConfig(
    r=8,               # rank — lower = fewer params, faster
    lora_alpha=32,      # scaling factor
    target_modules=["c_attn"],  # which layers to adapt
    lora_dropout=0.1,
)
model = get_peft_model(model, lora_config)
model.print_trainable_parameters()  # Should be ~0.1% of total

# 3. Fine-tune on a small dataset (your own text, a specific domain)
# 4. Compare generation before vs after fine-tuning
# 5. Q: What does the "r" parameter control? What happens with r=1 vs r=64?
```

### Task P8-4: RAG Theory Deep Dive (2 hrs)
```python
# You've built RAG systems. Now understand the ML behind retrieval:
# 1. Train a simple bi-encoder from scratch:
#    - Two BERT models (or shared weights)
#    - Contrastive loss: similar pairs close, dissimilar pairs far
# 2. Compare retrieval quality: TF-IDF vs BM25 vs dense embeddings
# 3. Implement a simple reranker using a cross-encoder
# 4. Write a 1-page explanation of why dense retrieval sometimes
#    fails vs BM25 and when to use hybrid search
```

---

# PHASE 9 — MLOps (Weeks 28-29)
**Goal:** You already know Docker, FastAPI, and K8s. Focus on ML-specific operations you DON'T know yet.

## 🧠 Concepts to Learn

### Experiment Tracking
- **Weights & Biases (W&B):** log metrics, hyperparameters, model artifacts, compare runs
- **MLflow:** open-source alternative, model registry, deployment
- Why it matters: reproducibility, debugging, team collaboration

### Model Optimization for Deployment
- **Quantization:** FP32 → FP16 → INT8 → INT4 (smaller, faster, slight quality loss)
- **ONNX:** universal model format, run PyTorch models anywhere
- **TorchScript:** compile PyTorch models for production
- **vLLM / TensorRT:** optimized inference engines for LLMs

### Data Management
- **DVC (Data Version Control):** Git for datasets and models
- **Feature stores:** centralized feature management
- **Data drift detection:** when production data diverges from training data

### Model Monitoring (Production)
- **Data drift:** input distribution changes
- **Concept drift:** relationship between features and target changes
- **A/B testing:** compare model versions in production
- You know Prometheus/Grafana from K8s — same tools, ML-specific metrics

## 📚 Resources
- 📺 **Made With ML** — Goku Mohandas (madewithml.com, free) — best MLOps resource
- 📖 **Designing Machine Learning Systems** — Chip Huyen — production ML bible
- 🔧 Weights & Biases documentation (excellent tutorials)
- 🔧 MLflow documentation

## 🏠 Homework — Phase 9

### Task P9-1: Experiment Tracking (2 hrs)
```python
import wandb

# 1. Sign up for W&B (free tier)
# 2. Take your Phase 4 CNN training loop
# 3. Add W&B logging:
wandb.init(project="cifar10-cnn", config={
    "learning_rate": 0.001,
    "epochs": 20,
    "batch_size": 64,
    "architecture": "SimpleCNN"
})

for epoch in range(20):
    # ... training ...
    wandb.log({"train_loss": loss, "val_accuracy": acc, "epoch": epoch})

# 4. Run 5 experiments with different hyperparameters
# 5. Use W&B's comparison dashboard to pick the best run
```

### Task P9-2: Model Serving with Your Stack (3 hrs)
```python
# You know FastAPI. Now serve an ML model with it.
from fastapi import FastAPI, UploadFile
import torch
from torchvision import transforms
from PIL import Image

app = FastAPI()

# Load your trained model
model = torch.load("cifar10_model.pt")
model.eval()

@app.post("/predict")
async def predict(file: UploadFile):
    image = Image.open(file.file)
    tensor = transforms.Compose([
        transforms.Resize(32),
        transforms.ToTensor(),
        transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))
    ])(image).unsqueeze(0)
    
    with torch.no_grad():
        output = model(tensor)
        prediction = output.argmax(1).item()
    
    return {"class": prediction, "confidence": output.softmax(1).max().item()}

# 1. Dockerize it (you know Docker — this is quick)
# 2. Add batch prediction endpoint
# 3. Add model versioning (load model by version parameter)
# 4. CHALLENGE: Deploy to your K8s cluster with a Deployment + Service
```

### Task P9-3: Quantization & Optimization (2 hrs)
```python
# 1. Take your trained model and quantize it:
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)
# 2. Compare: file size, inference speed, accuracy
# 3. Export to ONNX:
torch.onnx.export(model, dummy_input, "model.onnx")
# 4. Run inference with ONNX Runtime — compare speed with PyTorch
```

---

# PHASE 10 — Advanced Topics (Weeks 30-32)
**Goal:** Explore the frontier. Pick what interests you most.

## 🧠 Concepts to Learn

### Reinforcement Learning
- **MDP:** states, actions, rewards, transitions, policy
- **Q-Learning:** learn action-value function, epsilon-greedy exploration
- **Deep Q-Network (DQN):** Q-learning with neural networks (Atari games)
- **Policy Gradients:** directly optimize the policy (REINFORCE)
- **PPO:** Proximal Policy Optimization — stable policy gradient, used in RLHF
- **RLHF connection:** PPO is how LLMs are aligned with human preferences

### Graph Neural Networks
- **Why graphs:** social networks, molecules, knowledge graphs can't be flattened
- **Message Passing:** nodes aggregate information from neighbors
- **GCN:** Graph Convolutional Networks
- **GAT:** Graph Attention Networks — attention on graph edges
- Use cases: drug discovery, recommendation systems, fraud detection

### Multimodal Models
- **CLIP:** align images and text in the same embedding space
- **Flamingo / LLaVA:** visual language models — see and talk about images
- **Whisper:** speech-to-text Transformer
- **How they work:** combine modality-specific encoders with a shared decoder/LLM

### Efficient Training & Scaling
- **Mixed precision (FP16/BF16):** 2x memory savings, faster matmul
- **Gradient checkpointing:** trade compute for memory (recompute activations)
- **DeepSpeed / FSDP:** distributed training across multiple GPUs
- **Mixture of Experts (MoE):** sparse models — only activate a subset of parameters
- **State Space Models (Mamba):** linear-time alternative to Transformers for sequences

## 📚 Resources
- 📺 **David Silver — RL Course** (DeepMind/UCL, YouTube, free) — the RL bible
- 📺 **Stanford CS224W — Machine Learning with Graphs** (YouTube, free)
- 📄 Key papers: CLIP, PPO, Mamba, Mixture of Experts
- 📖 **Spinning Up in Deep RL** — OpenAI (spinningup.openai.com, free)

## 🏠 Homework — Phase 10

### Task P10-1: Q-Learning Agent (3 hrs)
```python
import gymnasium as gym

# 1. Implement Q-Learning for CartPole or FrozenLake
# 2. Watch the agent go from random to solving the task
# 3. Implement DQN — add a neural network as the Q-function
# 4. Q: How does PPO differ from DQN? Write a 1-page comparison.
```

### Task P10-2: CLIP Exploration (2 hrs)
```python
from transformers import CLIPProcessor, CLIPModel

# 1. Load CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# 2. Zero-shot image classification (no training needed!)
# 3. Text-to-image search: find the best matching image for a text query
# 4. Q: How does CLIP enable text-to-image generation in Stable Diffusion?
```

### Task P10-3: Mixed Precision Training (1 hr)
```python
from torch.amp import autocast, GradScaler

# 1. Take your Phase 4 CNN
# 2. Add mixed precision training:
scaler = GradScaler()
for batch in train_loader:
    optimizer.zero_grad()
    with autocast(device_type='cuda'):
        output = model(batch_x)
        loss = criterion(output, batch_y)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()

# 3. Compare: training speed, memory usage, final accuracy
# 4. Q: Why does FP16 not hurt accuracy significantly?
```

---

# PHASE 11 — Capstone Projects (Weeks 33+)
**See [10_Projects.md](./10_Projects.md) for full project specs.**

---

## 📊 Weekly Cadence (Template)

```
Monday    — Watch/Read: New concepts + take notes (1.5 hrs)
Tuesday   — Code Lab: Implement the concept from scratch (2 hrs)
Wednesday — Deep Dive: Read the paper or textbook chapter (1 hr)
Thursday  — Lab: Build something more complex (2 hrs)
Friday    — Homework: Complete the phase project (2 hrs)
Weekend   — Review + explore (optional, light reading, papers)
```

---

## 🔗 Master Resource List

### Primary Learning
| Resource | Type | Cost | Best For |
|----------|------|------|----------|
| [Andrej Karpathy — Zero to Hero](https://www.youtube.com/@AndrejKarpathy) | YouTube | Free | Build neural nets from scratch |
| [Andrew Ng — ML Specialization](https://www.coursera.org/specializations/machine-learning-introduction) | Coursera | Free (audit) | Best structured ML intro |
| [Andrew Ng — DL Specialization](https://www.coursera.org/specializations/deep-learning) | Coursera | Free (audit) | DL fundamentals |
| [fast.ai](https://course.fast.ai/) | Course | Free | Practical, code-first DL |
| [Stanford CS231n](https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv) | YouTube | Free | CNNs & vision |
| [Stanford CS224n](https://www.youtube.com/playlist?list=PLoROMvodv4rMFqRtEuo6SGjY4XbRIVRd4) | YouTube | Free | NLP with deep learning |
| [Stanford CS25](https://www.youtube.com/@StanfordCS25) | YouTube | Free | Transformers United |
| [MIT 6.S191](https://www.youtube.com/playlist?list=PLtBw6njQRU-rwp5__7C0oIVt26ZgjG9NI) | YouTube | Free | Modern DL overview |
| [3Blue1Brown](https://www.youtube.com/@3blue1brown) | YouTube | Free | Math + DL visual intuition |
| [StatQuest](https://www.youtube.com/@statquest) | YouTube | Free | ML algorithm intuition |
| [Hugging Face Course](https://huggingface.co/course) | Course | Free | Transformers ecosystem |
| [Hugging Face Diffusion Course](https://huggingface.co/learn/diffusion-course) | Course | Free | Diffusion models hands-on |

### Books
| Book | Author | Best For |
|------|--------|----------|
| *Hands-On Machine Learning* (3rd ed.) | Géron | Practical ML + scikit-learn |
| *Deep Learning with Python* (2nd ed.) | Chollet | Intuitive DL |
| *Dive into Deep Learning* | Zhang et al. | Interactive, code-first (d2l.ai, free) |
| *Build an LLM from Scratch* | Raschka | LLMs from first principles |
| *Deep Learning* | Goodfellow et al. | Theory bible (deeplearningbook.org, free) |
| *Understanding Deep Learning* | Prince | Modern theory (2023, free) |
| *Mathematics for Machine Learning* | Deisenroth et al. | Math foundations (mml-book.github.io, free) |
| *Designing ML Systems* | Huyen | MLOps & production |

### Blogs & Websites
| Blog | Best For |
|------|----------|
| [Jay Alammar](https://jalammar.github.io/) | Illustrated explanations (Transformers, BERT, GPT) |
| [Lilian Weng](https://lilianweng.github.io/) | In-depth technical posts (diffusion, attention, RL) |
| [Chris Olah](https://colah.github.io/) | Visual intuition (LSTMs, neural net representations) |
| [Distill.pub](https://distill.pub/) | Interactive ML research articles |
| [Papers With Code](https://paperswithcode.com/) | Papers + implementations + benchmarks |
| [Made With ML](https://madewithml.com/) | MLOps, end-to-end ML |

### Tools
- **Framework:** PyTorch (primary), Hugging Face Transformers, scikit-learn
- **Notebooks:** Google Colab (free GPU), Jupyter
- **Experiment Tracking:** Weights & Biases, MLflow
- **Deployment:** FastAPI (you know this!), Docker (you know this!), K8s (you know this!)
- **Datasets:** Kaggle, Hugging Face Datasets, UCI ML Repository
- **Papers:** arXiv, Papers With Code, Semantic Scholar
