# Phase 9: MLOps

> **Goal:** Adapt your DevOps/Backend knowledge to ML pipelines.
> **Duration:** 2 weeks (condensed for backend dev)

## You already know:
- Docker, Kubernetes, FastAPI, CI/CD, Prometheus.

## What's new in MLOps:
1. **Experiment Tracking:** ML models aren't code. They are code + data + hyperparameters. You need to track all three (Weights & Biases, MLflow).
2. **Data Versioning:** Git is bad at large files. DVC (Data Version Control) acts like Git for datasets.
3. **Model Serving Optimization:** Running PyTorch in Python is slow. You compile models using ONNX or TensorRT, or serve LLMs using vLLM (which handles continuous batching and KV caching).
4. **Monitoring for Drift:** Software fails immediately (500 error). ML models fail silently (predicting the wrong thing because input distributions changed).

## Homework
- Complete `homework/P9-1_wandb_tracking.md`
- Complete `homework/P9-2_onnx_export.md`
