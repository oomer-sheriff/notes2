# Forward Pass, Backward Pass, and Backpropagation

How do neural networks actually learn? Through a two-step process executed thousands of times: the Forward Pass and the Backward Pass.

## 1. The Forward Pass

Data flows from the input layer, through the hidden layers, to the output layer to generate a prediction. We then use a **Loss Function** to measure how wrong that prediction is compared to the true label.

```python
import torch

# Let's use PyTorch to demonstrate this clearly.
# We create a simple weight and bias. requires_grad=True means PyTorch
# will track all operations on these tensors to calculate gradients later.
w = torch.tensor(0.5, requires_grad=True)
b = torch.tensor(0.1, requires_grad=True)

x = torch.tensor(2.0)    # Input
y_true = torch.tensor(3.0) # True label

# FORWARD PASS
y_pred = w * x + b       # 0.5 * 2.0 + 0.1 = 1.1

# CALCULATE LOSS (Mean Squared Error)
loss = (y_pred - y_true)**2 # (1.1 - 3.0)^2 = 3.61
print(f"Prediction: {y_pred.item():.2f}, Loss: {loss.item():.2f}")
```

## 2. The Backward Pass (Backpropagation)

We know the loss. Now we need to know: *How should we change $w$ and $b$ to make the loss smaller?*
We need the **gradients** ($\frac{\partial Loss}{\partial w}$ and $\frac{\partial Loss}{\partial b}$).

Backpropagation is just the **Chain Rule of Calculus** applied backward through the network's computational graph.

1.  How much did `y_pred` affect the `loss`?
2.  How much did `w` affect `y_pred`?
3.  Therefore, how much did `w` affect the `loss`?

```python
# BACKWARD PASS
# In PyTorch, this ONE LINE calculates every single gradient in the entire network 
# using the chain rule, no matter how deep the network is!
loss.backward()

# Let's look at the gradients
print(f"Gradient of w (dL/dw): {w.grad.item():.2f}")
print(f"Gradient of b (dL/db): {b.grad.item():.2f}")

# The gradient of w is negative (-7.6). 
# This means if we INCREASE w, the loss will DECREASE.
```

## 3. The Optimization Step

Now that we have the gradients (which point uphill), we take a small step downhill (opposite the gradient) to update the weights. This is **Gradient Descent**.

```python
learning_rate = 0.01

# We must wrap updates in torch.no_grad() because we don't want PyTorch 
# to track the *update* operation itself as part of the computational graph.
with torch.no_grad():
    w -= learning_rate * w.grad
    b -= learning_rate * b.grad
    
    # Crucial step: Clear the gradients after updating, otherwise they accumulate!
    w.grad.zero_()
    b.grad.zero_()

print(f"Updated w: {w.item():.4f}, Updated b: {b.item():.4f}")

# If we run the forward pass again, the loss will be lower!
y_pred_new = w * x + b
new_loss = (y_pred_new - y_true)**2
print(f"New Loss: {new_loss.item():.2f} (It went down!)")
```

---
## References
*   [3Blue1Brown: What is Backpropagation really doing?](https://www.youtube.com/watch?v=Ilg3gGewQ5U)
*   [Andrej Karpathy: Micrograd (Building Autograd from scratch)](https://www.youtube.com/watch?v=VMj-3S1tku0)
