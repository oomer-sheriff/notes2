# 04 — Namespaces: Organising Your Cluster

> **The key insight:** Namespaces are organisational and RBAC boundaries — they are NOT network isolation. A pod in namespace `dev` can still talk to a pod in namespace `prod` by default. You need NetworkPolicies for true network isolation (Phase 3).

---

## 🏢 What Are Namespaces?

A namespace is a **logical partition inside a single Kubernetes cluster** that provides a scope for names and a boundary for permissions and resource quotas.

```
┌──────────────────────────────────────────────────────────────────┐
│                      K8s Cluster                                 │
│  Physical: shared nodes, shared etcd, shared API server          │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │
│  │   default   │  │     dev     │  │       production       │  │
│  │             │  │             │  │                        │  │
│  │ [deployment]│  │ [deployment]│  │ [deployment]           │  │
│  │ [service]   │  │ [service]   │  │ [service]              │  │
│  │ [pods]      │  │ [pods]      │  │ [pods]                 │  │
│  │             │  │             │  │                        │  │
│  │ dev team    │  │ dev team    │  │ ops team (only!)       │  │
│  │ can see     │  │ can touch   │  │ (RBAC boundary)        │  │
│  └─────────────┘  └─────────────┘  └────────────────────────┘  │
│                                                                  │
│  All namespaces share the same physical nodes                    │
└──────────────────────────────────────────────────────────────────┘
```

> **Analogy:** Think of a K8s cluster as an **apartment building**.  
> Each namespace is a separate apartment unit.  
> Apartments share the same building infrastructure (elevator, electricity, plumbing = nodes, CPU, RAM).  
> But each apartment has its own locks (RBAC), its own utility bill (ResourceQuota), and your neighbour can't just walk in (if you configure it).  
> However, the hallway between apartments is open by default — anyone can knock on anyone's door (cross-namespace networking without NetworkPolicy).

---

## 📦 The Four Built-in Namespaces

```bash
kubectl get namespaces
# NAME              STATUS
# default           Active   ← Your stuff goes here if you don't specify
# kube-system       Active   ← K8s internals (etcd, API server, scheduler...)
# kube-public       Active   ← Publicly readable; rarely used
# kube-node-lease   Active   ← Node heartbeat objects; internal K8s use
```

**Rules:**
- **Never** deploy your apps into `kube-system` — it's sacred
- **Never** delete `kube-system` or `kube-public` — you'll break your cluster
- `default` is fine for learning, but use named namespaces in real projects

---

## 📏 What Is and Isn't Namespaced

Not every K8s resource belongs to a namespace. Some are cluster-wide:

```bash
# See all namespaced resource types
kubectl api-resources --namespaced=true

# See all CLUSTER-WIDE resource types (not in any namespace)
kubectl api-resources --namespaced=false
```

| Namespaced (belong to a namespace) | Cluster-wide (span all namespaces) |
|-----------------------------------|-----------------------------------|
| Pods | Nodes |
| Deployments | PersistentVolumes |
| Services | ClusterRoles |
| ConfigMaps | StorageClasses |
| Secrets | Namespaces themselves |
| ServiceAccounts | CustomResourceDefinitions |

---

## 🛠️ Namespace Commands

```bash
# ─── CREATE ────────────────────────────────────────────────────
kubectl create namespace dev
kubectl create namespace staging
kubectl create namespace production

# Or via YAML:
kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: team-backend
  labels:
    team: backend
    environment: dev
EOF

# ─── LIST ──────────────────────────────────────────────────────
kubectl get namespaces
kubectl get ns              # Shorthand

# ─── WORK IN A NAMESPACE ───────────────────────────────────────
# Option 1: -n flag every time (explicit, always clear)
kubectl get pods -n dev
kubectl apply -f deployment.yaml -n staging
kubectl delete pod nginx -n dev

# Option 2: Change the default namespace for your session
kubectl config set-context --current --namespace=dev
kubectl get pods          # Now implicitly looks in "dev"
# ↑ CAUTION: easy to forget you changed this and run commands in wrong namespace

# Best practice: use kubens (if installed)
kubens dev               # Switch default namespace
kubens                   # List namespaces, shows current
kubens default           # Switch back to default

# ─── CROSS-NAMESPACE COMMANDS ──────────────────────────────────
kubectl get pods --all-namespaces
kubectl get pods -A                  # Same, shorter

# ─── DELETE ────────────────────────────────────────────────────
kubectl delete namespace dev
# ↑ WARNING: This deletes ALL resources inside the namespace!
#   Deployments, pods, services, configmaps, secrets — everything!
#   There is no "are you sure?" prompt.
```

---

## 💰 ResourceQuotas — Limiting What a Namespace Can Use

ResourceQuotas prevent one team or namespace from consuming all cluster resources.

```yaml
# quota.yaml — limits what the "dev" namespace can consume
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    # Compute resources
    requests.cpu: "4"          # Total CPU requests across all pods ≤ 4 cores
    requests.memory: 8Gi       # Total memory requests ≤ 8GiB
    limits.cpu: "8"            # Total CPU limits ≤ 8 cores
    limits.memory: 16Gi        # Total memory limits ≤ 16GiB

    # Object count limits
    count/pods: "20"           # Max 20 pods
    count/services: "10"       # Max 10 services
    count/deployments.apps: "10"
    count/secrets: "20"
    count/configmaps: "20"
    
    # Storage
    requests.storage: 50Gi     # Total PVC storage requests ≤ 50GiB
```

**Behaviour when quota is exceeded:**
```
If you try to create a pod that would push the namespace over quota:
  kubectl apply -f my-pod.yaml
  Error: pods "my-pod" is forbidden: exceeded quota: dev-quota,
         requested: requests.memory=2Gi, 
         used: requests.memory=7Gi, 
         limited: requests.memory=8Gi
```

**Important:** Once a ResourceQuota is set on a namespace, **every pod MUST specify resource requests and limits**. Pods without them will be rejected.

---

## 📐 LimitRange — Default Resource Limits

A ResourceQuota tells the namespace its budget. A **LimitRange** sets **defaults for containers that don't specify limits**.

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: dev-limits
  namespace: dev
spec:
  limits:
  - type: Container
    default:               # Applied if container doesn't set limits
      cpu: "200m"
      memory: "256Mi"
    defaultRequest:        # Applied if container doesn't set requests
      cpu: "100m"
      memory: "128Mi"
    max:                   # Container can't request more than this
      cpu: "2"
      memory: "2Gi"
    min:                   # Container can't request less than this
      cpu: "10m"
      memory: "32Mi"
```

**The interplay:**
```
LimitRange sets defaults → new pods automatically get those limits
ResourceQuota checks totals → if adding the pod would exceed the quota, rejected

Both work together:
  LimitRange: "No container can use more than 2 CPU"
  ResourceQuota: "This whole namespace can't use more than 8 CPU total"
```

---

## 🏷️ Namespace Best Practices

### Good Namespace Strategies

**By environment (most common):**
```
dev, staging, production
```

**By team:**
```
team-frontend, team-backend, team-data
```

**By application (microservices):**
```
checkout, inventory, auth, notification
```

**Hybrid (team + env):**
```
backend-dev, backend-prod
frontend-dev, frontend-prod
```

### Naming Conventions
```bash
# Use lowercase, hyphens only (no underscores, no dots)
dev ✅
team-backend ✅
my_namespace ❌  (underscores not allowed)
TeamBackend ❌   (uppercase not recommended)
```

---

## 🔍 Common Namespace Gotchas

### Gotcha 1: Forgetting -n Flag

The most common mistake of new K8s users:
```bash
kubectl apply -f deployment.yaml       # Goes to default namespace
kubectl get pods                       # Looking in default... "nothing there!"

# Fix: always be explicit
kubectl apply -f deployment.yaml -n staging
kubectl get pods -n staging
```

### Gotcha 2: Cross-Namespace Service DNS

```bash
# App in "frontend" namespace trying to reach "api" service in "backend" namespace:
curl http://api-service              # ❌ Resolves to api-service.frontend.svc.cluster.local
curl http://api-service.backend      # ❌ Still missing .svc.cluster.local
curl http://api-service.backend.svc.cluster.local  # ✅ Full DNS name required
```

### Gotcha 3: Namespace Deletion is Destructive

```bash
kubectl delete namespace dev     # ← Deletes EVERYTHING in dev, no confirmation!
```

**Safe practice:** Before deleting a namespace, list its contents:
```bash
kubectl get all -n dev           # Review what will be deleted
kubectl get pvc -n dev           # PVCs won't auto-delete if they have data!
kubectl delete namespace dev     # Now delete
```

### Gotcha 4: ClusterRoles vs Roles

- A **Role** lives in a namespace and only grants permission IN that namespace
- A **ClusterRole** is cluster-wide — we'll cover this in Phase 5 (Security)

### Gotcha 5: Secrets Are Per-Namespace

A secret in `dev` is NOT accessible from `production`. You must create the same secret in each namespace that needs it (or use an external secret manager like Vault).

---

## 🧪 Test Yourself

1. **You deployed an app to the `default` namespace. `kubectl get pods` shows it. Your teammate runs the same command and sees nothing. Why?** (Hint: think about contexts and default namespaces): I should have used proper -n and deployed to a certain namespace, but as long as there is no namespace explicitly mentioned in the yaml, the teammate should be able to find the pod in default

2. **What happens when you `kubectl delete namespace production`?** Is there a confirmation prompt?: no conifrmation, destructive

3. **A pod in namespace `checkout` needs to connect to a Redis service in namespace `cache`. What's the correct URL?**rediscache.svc.cluster.local

4. **You set a ResourceQuota of `count/pods: 10` on the `dev` namespace. There are 9 pods. You try to create a deployment with `replicas: 3`. What happens?** one pod will be created and the other 2 will not be created as it will exceed the quota

5. **What's the difference between a LimitRange and a ResourceQuota?**limit sets default limits for containers without any specified resource requirements, resourcequota ensures that a namespace doesnt go past its assigned budget

6. **Why do nodes NOT belong to any namespace?**nodes are physical or virtual machines that run pods, they do not have any concept of namespaces

7. **You have `kubectl config set-context --current --namespace=dev`. You then run `kubectl get secrets`. Are you looking in `dev`, `default`, or all namespaces?** dev because we have switched our context to dev

