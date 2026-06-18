# Phase 10: Advanced Topics

> **Goal:** Explore specialized domains beyond standard deep learning.
> **Duration:** 3 weeks

## Reinforcement Learning (RL)
Learning by trial and error based on rewards.
- **Value-based (Q-Learning, DQN):** Learn the value of taking an action in a given state.
- **Policy-based (REINFORCE, PPO):** Directly learn the best action to take.

## Graph Neural Networks (GNNs)
For data that doesn't fit in grids (images) or sequences (text).
- Social networks, molecular structures, knowledge graphs.
- **Message Passing:** Nodes update their state by aggregating information from neighbors.

## Efficient Training
- **Mixed Precision:** Training with 16-bit floats instead of 32-bit.
- **Gradient Checkpointing:** Saving memory by recomputing activations instead of storing them.
- **Mixture of Experts (MoE):** Sparse models where only a subset of parameters (experts) is used for any given token (e.g., Mixtral 8x7B).

## Homework
- Complete `homework/P10-1_dqn_agent.md`
