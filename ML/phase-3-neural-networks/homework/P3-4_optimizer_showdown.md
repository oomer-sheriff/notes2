# Task P3-4: Optimizer Showdown

**Goal:** Visually compare how different optimizers traverse the loss landscape.

Create a Jupyter Notebook in `homework/lab-files/`.

### The Setup
We are going to train the exact same PyTorch model 4 different times on the Digits dataset (from P3-2). The only thing we will change is the optimizer.

1. **SGD:** `optim.SGD(model.parameters(), lr=0.01)`
2. **SGD + Momentum:** `optim.SGD(model.parameters(), lr=0.01, momentum=0.9)`
3. **Adam:** `optim.Adam(model.parameters(), lr=0.001)`
4. **AdamW:** `optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)`

### The Experiment
1. Write a function `train_model(optimizer_name)` that initializes a fresh model, sets up the chosen optimizer, trains for 200 epochs, and returns a list of the Loss values recorded at every epoch.
2. Run this function for all 4 optimizers.
3. Create a single `matplotlib` line chart.
4. Plot the 4 loss arrays on the same chart (use different colors and add a legend).

### Questions to Answer
*   Which optimizer dropped the loss the fastest in the first 20 epochs?
*   Which optimizer achieved the lowest overall loss at epoch 200?
*   Do you notice the standard SGD curve looking "bumpy" or slow compared to Momentum?

*(Hint: Adam usually wins the speed race, but sometimes well-tuned SGD+Momentum gets a slightly better final result!)*
