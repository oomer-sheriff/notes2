# Task P4-3: Transfer Learning with ResNet

**Goal:** Use a pre-trained ResNet18 model to achieve a significantly higher accuracy on CIFAR-10 in a fraction of the time.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. Setup Data
Use the exact same `DataLoader` setup for CIFAR-10 from the previous homework (P4-2).

### 2. Feature Extraction (Freezing Weights)
1. Load a pre-trained ResNet18 model using `torchvision.models`.
2. Loop through the model parameters and set `requires_grad = False` to freeze all the convolutional layers.
3. Replace the final fully connected layer (`model.fc`) with a new `nn.Linear` layer that outputs 10 classes (for CIFAR-10). *Note: The new layer has `requires_grad=True` by default.*
4. Initialize your Optimizer, making sure you only pass the parameters of the new `model.fc` layer! `optim.Adam(model.fc.parameters(), lr=0.001)`
5. Train for just 5 epochs.
6. What is the test accuracy? How does it compare to your from-scratch CNN after 15 epochs?

### 3. Fine-Tuning (Unfreezing Weights)
Now we will fine-tune the *last few* convolutional layers.
1. Re-load the model and re-replace the final layer (start fresh).
2. Freeze *only* the first 3 blocks of ResNet. Leave `model.layer4` and `model.fc` unfrozen.
   *Hint: First freeze everything, then loop through `model.layer4.parameters()` and set `requires_grad=True`.*
3. Initialize the Optimizer. This time pass both the layer4 parameters and the fc parameters. **Use a very small learning rate:** `lr=1e-4`.
4. Train for 5 epochs.
5. What is the test accuracy now?

*Question:* Why do we use a much smaller learning rate when fine-tuning compared to training from scratch?
