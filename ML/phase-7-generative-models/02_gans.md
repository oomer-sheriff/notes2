# GANs — Generative Adversarial Networks

## The Adversarial Idea

The VAE generates samples by optimizing a loss function. The GAN (Goodfellow et al., 2014) takes a completely different approach: **pit two networks against each other**.

- **Generator (G):** Takes random noise z and produces fake data G(z). It tries to fool the discriminator.
- **Discriminator (D):** Takes an input (real or fake) and outputs a probability of it being real. It tries to catch the generator.

The analogy: G is a **counterfeiter** printing fake banknotes. D is a **detective** trying to catch counterfeits. Both get better over time. When the game reaches equilibrium, the counterfeiter's fakes are indistinguishable from real banknotes.

```
         z ~ N(0,1)
             ↓
     [Generator G]   →   G(z) = "fake"
                              ↓
Real data x  → →  [Discriminator D] → P(real) ∈ [0,1]
```

---

## The Min-Max Game

The GAN objective is a two-player game:

```
min_G max_D  E[log D(x)]  +  E[log(1 - D(G(z)))]
              ↑                    ↑
     D wants this HIGH     D wants D(G(z)) low → log(1-D(G(z))) high
     (correctly say real   G wants D(G(z)) high → G(z) fools D
     is real)
```

**Discriminator training:** Maximize the chance of correctly classifying real as real and fake as fake.
- Real samples: D should output ~1.0 → loss term: `-log(D(x))`
- Fake samples: D should output ~0.0 → loss term: `-log(1 - D(G(z)))`

**Generator training:** Minimize the chance of being caught.
- G wants D(G(z)) to be high (close to 1.0, "real")
- Generator loss: `-log(D(G(z)))` (the "non-saturating" version — practical improvement over the original)

---

## Building a GAN for MNIST

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import torchvision.utils as vutils
import matplotlib.pyplot as plt
import numpy as np

# --- Data ---
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))  # Normalize to [-1, 1] to match Generator's Tanh output
])

train_data   = datasets.MNIST('./data', train=True, download=True, transform=transform)
train_loader = DataLoader(train_data, batch_size=128, shuffle=True)

LATENT_DIM = 100
device     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


class Generator(nn.Module):
    """
    Maps random noise z → fake MNIST image.
    
    Input:  z of shape (batch, 100) — random noise from N(0,1)
    Output: image of shape (batch, 1, 28, 28) — a fake digit
    
    We use LeakyReLU instead of ReLU in the hidden layers — the small
    negative slope (0.2) helps gradients flow even for negative activations.
    
    BatchNorm1d stabilizes training by normalizing layer outputs.
    
    The final Tanh maps output to [-1, 1], matching our normalized real images.
    """
    def __init__(self, latent_dim=100):
        super().__init__()
        self.net = nn.Sequential(
            # 100 → 256
            nn.Linear(latent_dim, 256),
            nn.BatchNorm1d(256),
            nn.LeakyReLU(0.2),
            
            # 256 → 512
            nn.Linear(256, 512),
            nn.BatchNorm1d(512),
            nn.LeakyReLU(0.2),
            
            # 512 → 1024
            nn.Linear(512, 1024),
            nn.BatchNorm1d(1024),
            nn.LeakyReLU(0.2),
            
            # 1024 → 784 (= 1×28×28 pixels)
            nn.Linear(1024, 784),
            nn.Tanh()  # Output range [-1, 1] to match normalized real images
        )
    
    def forward(self, z):
        # z: (batch, latent_dim)
        return self.net(z).view(-1, 1, 28, 28)  # Reshape to image


class Discriminator(nn.Module):
    """
    Maps a (real or fake) image → probability of being real.
    
    Input:  image of shape (batch, 1, 28, 28)
    Output: scalar in [0,1] — probability the image is REAL
    
    NO BatchNorm in the discriminator — it can cause training instability.
    LeakyReLU is standard for discriminators.
    Dropout adds regularization — prevents D from becoming too strong too fast.
    """
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Flatten(),                           # (batch, 1, 28, 28) → (batch, 784)
            
            nn.Linear(784, 512),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(512, 256),
            nn.LeakyReLU(0.2),
            nn.Dropout(0.3),
            
            nn.Linear(256, 1),
            nn.Sigmoid()                            # Output: P(real) ∈ [0,1]
        )
    
    def forward(self, x):
        return self.net(x)


G = Generator(LATENT_DIM).to(device)
D = Discriminator().to(device)

# Separate optimizers — G and D are trained independently
# D usually uses a slightly lower LR to prevent it from dominating too quickly
opt_G = torch.optim.Adam(G.parameters(), lr=0.0002, betas=(0.5, 0.999))
opt_D = torch.optim.Adam(D.parameters(), lr=0.0001, betas=(0.5, 0.999))
# betas=(0.5, 0.999) is the standard GAN setting — lower beta1 than Adam default

criterion = nn.BCELoss()
```

---

## The Training Loop (Two-Step Per Batch)

GAN training alternates between updating D and updating G. These are **separate backward passes** — you never update both at the same time.

```python
# Fixed noise for monitoring: generate the SAME fake images every epoch
fixed_noise = torch.randn(16, LATENT_DIM).to(device)

d_losses, g_losses = [], []

for epoch in range(50):
    d_loss_epoch, g_loss_epoch = 0, 0
    
    for real_images, _ in train_loader:
        real_images = real_images.to(device)
        batch_size  = real_images.size(0)
        
        # --- Labels ---
        # Real images get label 1.0, fake images get label 0.0
        # Label smoothing: use 0.9 instead of 1.0 for real — prevents D from becoming overconfident
        real_labels = torch.full((batch_size, 1), 0.9, device=device)
        fake_labels = torch.zeros(batch_size, 1, device=device)
        
        # ===== STEP 1: Train the Discriminator =====
        # Goal: D correctly classifies real as real AND fake as fake
        # We freeze G while training D — opt_D.zero_grad() only zeroes D's gradients
        D.zero_grad()
        
        # D on real images — should output ~1.0
        output_real = D(real_images)
        loss_D_real = criterion(output_real, real_labels)
        
        # Generate fake images — detach so gradients don't flow into G
        # "detach" is critical here: we don't want to update G when training D
        z            = torch.randn(batch_size, LATENT_DIM).to(device)
        fake_images  = G(z).detach()    # .detach() stops gradient from reaching G
        output_fake  = D(fake_images)
        loss_D_fake  = criterion(output_fake, fake_labels)
        
        # Total D loss: sum of real and fake losses
        loss_D = loss_D_real + loss_D_fake
        loss_D.backward()
        opt_D.step()
        
        # ===== STEP 2: Train the Generator =====
        # Goal: G produces fakes that D calls real (label 1.0)
        # We DON'T freeze D — G needs D's gradients to know how to improve
        G.zero_grad()
        
        z           = torch.randn(batch_size, LATENT_DIM).to(device)
        fake_images = G(z)                          # Generate fresh fakes (not detached!)
        output      = D(fake_images)                # D evaluates these fakes
        
        # Generator loss: wants D to say these fakes are REAL (label 1.0)
        # This is the "non-saturating" trick: use log(D(G(z))) instead of log(1-D(G(z)))
        loss_G = criterion(output, real_labels)     # Fool D into thinking fakes are real
        loss_G.backward()
        opt_G.step()
        
        d_loss_epoch += loss_D.item()
        g_loss_epoch += loss_G.item()
    
    d_losses.append(d_loss_epoch / len(train_loader))
    g_losses.append(g_loss_epoch / len(train_loader))
    
    # Generate images from fixed noise to monitor progress
    if (epoch + 1) % 10 == 0:
        G.eval()
        with torch.no_grad():
            fake_grid = G(fixed_noise).cpu()
        G.train()
        
        grid = vutils.make_grid(fake_grid, nrow=4, normalize=True)
        plt.figure(figsize=(8, 8))
        plt.imshow(grid.permute(1, 2, 0))
        plt.title(f'Epoch {epoch+1} Generated Images')
        plt.axis('off')
        # plt.show()
        
        print(f"Epoch {epoch+1}: D_loss={d_losses[-1]:.4f}, G_loss={g_losses[-1]:.4f}")


# Plot loss curves
plt.figure(figsize=(10, 4))
plt.plot(d_losses, label='Discriminator Loss')
plt.plot(g_losses, label='Generator Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.title('GAN Training Dynamics')
# plt.show()
```

---

## The Failure Modes: Mode Collapse

Mode collapse is when the Generator learns to produce only one or a few types of outputs (e.g., always generates the digit "1") because those happen to fool the discriminator. The name comes from probability theory: G collapses to generating only one "mode" of the data distribution.

**How to detect it:** Look at a grid of generated images. If every image looks nearly identical despite different input noise, you have mode collapse.

**How to trigger it intentionally (for learning):**
```python
# 1. Make G too powerful relative to D:
G_big = Generator(latent_dim=100)  # Make G much larger
# Add extra layers to G while keeping D small

# 2. Train G too many times per D update:
for _ in range(5):  # Train G 5× more than D
    # G update...

# 3. Use too high a learning rate for G:
opt_G_bad = torch.optim.Adam(G.parameters(), lr=0.01)  # 50× higher than normal
```

**Solutions in practice:**
- **Wasserstein GAN (WGAN):** Uses a different loss based on the Wasserstein distance — more stable, better mode coverage
- **Progressive Growing (ProGAN):** Start with low-resolution images, gradually increase resolution
- **StyleGAN:** Separate style from content; spectral normalization stabilizes training
- **Minibatch discrimination:** Allow D to see multiple samples at once, making it harder to collapse to one mode

---
## References
*   [Goodfellow et al. (2014): Generative Adversarial Nets](https://arxiv.org/abs/1406.2661) — The original GAN paper
*   [Arjovsky et al. (2017): Wasserstein GAN](https://arxiv.org/abs/1701.07875)
*   [Karras et al. (2019): A Style-Based Generator Architecture for GANs](https://arxiv.org/abs/1812.04948) — StyleGAN
