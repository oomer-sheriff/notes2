# Fine-Tuning LLMs (PEFT, LoRA, RLHF)

A pre-trained Language Model (like the base LLaMA-3 or GPT-3) is just a document completer. If you prompt it with `"The capital of France is"`, it might say `" Paris."`. But if you prompt it with `"What is the capital of France?"`, it might respond with `"What is the capital of Germany?"` because it thinks you are writing a list of trivia questions.

To turn a "document completer" into a "helpful assistant" (like ChatGPT), we must fine-tune it.

---

## 1. Instruction Tuning (Supervised Fine-Tuning - SFT)

We collect tens of thousands of high-quality (Prompt, Response) pairs written by humans.
We feed these pairs to the model and train it using standard next-token prediction (Cross-Entropy Loss).

**The format matters:** We must introduce special tokens so the model learns the structure of a conversation.
```
<|system|> You are a helpful assistant. <|end|>
<|user|> What is the capital of France? <|end|>
<|assistant|> The capital of France is Paris. <|end|>
```

During training, we only calculate the loss on the `<|assistant|>` tokens. We don't penalize the model for failing to predict the user's prompt.

After SFT, the model learns to stop rambling, answer questions directly, and output the `<|end|>` token when it finishes its thought.

---

## 2. The Problem with Full Fine-Tuning

A model like LLaMA-3 70B has 70 billion parameters. They are stored in FP16 (16 bits, or 2 bytes per parameter).
`70 billion * 2 bytes = 140 GB of VRAM` just to *hold* the model.

During training (backpropagation), you also need to store:
- Gradients (140 GB)
- Optimizer states (e.g., Adam needs momentum and variance for every parameter = 280 GB)
- Forward activations

Full fine-tuning of a 70B model requires nearly **800 GB of VRAM** (about ten $40,000 A100 GPUs). This is inaccessible for most companies. Furthermore, updating all parameters risks "Catastrophic Forgetting" — the model forgets its general knowledge to overfit on the fine-tuning task.

---

## 3. Parameter-Efficient Fine-Tuning (PEFT): LoRA

**LoRA (Low-Rank Adaptation)** solves the VRAM problem.

Instead of updating the massive, original pre-trained weight matrices ($W_{orig}$), we **freeze** them completely. They require no gradients or optimizer states.

We inject two tiny, new trainable matrices ($A$ and $B$) alongside each frozen matrix.
If $W_{orig}$ is $4096 \times 4096$, the weight update $\Delta W$ would normally also be $4096 \times 4096$ (16 million parameters).

LoRA hypothesizes that the "intrinsic rank" of the update is very low. Instead of learning $\Delta W$ directly, we learn it as the product of two much smaller matrices:
$\Delta W = A \times B$
where $A$ is $4096 \times r$, and $B$ is $r \times 4096$. The rank $r$ is a hyperparameter (usually 8, 16, or 64).

If $r=8$:
$A$ parameters: $4096 \times 8 = 32,768$
$B$ parameters: $8 \times 4096 = 32,768$
Total trainable parameters: **65,536** (instead of 16 million!)

During the forward pass:
$Output = (W_{orig} \cdot x) + (A \cdot B \cdot x)$

**Why LoRA is amazing:**
1. Reduces trainable parameters by 99.9%. You can fine-tune a 70B model on a single consumer GPU (with QLoRA).
2. The $A \cdot B$ matrix can be pre-calculated and permanently added back into $W_{orig}$ after training, meaning **zero latency penalty** during inference.
3. You can hot-swap "LoRA adapters" for different tasks on the fly while keeping one copy of the giant base model in memory.

---

## 4. Alignment: RLHF and DPO

After Instruction Tuning, the model might still output toxic content, give dangerous advice, or hallucinate. We need to "align" it with human values.

### RLHF (Reinforcement Learning from Human Feedback)

This is how OpenAI aligned ChatGPT. It is complex and requires three models:
1. **The SFT Model:** The instruction-tuned model we want to improve.
2. **The Reward Model:** We give the SFT model a prompt and generate two different responses (A and B). A human annotator reads them and clicks "I prefer A over B". We train a separate Reward Model to score responses based on human preferences.
3. **The RL Phase (PPO):** We let the SFT model generate responses. The Reward Model scores them. We use a Reinforcement Learning algorithm called PPO (Proximal Policy Optimization) to update the SFT model's weights to maximize the reward score, while keeping a KL-divergence penalty to prevent the model from drifting too far from fluent English.

### DPO (Direct Preference Optimization)

RLHF is notoriously unstable and hard to code. In 2023, Stanford researchers published DPO, which is rapidly replacing RLHF.

**The brilliant insight of DPO:** You don't need a separate Reward Model, and you don't need complex PPO reinforcement learning.
With some clever math, you can use the Language Model *itself* as the reward model.

You still collect the human preference data (Prompt, Preferred Response, Rejected Response).
You optimize a simple loss function that increases the probability of the Preferred Response while decreasing the probability of the Rejected Response.
It is stable, computationally cheap, and achieves identical or better results than RLHF.

---
## References
*   [Hu et al. (2021): LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
*   [Ouyang et al. (2022): Training language models to follow instructions with human feedback (InstructGPT/RLHF)](https://arxiv.org/abs/2203.02155)
*   [Rafailov et al. (2023): Direct Preference Optimization: Your Language Model is Secretly a Reward Model (DPO)](https://arxiv.org/abs/2305.18290)
