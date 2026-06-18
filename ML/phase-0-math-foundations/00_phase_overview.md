# Phase 0: Math Foundations for ML

> **Goal:** Review the core linear algebra and calculus needed to understand backpropagation and loss functions.
> **Duration:** 1-2 weeks (condensed for experienced devs)

## The Absolute Essentials

You don't need a math degree to do ML. You need to understand:

1. **Matrix Multiplication:** How data flows through layers.
2. **Derivatives & Chain Rule:** How gradients flow backwards to update weights.
3. **Probability Distributions:** Why we use cross-entropy and what it means.

## Quick Cheat Sheet

### Linear Algebra
- Dot product: scalar output of two vectors. `np.dot(a, b)`
- Matrix mult: `(m x n) @ (n x p) -> (m x p)`. This defines network layer sizes.
- Transpose: swapping rows and columns. Critical for aligning dimensions.

### Calculus
- Derivative: slope of a function. Tells us which way is "downhill" for the loss.
- Partial derivative: slope with respect to *one* variable (one weight).
- Chain rule: $f(g(x))' = f'(g(x)) \cdot g'(x)$. This is backpropagation.

### Probability
- Gaussian (Normal) Distribution: The bell curve. Many ML assumptions rely on this.
- Softmax: Turns a vector of raw scores (logits) into a probability distribution summing to 1.
- Cross-Entropy: Measures how different two probability distributions are.

## Resources
- [3Blue1Brown - Essence of Linear Algebra](https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab)
- [3Blue1Brown - Essence of Calculus](https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr)

## Homework
- Complete `homework/P0-1_math_refresher.md`
