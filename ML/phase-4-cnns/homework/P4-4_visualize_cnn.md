# Task P4-4: Visualize What CNNs See

**Goal:** Crack open the "black box" and look at the actual feature maps inside the network to understand how it makes decisions.

Create a Jupyter Notebook in `homework/lab-files/`.

### 1. Load the Model and an Image
1. Load your trained `SimpleCNN` from Task P4-2 (or just use a pretrained `resnet18`).
2. Download a high-quality picture of a dog or cat from the internet and load it using PIL.
3. Apply the necessary PyTorch transforms to turn it into a tensor and add a batch dimension.

### 2. Extract Feature Maps (Forward Hooks)
PyTorch has a feature called "Hooks" that allows you to grab the output of any intermediate layer during the forward pass.

```python
# List to store our feature maps
activation = {}

def get_activation(name):
    # This hook function will be called every time the layer processes data
    def hook(model, input, output):
        # Save the output tensor (detached from the graph so it doesn't use memory)
        activation[name] = output.detach()
    return hook

# Attach the hook to the FIRST convolutional layer of your model
# E.g., model.features[0].register_forward_hook(get_activation('conv1'))
# Attach a second hook to the LAST convolutional layer
# E.g., model.features[8].register_forward_hook(get_activation('conv3'))
```

1. Pass your image through the network (`model(image_tensor)`).
2. The `activation` dictionary should now contain the tensors output by those specific layers.

### 3. Visualization
The output of the first convolutional layer will have shape `[1, 32, H, W]` (assuming 32 filters).

1. Pick the first 16 feature maps from `conv1`.
2. Use `matplotlib.pyplot.subplots(4, 4)` to plot a 4x4 grid.
3. Display the 16 feature maps as grayscale images.
4. *Observe:* Do you see filters that act like edge detectors? Color detectors?

Repeat the visualization for the last convolutional layer.
*Observe:* These images will look very blurry and abstract. Why? Because deep layers detect high-level semantic concepts (like "dog ear"), not raw pixels!
