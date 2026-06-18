# Task P3-3: Autograd Deep Dive

**Goal:** Understand how PyTorch builds its computational graph dynamically.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. Manual Gradient Tracking
Let's verify PyTorch does math correctly.

1. Create a tensor `x = torch.tensor(2.0, requires_grad=True)`.
2. Perform the computation: `y = 3*x**2 + 4*x + 2`.
3. Call `y.backward()`.
4. Print `x.grad`. 
5. *Verify on paper:* What is $\frac{dy}{dx}$ when $x=2$? Does it match `x.grad`?

### 2. Writing a Custom Autograd Function
PyTorch knows how to differentiate `torch.sin` and `torch.exp`. What if you invent a new mathematical function? You have to teach PyTorch how to differentiate it.

Implement the `backward` method for a custom ReLU function:
```python
import torch

class MyReLU(torch.autograd.Function):
    
    @staticmethod
    def forward(ctx, input_tensor):
        # Save the input for use in the backward pass
        ctx.save_for_backward(input_tensor)
        # Apply ReLU
        return input_tensor.clamp(min=0)
    
    @staticmethod
    def backward(ctx, grad_output):
        # grad_output is the gradient passed back from the next layer (dL/dy)
        input_tensor, = ctx.saved_tensors
        
        # We need to return dL/dx = dL/dy * dy/dx
        # The derivative of ReLU (dy/dx) is 1 if x > 0, else 0.
        
        # Clone the incoming gradient
        grad_input = grad_output.clone()
        
        # TODO: Set grad_input to 0 wherever input_tensor <= 0
        
        return grad_input

# Testing it
x = torch.tensor([-2.0, 0.0, 3.0], requires_grad=True)
my_relu = MyReLU.apply # This is how you use a custom function
y = my_relu(x)

# Assume the loss gradient coming from above is [1.0, 1.0, 1.0]
y.backward(torch.tensor([1.0, 1.0, 1.0]))

print("Input:", x)
print("Output:", y)
print("Gradients:", x.grad) # Should be [0.0, 0.0, 1.0]
```
