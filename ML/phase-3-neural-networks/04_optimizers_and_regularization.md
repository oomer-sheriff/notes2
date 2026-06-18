# Optimizers and Regularization

## 1. Optimizers

Gradient Descent tells us the direction to step. The **Optimizer** defines *how* we take that step.

*   **SGD (Stochastic Gradient Descent):** Very noisy. Takes steps based purely on the current batch's gradient.
*   **SGD + Momentum:** Accumulates a "velocity" vector. If it keeps stepping in the same direction, it speeds up. Helps push through flat regions of the loss landscape.
*   **Adam (Adaptive Moment Estimation):** The industry default. It maintains a separate learning rate for *every single weight*. It combines Momentum with RMSProp (scaling learning rates based on past gradient sizes).

```python
import torch
import torch.nn as nn
import torch.optim as optim

model = nn.Linear(10, 2) # Dummy model

# Basic SGD
opt_sgd = optim.SGD(model.parameters(), lr=0.01)

# SGD with Momentum
opt_momentum = optim.SGD(model.parameters(), lr=0.01, momentum=0.9)

# Adam (Usually use a smaller learning rate, 1e-3 or 1e-4)
opt_adam = optim.Adam(model.parameters(), lr=0.001)

# Usage in training loop:
# opt_adam.zero_grad()
# loss.backward()
# opt_adam.step()
```

## 2. Regularization (Preventing Overfitting)

Neural networks are so powerful they can easily memorize the training data. Regularization techniques force the network to learn generalized patterns instead.

### Dropout
During training, Dropout randomly turns off a percentage of neurons in a layer. This prevents neurons from co-adapting (relying too heavily on a specific neighboring neuron).

### Batch Normalization
Normalizes the activations of a layer across the batch so they have a mean of 0 and standard dev of 1. It stabilizes the gradients, allowing for much higher learning rates and faster training.

```python
class RegularizedMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(100, 50),
            
            # BatchNorm usually goes BEFORE the activation function
            nn.BatchNorm1d(50), 
            nn.ReLU(),
            
            # Dropout drops 20% of neurons during training
            nn.Dropout(p=0.2),  
            
            nn.Linear(50, 10)
        )
        
    def forward(self, x):
        return self.net(x)

model = RegularizedMLP()
# CRITICAL: You must tell PyTorch if you are training or evaluating!
# Dropout behaves differently (it turns OFF during evaluation).
model.train() 
# ... train loop ...
model.eval()
# ... evaluation ...
```

### Weight Decay (L2 Regularization)
Penalizes the model for having large weights. Instead of adding it to the loss function manually, modern optimizers handle it directly.

```python
# AdamW is Adam with mathematically correct Weight Decay.
# Used heavily in modern architectures like Transformers.
opt_adamw = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
```

---
## References
*   [Ruder.io: An overview of gradient descent optimization algorithms](https://ruder.io/optimizing-gradient-descent/)
*   [PyTorch: Optimizers](https://pytorch.org/docs/stable/optim.html)
