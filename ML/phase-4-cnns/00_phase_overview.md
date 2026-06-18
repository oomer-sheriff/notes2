# Phase 4: Convolutional Neural Networks (CNNs) & Vision

> **Goal:** Understand spatial data processing and the evolution of vision architectures.
> **Duration:** 2-3 weeks

## Why Convolutions?
Fully connected networks (MLPs) ignore the spatial structure of images (they flatten a 2D image into a 1D vector).
**Convolutions** preserve spatial relationships.
- **Local Connectivity:** A neuron only looks at a small patch of the image.
- **Parameter Sharing:** The same "filter" (e.g., an edge detector) is swept across the whole image, drastically reducing the number of weights to learn.

## The CNN Recipe
1. **Conv Layer:** Extracts features.
2. **ReLU:** Adds non-linearity.
3. **Pooling (Max/Avg):** Downsamples the image, making it robust to translations.
4. **Fully Connected Layers (at the end):** Combines features for final classification.

## Transfer Learning
Training a deep CNN from scratch takes massive data and compute.
Instead, we use models pre-trained on ImageNet (like ResNet).
- **Feature Extraction:** Freeze the CNN backbone, only train a new final classification layer.
- **Fine-Tuning:** Unfreeze the top layers and train with a very small learning rate.

## Homework
- Complete `homework/P4-1_cnn_from_scratch.md`
- Complete `homework/P4-2_transfer_learning.md`
