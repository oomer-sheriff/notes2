# Task P7-2: Generative Adversarial Networks (GANs)

**Goal:** Build a DCGAN-style network, train it on MNIST using the two-step adversarial process, and learn how to trigger and identify mode collapse.

Create a Jupyter Notebook in `homework/lab-files/`. **Run on GPU.**

## Part 1: Build and Train the GAN
1. Copy the Generator and Discriminator architectures from `02_gans.md`.
2. Implement the training loop carefully. Remember the crucial details:
   - `D.zero_grad()` before computing D's loss
   - `fake_images.detach()` when training D
   - `G.zero_grad()` before computing G's loss
   - Generate fresh fakes (no detach) when training G
   - Use label smoothing (0.9) for real labels when training D.
3. Train for 50 epochs. Save a grid of 16 generated images every 5 epochs.

## Part 2: Visualize the Game
Plot the Generator and Discriminator losses over time. 
**Question:** Unlike a normal neural network where loss goes to 0, GAN losses oscillate and eventually plateau around a certain value. If the discriminator outputs exactly 0.5 for everything (perfect equilibrium), what theoretical value should the BCE loss converge to? Calculate `-ln(0.5)`. Does your plot reflect this?

## Part 3: Intentional Mode Collapse
Create a new instance of the model, but intentionally break it to cause mode collapse.
1. Increase the Generator's learning rate to `0.01`.
2. Remove the `BatchNorm1d` layers from the Generator.
3. Train for 10 epochs.
4. Plot a grid of 16 generated images.
**Observation:** You should see that almost all generated images look identical (e.g., they all look like the number "1" or "7"), regardless of the input noise. The generator has collapsed to a single mode.
