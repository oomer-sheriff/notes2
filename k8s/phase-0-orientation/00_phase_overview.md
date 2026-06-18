# Phase 0 — Orientation

> **Duration:** 1–2 weeks  
> **Daily time:** ~1.5 hours  
> **Goal:** Understand _what_ Kubernetes is, _why_ it was invented, and how every component fits together. No commands yet — build the mental model first.

---

## 📁 Files In This Phase

| File | What You'll Learn |
|------|------------------|
| [01_why_kubernetes.md](./01_why_kubernetes.md) | The pain that K8s was built to solve. Docker alone isn't enough. |
| [02_architecture.md](./02_architecture.md) | Every component explained with analogies and diagrams |
| [03_key_mental_models.md](./03_key_mental_models.md) | The 5 mental models that make K8s "click" |
| [04_environment_setup.md](./04_environment_setup.md) | Get a real cluster running on your machine |
| [05_kubectl_first_look.md](./05_kubectl_first_look.md) | Your first kubectl commands — explore a live cluster |

---

## 🎯 Phase 0 Learning Objectives

By the end of this phase, you should be able to:

- [*] Explain what problem Kubernetes solves (in plain English, to a non-technical person): main problem it solves is to easyily maintain and deploy containers as needed and enable communication and scaling easily
- [*] Draw the K8s architecture from memory and label every component
- [*] Explain what each component does and what happens if it dies: etcd is the key value store holding state info, api-server is the gateway for all components to talk to each other, control-plane manages the cluster, scheduler decides which nodes to run pods on, controller-manager manages the control plane, kubelet runs on worker nodes and manages pods, kube-proxy manages the network, container runtime manages containers
- [*] Describe the "desired state vs actual state" model: desired state vs actual state model is the core concept of kubernetes, where you define the desired state of your cluster and the control plane works to maintain that state
- [*] Have a working local cluster (`kind` or `minikube`)
- [*] Run your first `kubectl` commands and understand the output

---

## 📚 Recommended Watching (Before Reading)

Watch these first — visual context makes the notes below much easier to absorb:

1. **"Kubernetes Explained in 15 Minutes"** — TechWorld with Nana  
   → https://www.youtube.com/watch?v=s_o8dwzRlu4

2. **"Kubernetes Architecture Explained"** — KodeKloud  
   → https://www.youtube.com/watch?v=umXEmn3cMkY

3. **"What is a Container?"** — Docker's own explainer (if containers feel fuzzy)  
   → https://www.youtube.com/watch?v=TvnZTi_gaNc

---

## ✅ Phase 0 Completion Checklist

- [*] Read all 5 notes files in this folder
- [*] Watched the 3 videos above
- [ ] Completed [Homework P0-1](./homework/P0-1_architecture_drawing.md) — Architecture from memory
- [ ] Completed [Homework P0-2](./homework/P0-2_kubectl_explore.md) — kubectl exploration lab
- [ ] Can answer the "Test Yourself" questions at the bottom of each notes file

---

> **Next Phase →** [Phase 1 — Core Objects](../phase-1-core-objects/00_phase_overview.md)
