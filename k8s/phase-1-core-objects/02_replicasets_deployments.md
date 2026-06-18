# 02 — ReplicaSets & Deployments

> **The point of this file:** You will almost never create a ReplicaSet directly. You create Deployments, which create ReplicaSets, which create Pods. But you need to understand all three layers to debug production issues.

---

## 🔁 The Problem ReplicaSets Solve

In Phase 0, you learned that if you just create a raw Pod and it dies — it stays dead. There's nothing to bring it back. K8s created the object, kubelet ran the container, and when the container died, K8s just noted the failure. That's it.

```
Raw Pod lifecycle:
  kubectl apply -f pod.yaml → Pod starts → Container crashes → Pod stays dead ❌

ReplicaSet lifecycle:
  ReplicaSet declares "I need 3 pods" → 3 Pods start
  → Pod #2 crashes → ReplicaSet notices count = 2, needs 3 → Creates Pod #2b ✅
```

**The ReplicaSet is the self-healing mechanism.**

---

## 🧩 ReplicaSet — The Self-Healing Layer

A ReplicaSet (RS) ensures that a specified number of pod "replicas" are running at any given time.

```
┌─────────────────────────────────────────────────────────┐
│                     ReplicaSet                          │
│                                                         │
│  spec:                                                  │
│    replicas: 3          ← "I want 3 pods"               │
│    selector:            ← "I own pods matching this"    │
│      matchLabels:                                       │
│        app: web                                         │
│    template:            ← "Pods should look like this"  │
│      (pod spec goes here)                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
                │ owns (via label selector)
      ┌─────────┼─────────┐
      ▼         ▼         ▼
  ┌───────┐ ┌───────┐ ┌───────┐
  │ Pod 1 │ │ Pod 2 │ │ Pod 3 │
  │ app=web│ │ app=web│ │ app=web│
  └───────┘ └───────┘ └───────┘
```

**The Reconciliation Loop for ReplicaSet:**
```
Every few seconds:
  Actual pod count = count pods matching selector
  Desired count = spec.replicas
  
  If actual < desired:
    Create (desired - actual) new pods from template
    
  If actual > desired:
    Delete (actual - desired) pods
    
  If actual == desired:
    Do nothing
```

### The Selector is Critical

The RS finds its pods via a **label selector** — not by name or any other link. This has an important implication:

> ⚠️ **If you manually create a pod with the same labels as an RS is watching, the RS will "adopt" it and may delete it to stay at the desired count!**

```bash
# RS wants 3 pods with label app=web
# You manually create: kubectl run extra-pod --image=nginx -l app=web
# Result: RS sees 4 pods, deletes 1 to get back to 3
# Your manually-created pod might be the one deleted!
```

---

## 🚀 Deployments — The Production Layer

A **Deployment** is a higher-level abstraction that manages ReplicaSets. It adds two crucial features:

1. **Rolling updates** — update pods gradually with zero downtime
2. **Rollback** — undo an update instantly if something goes wrong

```
Deployment "web-app"
    │
    │ manages (owns)
    ├──── ReplicaSet "web-app-abc123" (OLD — 0 pods)
    │
    └──── ReplicaSet "web-app-def456" (NEW — 3 pods ✅)
    
    During a rolling update, BOTH ReplicaSets exist!
    Old RS scales down as New RS scales up.
```

### Why Deployments Create Multiple ReplicaSets

When you update a Deployment (e.g., change the image), K8s does NOT modify the existing ReplicaSet. Instead:
1. Creates a NEW ReplicaSet with the new pod template
2. Scales UP the new RS
3. Scales DOWN the old RS
4. When rollout is complete, old RS stays at 0 replicas (kept for rollback!)

```
Before update:
  RS-v1 (3 pods)     RS-v2 (0 pods)

During rolling update (step by step):
  RS-v1 (2 pods)     RS-v2 (1 pod)   ← New pod comes up
  RS-v1 (1 pod)      RS-v2 (2 pods)  ← Old pod goes down
  RS-v1 (0 pods)     RS-v2 (3 pods)  ← Update complete

After update (RS-v1 kept for rollback):
  RS-v1 (0 pods)     RS-v2 (3 pods) ✅
  
Rollback (kubectl rollout undo):
  RS-v1 (3 pods)     RS-v2 (0 pods) ← RS-v1 scales back up!
```

> **Analogy:** A Deployment is like a **project manager** who delegates all actual work to a team lead (ReplicaSet), who then assigns it to workers (Pods).  
> When the project manager wants to change the work process (update image), they hire a new team lead with the new process, gradually transfer workers from old team to new team, and keep the old team lead on retainer (0 pods but RS preserved) in case they need to reverse the change.

---

## 📄 Deployment YAML — Fully Annotated

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: default
  labels:
    app: web-app           # Labels on the Deployment itself
spec:
  replicas: 3              # ← How many pods to maintain

  selector:                # ← Which pods does THIS Deployment own?
    matchLabels:
      app: web-app         # Must match template.metadata.labels!

  strategy:
    type: RollingUpdate    # The default. Alternative: Recreate
    rollingUpdate:
      maxSurge: 1          # Max EXTRA pods above desired (can be %)
      maxUnavailable: 0    # Max pods that can be down during update (0 = zero downtime!)

  # ─── REVISION HISTORY ─────────────────────────────────────
  revisionHistoryLimit: 5  # How many old ReplicaSets to keep (for rollback)
  # ──────────────────────────────────────────────────────────

  template:                # ← Pod template (EVERYTHING below here is a Pod spec)
    metadata:
      labels:
        app: web-app       # These labels MUST match the selector above!
        version: v1

    spec:
      containers:
      - name: nginx
        image: nginx:1.24  # We'll update this to 1.25 in the lab
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## 🔄 Rolling Update Strategies Explained

### `RollingUpdate` (Default) — Zero Downtime

```
spec.strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1          # Can go UP to desired+1 pods during update
    maxUnavailable: 0    # Always keep ALL desired pods running
```

Timeline with 3 replicas, maxSurge=1, maxUnavailable=0:

```
Time 0: [v1][v1][v1]              ← 3 pods, all v1
Time 1: [v1][v1][v1][v2]         ← New v2 pod created (surge=1, total=4)
Time 2: [v1][v1][v2]             ← v2 is ready, one v1 terminated (back to 3)
Time 3: [v1][v1][v2][v2]         ← Another v2 pod created
Time 4: [v1][v2][v2]             ← v2 ready, another v1 down
Time 5: [v1][v2][v2][v2]         ← Last v2 created
Time 6: [v2][v2][v2]             ← Last v1 down. Done! ✅
```

### `Recreate` — Downtime Guaranteed

```
spec.strategy:
  type: Recreate
```

```
Time 0: [v1][v1][v1]             ← All old pods
Time 1: [][][][]                  ← ALL old pods deleted (DOWNTIME STARTS)
Time 2: [v2][v2][v2]             ← All new pods created (DOWNTIME ENDS)
```

**Use Recreate when:** App cannot run two versions simultaneously (e.g., it holds exclusive DB locks, or the DB schema change breaks the old version).

---

## 🕹️ Deployment Commands — The Full Toolkit

```bash
# ─── CREATE ────────────────────────────────────────────────
kubectl create deployment web-app --image=nginx:1.24 --replicas=3

# ─── UPDATE ────────────────────────────────────────────────
# Method 1: Update image directly (fastest)
kubectl set image deployment/web-app nginx=nginx:1.25

# Method 2: Edit the Deployment live
kubectl edit deployment web-app
# (opens $EDITOR with the full YAML — change image tag and save)

# Method 3: Apply updated YAML
kubectl apply -f deployment.yaml

# ─── WATCH THE ROLLOUT ─────────────────────────────────────
kubectl rollout status deployment/web-app
# Output: Waiting for deployment "web-app" rollout to finish: 1 of 3 updated...
#         deployment "web-app" successfully rolled out

# ─── HISTORY ───────────────────────────────────────────────
kubectl rollout history deployment/web-app
# REVISION  CHANGE-CAUSE
# 1         <none>
# 2         <none>

# To track WHAT changed (add --record flag or use --revision)
kubectl set image deployment/web-app nginx=nginx:1.25 --record
kubectl rollout history deployment/web-app --revision=2

# ─── ROLLBACK ──────────────────────────────────────────────
kubectl rollout undo deployment/web-app              # Roll back to previous
kubectl rollout undo deployment/web-app --to-revision=1  # Roll back to specific revision

# ─── PAUSE / RESUME (batch multiple changes) ───────────────
kubectl rollout pause deployment/web-app
kubectl set image deployment/web-app nginx=nginx:1.25
kubectl set resources deployment/web-app -c nginx --limits=cpu=500m,memory=256Mi
kubectl rollout resume deployment/web-app
# Only ONE rollout happens with ALL changes applied at once

# ─── SCALE ─────────────────────────────────────────────────
kubectl scale deployment web-app --replicas=5

# ─── DELETE ────────────────────────────────────────────────
kubectl delete deployment web-app
# This cascades: Deployment → ReplicaSets → Pods (all deleted)
```

---

## 🔍 Understanding the Relationship — Inspect It Live

```bash
# 1. Create a deployment
kubectl create deployment web-app --image=nginx:1.24 --replicas=3

# 2. See all three layers
kubectl get deployments
kubectl get replicasets
kubectl get pods

# 3. Check ownership — look at ownerReferences
kubectl get replicaset -o yaml | grep -A5 ownerReferences
kubectl get pod <pod-name> -o yaml | grep -A5 ownerReferences

# 4. Update and watch the new ReplicaSet appear
kubectl set image deployment/web-app nginx=nginx:1.25
kubectl get replicasets    # You'll see TWO ReplicaSets now!
kubectl rollout status deployment/web-app

# 5. After rollout: old RS is at 0 replicas, new RS has 3
kubectl get replicasets
# NAME                   DESIRED   CURRENT   READY   AGE
# web-app-abc123         0         0         0       5m    ← Old RS (kept for rollback)
# web-app-def456         3         3         3       1m    ← Current RS
```

---

## ⚡ Other Workload Controllers (Brief Overview)

You won't go deep on these yet, but know they exist:

| Controller | Use Case | Key Difference |
|-----------|---------|---------------|
| **DaemonSet** | Run exactly one pod per node | Log collectors, monitoring agents, CNI plugins |
| **StatefulSet** | Stateful apps (DBs) | Stable pod names, ordered scaling, per-pod PVC |
| **Job** | Run to completion | Exits when done; tracks completions |
| **CronJob** | Scheduled tasks | Creates Jobs on a cron schedule |

---

## 🧪 Test Yourself

1. **You have a Deployment with 3 replicas. You delete one pod manually. What happens within 30 seconds?** (Be specific about which component acts and how.) it comes back due to deployment controller.

2. **What is the difference between a ReplicaSet and a Deployment?** Which one would you create in production, and why? deployment is a abstraction  over replicaset, it provides rollingupdates and rollback

3. **After a rolling update, you notice a bug in the new version. What single command do you run to instantly revert?**kubectl rollout undo deployment/web-app --to-revision=1

4. **Your Deployment has `maxUnavailable: 0` and `maxSurge: 1`. You have 5 replicas. Walk through what happens during an update.** we get the 6th pod as extra one and when it is ready the first pod is deleted

5. **Why does K8s keep old ReplicaSets around at 0 replicas after a rollout completes?**for backup

6. **`kubectl rollout status deployment/web-app` hangs indefinitely. What might be wrong?** (Hint: think about what could prevent new pods from becoming Ready) oom issues? im not sure

7. **What's the difference between `kubectl delete pod <pod>` and `kubectl delete deployment <deployment>`?** Which one permanently removes the workload? delete deployment permanently removes. delete pod only removes that specific pod. deployement controller will create a new pod to replace it.

8. **When would you use `strategy.type: Recreate` instead of `RollingUpdate`?** when the application cannot run two versions simultaneously
