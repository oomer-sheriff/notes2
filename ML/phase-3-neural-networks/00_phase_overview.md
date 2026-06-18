# Phase 3: Neural Networks Fundamentals

> **Goal:** Build the intuition for Deep Learning and learn PyTorch.
> **Duration:** 3 weeks

## The Anatomy of a Neural Network

1. **Neurons (Nodes):** Compute a weighted sum of inputs plus a bias: $z = w^T x + b$.
2. **Activation Functions:** Add non-linearity. Without this, a deep network is just one giant linear regression.
   - *ReLU:* $\max(0, x)$. The default choice. Fast and fixes vanishing gradients.
   - *Sigmoid/Softmax:* Used for outputting probabilities.
3. **Layers:** Stacked neurons. Input -> Hidden Layers -> Output.

## How They Learn: Backpropagation
1. **Forward Pass:** Input flows through the network, generating a prediction.
2. **Compute Loss:** Measure how wrong the prediction is (e.g., Cross-Entropy, MSE).
3. **Backward Pass (Autograd):** Calculate the gradient of the loss with respect to every weight using the chain rule.
4. **Optimizer Step:** Update weights in the opposite direction of the gradient to minimize loss (Gradient Descent/Adam).

## PyTorch Workflow
PyTorch is built on two core concepts:
1. **Tensors:** Like NumPy arrays, but can run on GPUs.
2. **Autograd:** Automatic differentiation engine that computes gradients for you.

## Homework
- Complete `homework/P3-1_pytorch_basics.md`
- Complete `homework/P3-2_build_mlp.md`
