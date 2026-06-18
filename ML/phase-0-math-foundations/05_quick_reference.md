# Phase 0: Quick Reference & Formulas

## Linear Algebra
*   **Dot Product:** $a \cdot b = \sum a_i b_i$
*   **Matrix Multiplication:** Row $i$ of Matrix A dot Column $j$ of Matrix B = element $(i,j)$ of output.
*   **Dimensions:** $(m \times n) \times (n \times p) \rightarrow (m \times p)$

## Calculus & Gradients
*   **Chain Rule:** $\frac{dy}{dx} = \frac{dy}{du} \cdot \frac{du}{dx}$
*   **Gradient Vector ($\nabla f$):** $[\frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, ... ]$ (Points in direction of steepest ascent).
*   **Weight Update Rule (Gradient Descent):** $w_{new} = w_{old} - \alpha \cdot \nabla L$ (where $\alpha$ is learning rate).

## Probability
*   **Softmax:** $\sigma(z)_i = \frac{e^{z_i}}{\sum_{j=1}^K e^{z_j}}$ (Turns logits into probabilities summing to 1).
*   **Cross-Entropy Loss (Binary):** $L = -[y \log(\hat{y}) + (1-y) \log(1-\hat{y})]$
*   **Cross-Entropy Loss (Multi-class):** $L = -\sum y_i \log(\hat{y}_i)$
