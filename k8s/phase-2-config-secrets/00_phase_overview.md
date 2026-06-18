# Phase 2 — Configuration & Secrets

> **Duration:** 2–3 weeks  
> **Daily time:** ~1.5–2 hours  
> **Goal:** Never hardcode config in your containers again. Learn how to inject configuration cleanly, handle sensitive data properly, and understand how the environment influences running pods.

---

## 📁 Files In This Phase

| File | What You'll Learn |
|------|------------------|
| [01_configmaps.md](./01_configmaps.md) | Store and inject non-sensitive config — env vars, files, and volumes |
| [02_secrets.md](./02_secrets.md) | Handle sensitive data — types, security reality, and best practices |
| [03_env_and_volume_patterns.md](./03_env_and_volume_patterns.md) | All the ways config gets into a container — deep patterns guide |
| [04_resource_management.md](./04_resource_management.md) | CPU/memory in depth — QoS classes, VPA, namespace quotas revisited |
| [05_quick_reference.md](./05_quick_reference.md) | Phase 2 cheat sheet |

---

## 🎯 Phase 2 Learning Objectives

By the end of this phase, you should be able to:

- [ ] Create ConfigMaps from literals, files, and directories
- [ ] Mount a ConfigMap as environment variables AND as a file volume
- [ ] Explain the difference between `env.valueFrom.configMapKeyRef` and a volume mount — and when to use each
- [ ] Create all 3 common types of Secrets (Opaque, docker-registry, TLS)
- [ ] Explain why base64 is NOT encryption and what the real risks of K8s Secrets are
- [ ] Configure resource requests, limits, and understand what happens when each is exceeded
- [ ] Explain all 3 QoS classes and what determines which class a pod gets

---

## 🔗 Prerequisite Check

Before starting Phase 2, confirm:
- [ ] Your cluster is running: `kubectl get nodes`
- [ ] You're comfortable creating Deployments and Services from Phase 1
- [ ] You understand labels and selectors (you'll use them again here)

> **Quick note on Services from Phase 1:** If you felt fuzzy on how traffic routing works, the labs in this phase have services in them — revisiting the [Services notes](../phase-1-core-objects/03_services.md) alongside these labs will solidify it naturally.

---

## 📚 Recommended Watching

1. **"Kubernetes ConfigMaps & Secrets Explained"** — TechWorld with Nana  
   → https://www.youtube.com/watch?v=FAnQTgr04mU

2. **"Kubernetes Secrets — Are They Really Secret?"** — CNCF  
   → https://www.youtube.com/watch?v=f4Ru6CPG1z4

---

## ✅ Phase 2 Completion Checklist

- [ ] Read all 4 notes files in this folder
- [ ] Completed [Homework P2-1](./homework/P2-1_configmaps.md) — ConfigMap lab
- [ ] Completed [Homework P2-2](./homework/P2-2_secrets.md) — Secrets security lab
- [ ] Completed [Homework P2-3](./homework/P2-3_resources.md) — Resource management lab
- [ ] Can answer all "Test Yourself" questions at the bottom of each notes file

---

> **← Previous Phase:** [Phase 1 — Core Objects](../phase-1-core-objects/00_phase_overview.md)  
> **Next Phase →:** [Phase 3 — Networking](../phase-3-networking/00_phase_overview.md)
