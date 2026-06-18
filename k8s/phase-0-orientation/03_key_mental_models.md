# 03 — The 5 Mental Models That Make K8s "Click"

> These are the conceptual frameworks that separate people who "use" K8s from people who truly *understand* it. Internalize these and debugging becomes intuitive.

---

## Mental Model #1 — Everything is a Declarative Object

### The Idea
In Kubernetes, you don't issue commands like "start this container" or "stop that server."  
Instead, you **declare the desired state** of an object — and K8s figures out how to make it so.

Every single thing in K8s is an **object** with the same structure:

```yaml
apiVersion: apps/v1          # Which API group handles this
kind: Deployment             # What type of object is this
metadata:                    # Who is it? (name, labels, etc.)
  name: my-web-app
  namespace: production
  labels:
    team: frontend
    version: v2
spec:                        # ← DESIRED STATE (what you want)
  replicas: 3
  ...

status:                      # ← ACTUAL STATE (what K8s sees)
  readyReplicas: 3           #   (K8s fills this in, not you)
  availableReplicas: 3
  ...
```

**`spec` = what you want.**  
**`status` = what K8s has.**  
**Controllers exist to close the gap between them.**

> **Analogy:** It's like ordering food at a restaurant.  
> You don't go into the kitchen and fry the burger yourself (imperative).  
> You tell the waiter "I'd like a cheeseburger, medium, no onions" (declarative).  
> The kitchen (K8s) figures out who cooks it, which pan, how long.  
> Your job is done at the moment you hand in your order.

### Why This Matters
- You can store all your K8s configs in Git → **GitOps**
- If something drifts, K8s will auto-correct it
- "Idempotent" — applying the same config twice doesn't cause harm
- You can recreate your ENTIRE infrastructure from a folder of YAML files

---

## Mental Model #2 — Labels and Selectors Are the Glue

### The Idea
K8s objects don't reference each other by name (with a few exceptions). Instead, they find each other through **labels** (tags on objects) and **selectors** (queries that match labels).

```
Labels are like price tags you stick on objects:

  ┌─────────────────────────┐     ┌─────────────────────────┐
  │  Pod                    │     │  Pod                    │
  │  labels:                │     │  labels:                │
  │    app: web-frontend    │     │    app: web-frontend    │
  │    version: v1          │     │    version: v2          │
  │    env: production      │     │    env: production      │
  └─────────────────────────┘     └─────────────────────────┘
  
  Service selector: app=web-frontend
  → Matches BOTH pods. Traffic goes to both.
  
  Deployment selector: app=web-frontend, version=v1
  → Matches only first pod. Only that pod is "owned."
```

**Labels are used for:**

| Use Case | Who Has Labels | Who Uses Selector |
|----------|---------------|------------------|
| Service → finds its backend pods | Pods | Service |
| Deployment → finds its pods | Pods | Deployment |
| Scheduling → place pod on correct node | Nodes | Pod's nodeSelector |
| Network policy → restrict who can talk | Pods | NetworkPolicy |

> **Analogy:** Labels are like **employee badges** in a large company.  
> Each employee (pod) wears a badge that says their department, role, and team.  
> When HR (a Service) sends out a memo, they send it to "everyone with badge: dept=Engineering, team=Backend" — they don't need to know individual names.  
> When you need to fire someone (delete pods), you fire everyone matching "team=Legacy".

### The Most Common Mistake
A Service selector doesn't match the pod labels → Service has no endpoints → traffic goes nowhere.  
**Always verify:** `kubectl get endpoints <service-name>`  
If you see `<none>`, your labels don't match.

```bash
# Check what labels a pod has
kubectl get pods --show-labels

# Check what a service's selector is
kubectl get svc my-service -o yaml | grep -A5 selector

# Check endpoints (real pod IPs the service routes to)
kubectl get endpoints my-service
```

---

## Mental Model #3 — Every Object Has an Owner (The Owner Reference Chain)

### The Idea
When you create a Deployment, K8s creates a hierarchy:

```
You create:
  Deployment "web-app"
         │
         │ creates (owns)
         ▼
  ReplicaSet "web-app-7f8d9c"
         │
         │ creates (owns)
         ├─────────────────┬──────────────────┐
         ▼                 ▼                  ▼
  Pod "web-app-abc"  Pod "web-app-def"  Pod "web-app-ghi"
```

Each object has `metadata.ownerReferences` pointing to its parent:

```yaml
# Inside a Pod's YAML (K8s fills this in automatically):
metadata:
  ownerReferences:
  - apiVersion: apps/v1
    kind: ReplicaSet
    name: web-app-7f8d9c
    uid: abc-123-...
```

### Why This Matters

1. **Garbage collection:** Delete the Deployment → K8s cascades the delete to ReplicaSet → then to Pods. The ownership chain handles cleanup.

2. **Self-healing:** Pod dies → ReplicaSet controller notices pod count dropped → creates new pod (it's the RS's responsibility because it's the owner).

3. **Debugging:** A pod that won't die? Check if something owns it. You can't permanently delete a pod owned by a Deployment by deleting the pod — the ReplicaSet immediately recreates it. **Delete the Deployment to permanently remove pods.**

> **Analogy:** Think of it like a **corporate org chart**.  
> If the VP (Deployment) is let go, all their direct reports (ReplicaSets) and their reports (Pods) are also let go — the whole subtree is cleaned up.  
> If an individual employee quits (pod dies), HR (ReplicaSet) just hires a replacement automatically.

---

## Mental Model #4 — Nodes Are Just Cattle, Not Pets

### The Idea
In traditional ops, servers were "pets" — each one had a name, a history, was carefully maintained. You'd SSH in, patch it, babysit it. Losing a server was traumatic.

In Kubernetes, nodes are "cattle" — interchangeable, disposable, numbered.

```
Old mindset (pets):
  "Oh no, web-server-3 is down! 
   That's the one with the custom SSL cert and 
   Bob manually configured nginx on it last year.
   This is a crisis."

K8s mindset (cattle):
  "Node 3 is down. 
   K8s moved all 12 pods to nodes 1, 2, 4, and 5.
   I'll order a replacement node.
   No data was lost. No action needed."
```

This is possible because:
- **All state** is in etcd, not on nodes
- **Container images** come from a registry — any node can pull them
- **Persistent data** goes in PersistentVolumes — separate from the node
- **Config** comes from ConfigMaps/Secrets — injected at runtime

> **Analogy:** Think of nodes like **hotel rooms**.  
> The hotel (cluster) works perfectly even if Room 204 is out of service.  
> You (the pod) move to Room 312. Your luggage (data) is in a storage unit (PersistentVolume), not in the room.  
> The room number means nothing — the room is a commodity.

### What This Means For You
- Never `ssh` into a node and manually change things → K8s doesn't know about it, will be overwritten
- Never store application data on the node filesystem → use PersistentVolumes
- Design apps assuming the underlying node can disappear at any time

---

## Mental Model #5 — Namespaces Are Soft Walls, Not Hard Prisons

### The Idea
Namespaces divide a cluster into virtual sub-clusters. Think of them as "rooms" in a house.

```
┌──────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                    │
│                                                          │
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────┐  │
│  │   namespace:  │  │   namespace:  │  │ namespace:  │  │
│  │     dev       │  │    staging    │  │   prod      │  │
│  │               │  │               │  │             │  │
│  │ [pods]        │  │ [pods]        │  │ [pods]      │  │
│  │ [services]    │  │ [services]    │  │ [services]  │  │
│  │ [deployments] │  │ [deployments] │  │ [deployments│  │
│  └───────────────┘  └───────────────┘  └─────────────┘  │
│                                                          │
│  Physical resources (nodes, storage) are SHARED         │
└──────────────────────────────────────────────────────────┘
```

**What namespaces DO provide:**
- Scope for names (two pods can both be called "nginx" in different namespaces)
- RBAC boundaries (dev team can only see/touch their namespace)
- ResourceQuota (limit how much CPU/RAM a namespace can use)
- NetworkPolicy (restrict cross-namespace traffic)

**What namespaces DON'T provide:**
- Network isolation (by default, pods CAN still talk cross-namespace)
- Node isolation (pods in different namespaces CAN land on the same node)
- True security boundaries (that's NetworkPolicy + RBAC combined)

**Built-in namespaces:**

| Namespace | Purpose |
|-----------|---------|
| `default` | Where your stuff goes if you don't specify |
| `kube-system` | K8s internal components (DNS, proxy, etc.) — don't touch! |
| `kube-public` | Publicly readable config; rarely used |
| `kube-node-lease` | Node heartbeat objects; internal use |

> **Analogy:** Namespaces are like **floors in an office building**.  
> Floor 3 (dev) and Floor 4 (prod) share the same elevator, electrical system, and parking lot (physical resources).  
> But Floor 3 employees don't usually wander into Floor 4 offices.  
> Security badges (RBAC) and locked doors (NetworkPolicy) enforce that — but the building infrastructure is shared.

### Important: Cross-Namespace Service DNS

This trips people up. Services in other namespaces ARE reachable, but you need the full DNS name:

```
Within same namespace:
  curl http://my-service           ✅ works

Cross-namespace:
  curl http://my-service           ❌ won't work
  curl http://my-service.dev       ❌ won't work  
  curl http://my-service.dev.svc.cluster.local   ✅ works!

Full DNS format:
  <service-name>.<namespace>.svc.cluster.local
```

---

## 🔄 The 5 Models — Quick Summary

| Model | The Core Idea | The Analogy |
|-------|-------------|-------------|
| **Declarative Objects** | Tell K8s WHAT, not HOW. spec = desire, status = reality | Restaurant order, not cooking yourself |
| **Labels & Selectors** | Objects find each other via tags, not hardcoded names | Employee badge + department memo |
| **Owner References** | Objects form a hierarchy; parents manage children's lifecycle | Corporate org chart |
| **Cattle Not Pets** | Nodes are disposable; all state is elsewhere | Hotel room, not your home |
| **Namespace Scope** | Soft walls for naming, RBAC, and quotas — not security perimeters | Floors in an office building |

---

## 🧪 Test Yourself

1. You `kubectl apply` the same Deployment YAML twice. What happens? (Think: declarative) : nothing
2. A Service is created but `kubectl get endpoints my-service` shows `<none>`. What's wrong?  labels not set properly
3. You `kubectl delete pod my-pod`. 10 seconds later it's back. Why? How do you permanently delete it?, declare it on the yaml file
4. A developer says "I stored the config file directly on the node at `/etc/myapp/config.json`." What's the problem with this? not maintainable, pods are ephemeral
5. You have a pod in namespace `dev` that needs to call a service in namespace `prod`. What URL does it use? : my-service.prod.svc.cluster.local
6. Why can't you have two pods named "nginx" in the same namespace? Can you have them in different namespaces? : no, because namespace scoped and naming should be unique , different name space we can have

