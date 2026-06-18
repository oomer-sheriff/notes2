# Phase 3 — Networking Deep Dive

> **Duration:** 2–3 weeks  
> **Daily time:** ~2 hours  
> **Goal:** Understand how traffic actually flows — inside the cluster, into the cluster, and between locked-down services. Networking is the #1 interview topic for senior K8s roles.

---

## 📁 Files In This Phase

| File | What You'll Learn |
|------|------------------|
| [01_cluster_networking_fundamentals.md](./01_cluster_networking_fundamentals.md) | The flat network model, CNI plugins, pod-to-pod traffic |
| [02_dns_and_service_discovery.md](./02_dns_and_service_discovery.md) | CoreDNS internals, all DNS record types, ndots and search domains |
| [03_ingress.md](./03_ingress.md) | Ingress Controllers, path/host routing, TLS termination |
| [04_network_policies.md](./04_network_policies.md) | Zero-trust networking, ingress/egress rules, policy patterns |
| [05_quick_reference.md](./05_quick_reference.md) | Phase 3 cheat sheet |

---

## 🎯 Phase 3 Learning Objectives

By the end of this phase you should be able to:

- [ ] Explain the K8s flat network model — why every pod can reach every other pod by default
- [ ] Describe what a CNI plugin does and name 3 examples
- [ ] Trace traffic from a pod IP through kube-proxy iptables rules to another pod
- [ ] Explain every part of a K8s DNS name and what `ndots:5` means
- [ ] Deploy an NGINX Ingress Controller and configure path-based + host-based routing
- [ ] Terminate TLS at the Ingress with a self-signed cert
- [ ] Write a default-deny NetworkPolicy and selectively allow traffic
- [ ] Prove NetworkPolicy is enforced using a debug pod

---

## 🔗 Prerequisite Check

Before starting Phase 3:
- [ ] Cluster running with 3 nodes: `kubectl get nodes`
- [ ] You can create Deployments, Services, ConfigMaps, Secrets comfortably
- [ ] You understand that ClusterIP Services have a virtual IP — not a real process

---

## 📚 Recommended Watching

1. **"Kubernetes Networking Explained"** — TechWorld with Nana  
   → https://www.youtube.com/watch?v=5cNrTU6o3Fw

2. **"How Kubernetes Networking Works"** — Hussein Nasser  
   → https://www.youtube.com/watch?v=8I3aSS_KGG8

3. **"Kubernetes NetworkPolicy Explained"** — NerdIO  
   → https://www.youtube.com/watch?v=3gGpMmYeEMA

---

## ✅ Phase 3 Completion Checklist

- [ ] Read all 4 notes files
- [ ] Completed [P3-1](./homework/P3-1_dns_discovery.md) — DNS and CoreDNS lab
- [ ] Completed [P3-2](./homework/P3-2_ingress.md) — Ingress Controller + routing lab
- [ ] Completed [P3-3](./homework/P3-3_network_policy.md) — Zero-trust Network Policy lab
- [ ] Can answer all "Test Yourself" questions

---

> **← Previous Phase:** [Phase 2 — Config & Secrets](../phase-2-config-secrets/00_phase_overview.md)  
> **Next Phase →:** [Phase 4 — Storage](../phase-4-storage/00_phase_overview.md)
