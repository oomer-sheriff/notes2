# Task P3-1: Neural Network from Scratch (NumPy Only)

**Goal:** Truly understand Backpropagation by implementing a 2-layer Neural Network from scratch using only NumPy. If you can do this, you understand deep learning better than 90% of practitioners.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. The Challenge

Implement the `NeuralNetwork` class below. You must complete the `backward` method.

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
        # Subtract max for numerical stability
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / exp_x.sum(axis=1, keepdims=True)
    
    def forward(self, X):
        self.z1 = X @ self.W1 + self.b1
        self.a1 = self.relu(self.z1)
        self.z2 = self.a1 @ self.W2 + self.b2
        self.a2 = self.softmax(self.z2)
        return self.a2
    
    def backward(self, X, y_true, lr=0.01):
        """
        X: shape (batch_size, input_size)
        y_true: shape (batch_size, output_size) - ONE-HOT ENCODED labels
        """
        m = X.shape[0] # batch size
        
        # --- THE HARD PART: Implement Backpropagation ---
        
        # 1. Gradient of the Loss w.r.t the output (z2)
        # Because we use Softmax + Cross Entropy, this simplifies beautifully:
        dz2 = self.a2 - y_true 
        
        # 2. Gradients for Layer 2 weights and biases
        # dW2 = ? (Hint: use self.a1.T)
        # db2 = ? (Hint: use np.sum on dz2)
        
        # 3. Gradient w.r.t hidden layer activations (a1)
        # da1 = ? (Hint: use W2.T)
        
        # 4. Gradient w.r.t hidden layer pre-activations (z1)
        # dz1 = da1 * self.relu_derivative(self.z1)
        
        # 5. Gradients for Layer 1 weights and biases
        # dW1 = ?
        # db1 = ?
        
        # 6. Update weights and biases
        # self.W2 -= lr * dW2
        # ... update the rest ...
        pass
```

### 2. Testing on Digits

Test your network on a small, real-world dataset (the 8x8 digits dataset).

```python
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder

# Load data
digits = load_digits()
X = digits.data  # shape (1797, 64)
y = digits.target

# Scale X to be between 0 and 1
X = X / 16.0 

# One-hot encode y (required for our custom backward pass)
encoder = OneHotEncoder(sparse_output=False)
y_onehot = encoder.fit_transform(y.reshape(-1, 1))

X_train, X_test, y_train, y_test = train_test_split(X, y_onehot, test_size=0.2)

# Initialize network: 64 inputs -> 32 hidden -> 10 outputs
nn = NeuralNetwork(64, 32, 10)

# Training Loop
epochs = 1000
for i in range(epochs):
    nn.forward(X_train)
    nn.backward(X_train, y_train, lr=0.1)
    
    if i % 100 == 0:
        preds = np.argmax(nn.forward(X_test), axis=1)
        true_labels = np.argmax(y_test, axis=1)
        acc = np.mean(preds == true_labels)
        print(f"Epoch {i}, Test Accuracy: {acc*100:.1f}%")
```

**Target:** You should achieve >90% test accuracy if your backprop is implemented correctly!
