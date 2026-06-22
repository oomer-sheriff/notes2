# Step-by-Step: Diffusion Model (Forward & Reverse)

**Scenario:** We have a tiny 1-pixel image with value `x_0 = 0.8`. We will run 2 steps of forward diffusion to turn it into noise, and then simulate 1 step of reverse diffusion (denoising).

---

## 1. Defining the Noise Schedule

A diffusion model needs a predefined schedule of variances ($\beta$) that dictate how much noise to add at each step $t$. Let's define a tiny 2-step schedule.

```
T = 2 steps
β_1 = 0.2    (Step 1 adds a little noise)
β_2 = 0.5    (Step 2 adds a lot of noise)
```

We pre-calculate the $\alpha$ values, which represent how much of the *original signal* is retained:
```
α_t = 1 - β_t
α_1 = 1 - 0.2 = 0.8
α_2 = 1 - 0.5 = 0.5
```

And the cumulative product $\bar{\alpha}_t$, which tells us how much original signal remains if we jump directly from $t=0$ to $t$:
```
ᾱ_1 = α_1 = 0.8
ᾱ_2 = α_1 * α_2 = 0.8 * 0.5 = 0.4
```

---

## 2. Forward Process (Adding Noise)

Let's say we want to jump directly to $t=2$ during training.

Formula: $x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1 - \bar{\alpha}_t} \epsilon$

1. **Original Image:** `x_0 = 0.8`
2. **Sample Random Noise:** Let's say the random number generator spits out `ε = -0.5`
3. **Compute Scaling Factors for t=2:**
   - Signal scale: $\sqrt{\alphā_2} = \sqrt{0.4} \approx 0.632$
   - Noise scale: $\sqrt{1 - ᾱ_2} = \sqrt{1 - 0.4} = \sqrt{0.6} \approx 0.775$
4. **Compute Noisy Image $x_2$:**
   ```
   x_2 = (0.632 * 0.8) + (0.775 * -0.5)
       = 0.5056 - 0.3875
       = 0.1181
   ```

The image has degraded from `0.8` to `0.1181`. The original structure is being washed out by the noise `ε`.

---

## 3. Training the U-Net (Predicting the Noise)

During training, we feed the noisy image $x_2$ and the timestep $t=2$ into our neural network (the U-Net).

**Input:** `x_2 = 0.1181`, `t = 2`

**Goal:** The network must predict the *exact* noise `ε` that was added.
The target is `ε = -0.5`.

Let's say our untrained network predicts `ε_pred = -0.1`.

**Loss:**
```
MSE = (ε_pred - ε_target)²
    = (-0.1 - (-0.5))²
    = (0.4)²
    = 0.16
```
We backpropagate this loss to update the U-Net weights so next time it predicts closer to `-0.5`.

---

## 4. Reverse Process (Sampling / Generation)

Now imagine the network is fully trained. We want to generate a new image from scratch.

We start at $t=2$ with pure random noise.
**Sample initial noise:** Let's say `x_2 = 0.9`

### Denoising Step: $t=2 \rightarrow t=1$

1. **Predict Noise:** We feed `x_2 = 0.9` and `t = 2` to our trained network. Let's assume the network perfectly predicts that the noise inside `x_2` is `ε_pred = 0.4`.

2. **Remove the Noise (Math):**
   The simplified formula to step backwards from $x_t$ to $x_{t-1}$ is:
   $x_{t-1} = \frac{1}{\sqrt{\alpha_t}} \left( x_t - \frac{\beta_t}{\sqrt{1 - \bar{\alpha}_t}} \epsilon_{pred} \right) + \sigma_t z$
   *(Note: $\sigma_t z$ is a small injection of fresh random noise, which is crucial for sample quality, but we'll set $z=0$ here for simplicity).*

   Let's plug in the numbers for $t=2$:
   - $\alpha_2 = 0.5$  $\rightarrow$  $\frac{1}{\sqrt{0.5}} \approx 1.414$
   - $\beta_2 = 0.5$
   - $\sqrt{1 - \bar{\alpha}_2} = \sqrt{1 - 0.4} = \sqrt{0.6} \approx 0.775$

   ```
   x_1 = 1.414 * (0.9 - (0.5 / 0.775) * 0.4)
       = 1.414 * (0.9 - (0.645) * 0.4)
       = 1.414 * (0.9 - 0.258)
       = 1.414 * 0.642
       = 0.908
   ```

We have successfully stepped backwards to $x_1$. We would then repeat this exact process: pass $x_1$ and $t=1$ to the network, predict the new noise, and subtract it to arrive at the final clean image $x_0$!

---
## Key Takeaways

| Concept | The Math in Plain English |
|---|---|
| Forward Process | Mixes the real image with random noise based on a predetermined schedule. |
| $\bar{\alpha}_t$ | The "shortcut" multiplier that lets us jump instantly to timestep $t$ without simulating all previous steps. |
| The Loss | `MSE(actual_noise, predicted_noise)`. It does *not* try to predict the clean image directly. |
| Reverse Process | Iteratively predicting noise and subtracting a fraction of it to slowly reveal a clean image out of pure static. |
