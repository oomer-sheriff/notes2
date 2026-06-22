# Task P7-1: Autoencoders and VAEs

**Goal:** Build a VAE from scratch on MNIST, demonstrate generation by sampling from the latent space, and perform latent space interpolation.

Create a Jupyter Notebook in `homework/lab-files/`.

## Part 1: Standard Autoencoder Baseline
1. Use the code from `01_autoencoders_and_vaes.md` to train a standard Autoencoder with `latent_dim=2`.
2. Extract the 2D latent codes for the entire test set.
3. Scatter plot the 2D codes, coloring the points by their true digit label (0-9).
4. **Observation:** You should see that the clusters are irregular, and there are large "empty" gaps between clusters. If you sample a coordinate from one of these empty gaps and decode it, it will look like garbage.

## Part 2: Build the VAE
1. Implement the VAE model from the concept notes.
2. Train it for 20 epochs using the combined loss function (Reconstruction BCE + KL Divergence).
3. Repeat the scatter plot experiment: plot the 2D latent means (`μ`) of the test set.
4. **Observation:** The clusters should now be much more tightly packed around the origin (0,0) with no empty gaps, forming a continuous blob.

## Part 3: Generation and Interpolation
1. **Generate:** Sample a 10×10 grid of points uniformly spaced across the 2D latent space (e.g., x from -3 to 3, y from -3 to 3). Decode these 100 points and plot them in a 10×10 image grid. You should see a smooth transition of digits mapping the entire 2D space!
2. **Interpolate:** Pick a real image of a "2" and a real image of a "7". Encode them to get `μ_2` and `μ_7`. Create 10 intermediate points between them using linear interpolation. Decode and plot the 10 frames. Watch the "2" morph smoothly into a "7".
