# Phase 1 — Core Objects

> **Duration:** 2–3 weeks  
> **Daily time:** ~1.5–2 hours  
> **Goal:** Master the four fundamental building blocks of Kubernetes: Pods, ReplicaSets, Deployments, and Services. These are the objects you'll use in EVERY phase after this.

---

## 📁 Files In This Phase

| File | What You'll Learn |
|------|------------------|
| [01_pods.md](./01_pods.md) | The atomic unit — what a pod is, lifecycle, patterns, probes |
| [02_replicasets_deployments.md](./02_replicasets_deployments.md) | Self-healing and rolling updates — the heart of production deploys |
| [03_services.md](./03_services.md) | Stable networking — ClusterIP, NodePort, LoadBalancer, DNS |
| [04_namespaces.md](./04_namespaces.md) | Virtual clusters — isolation, quotas, naming scope |
| [05_quick_reference.md](./05_quick_reference.md) | Phase 1 cheat sheet |

---

## 🎯 Phase 1 Learning Objectives

By the end of this phase, you should be able to:

- [ ] Explain what a Pod is and why it's the atomic unit (not a container)
- [ ] Describe all Pod lifecycle states and what causes each
- [ ] Explain the 3 multi-container pod patterns (Sidecar, Ambassador, Adapter)
- [ ] Explain the difference between a ReplicaSet and a Deployment
- [ ] Perform a rolling update and roll it back from the CLI
- [ ] Explain all 4 Service types and when to use each
- [ ] Use `kubectl exec` to verify cross-pod DNS communication works
- [ ] Set up namespace isolation and explain what it does/doesn't do

---

## 🔗 Prerequisite Check

Before starting Phase 1, make sure:
- [ ] Your kind cluster is running: `kubectl get nodes` shows 3 `Ready` nodes
- [ ] You're comfortable with `kubectl get`, `describe`, `logs`, `exec`

> **Note on cluster startup:** If `kind create cluster` hung for you earlier, it's likely a Docker Desktop resource issue. Try: Settings → Resources → increase RAM to 6-8GB and retry.

---

## 📚 Recommended Watching (Before Reading)

1. **"Kubernetes Pods Explained"** — TechWorld with Nana  
   → https://www.youtube.com/watch?v=5cNrTU6o3Fw

2. **"Kubernetes Deployments & Rolling Updates"** — KodeKloud  
   → https://www.youtube.com/watch?v=mNK14yXIZF4

3. **"Kubernetes Services Explained"** — TechWorld with Nana  
   → https://www.youtube.com/watch?v=T4Z7visMM4E

---

## ✅ Phase 1 Completion Checklist

- [ ] Read all 4 notes files in this folder
- [ ] Completed [Homework P1-1](./homework/P1-1_pod_lifecycle.md) — Pod deep dive lab
- [ ] Completed [Homework P1-2](./homework/P1-2_deployments.md) — Rolling update + rollback lab
- [ ] Completed [Homework P1-3](./homework/P1-3_services.md) — Service types + DNS lab
- [ ] Completed [Homework P1-4](./homework/P1-4_namespaces.md) — Namespace isolation lab
- [ ] Can answer all "Test Yourself" questions at the bottom of each notes file

---

> **← Previous Phase:** [Phase 0 — Orientation](../phase-0-orientation/00_phase_overview.md)  
> **Next Phase →:** [Phase 2 — Config & Secrets](../phase-2-config-secrets/00_phase_overview.md)
