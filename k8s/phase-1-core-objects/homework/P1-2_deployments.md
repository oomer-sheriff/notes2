# Homework P1-2 — Deployments, Rolling Updates & Rollbacks

> **Time:** 2 hours  
> **Goal:** Build muscle memory around the full Deployment lifecycle — create, scale, update, rollback, and understand what's happening at each step.

---

## 🚀 Setup

```powershell
kubectl create namespace lab2
kubectl config set-context --current --namespace=lab2
```

---

## Part 1 — Create and Inspect the Deployment Hierarchy (30 min)

### Task 1.1 — Create Your Deployment

Save as `lab-files/web-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: lab2
  labels:
    app: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app      # MUST match template.metadata.labels
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  revisionHistoryLimit: 5
  template:
    metadata:
      labels:
        app: web-app    # MUST match selector.matchLabels
        version: v1
    spec:
      containers:
      - name: nginx
        image: nginx:1.24   # Deliberately OLD version — we'll update it
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

```powershell
kubectl apply -f lab-files/web-deployment.yaml

# Watch all three layers come up
kubectl get pods -n lab2 -w
# Wait until 3/3 pods are Running/Ready, then Ctrl+C
```

---

### Task 1.2 — Inspect the Three-Layer Hierarchy

```powershell
# Layer 1: The Deployment
kubectl get deployment web-app -n lab2
kubectl describe deployment web-app -n lab2   # Note: Selector, Replicas, Strategy

# Layer 2: The ReplicaSet (K8s auto-created this)
kubectl get replicasets -n lab2
# Note the NAME — it will be web-app-<hash>

# Layer 3: The Pods (created by the ReplicaSet)
kubectl get pods -n lab2 --show-labels
# Note: each pod has app=web-app AND a pod-template-hash label

# See the ownership chain
kubectl get replicaset -n lab2 -o yaml | grep -A8 ownerReferences
kubectl get pods -n lab2 -o yaml | grep -A8 ownerReferences
```

**Fill in:**

| Question | Answer |
|----------|--------|
| What is the ReplicaSet's name? | |
| What hash is appended to each pod name? | |
| Who owns the ReplicaSet? (from ownerReferences) | |
| Who owns the Pods? | |

---

### Task 1.3 — Self-Healing Demo

```powershell
# See all 3 pods
kubectl get pods -n lab2

# Delete one pod manually
POD=$(kubectl get pods -n lab2 -o jsonpath='{.items[0].metadata.name}')
kubectl delete pod $POD -n lab2

# Watch it immediately be recreated
kubectl get pods -n lab2 -w
```

**Question:** How long did it take for the replacement pod to appear? What component created it?

---

## Part 2 — Rolling Update (45 min)

### Task 2.1 — Perform a Rolling Update

```powershell
# Check current image
kubectl get deployment web-app -n lab2 -o jsonpath='{.spec.template.spec.containers[0].image}'
echo ""

# Open a SECOND terminal and run this watcher BEFORE updating:
kubectl get pods -n lab2 -w

# In your FIRST terminal, trigger the update:
kubectl set image deployment/web-app nginx=nginx:1.25 -n lab2

# Watch the rolling update happen in real time in the second terminal
# You should see:
# - New pods (1.25) being created
# - Old pods (1.24) being terminated
# - Brief period with 4 pods (surge=1)
```

**Fill in while watching:**

| Observation | What You Saw |
|-------------|-------------|
| Max pods at any one time during update | |
| Time for full rollout (note start and end time) | |
| Were there ever 0 running pods? (expected: No, maxUnavailable=0) | |

---

### Task 2.2 — Check Rollout Status

```powershell
# Check rollout status (do this DURING an update)
kubectl rollout status deployment/web-app -n lab2

# Check rollout history
kubectl rollout history deployment/web-app -n lab2

# Inspect revision 1 vs revision 2
kubectl rollout history deployment/web-app -n lab2 --revision=1
kubectl rollout history deployment/web-app -n lab2 --revision=2
```

**Observe:** Notice there are now TWO ReplicaSets:

```powershell
kubectl get replicasets -n lab2
# You should see:
# web-app-abc123    3   3   3    (new, has the pods)
# web-app-def456    0   0   0    (old, kept at 0 for rollback)
```

---

### Task 2.3 — Rollback

```powershell
# Simulate a bad deploy — update to a broken image
kubectl set image deployment/web-app nginx=nginx:DOESNOTEXIST -n lab2

# Watch what happens
kubectl get pods -n lab2 -w
kubectl rollout status deployment/web-app -n lab2

# See the ImagePullBackOff
kubectl describe pod -n lab2 -l app=web-app | grep -A10 Events

# ROLLBACK!
kubectl rollout undo deployment/web-app -n lab2

# Watch recovery
kubectl get pods -n lab2 -w
kubectl rollout status deployment/web-app -n lab2

# Check history again — notice revision 4 now
kubectl rollout history deployment/web-app -n lab2
```

**Key observation:** Notice how quickly the rollback happens compared to the original deploy. The old ReplicaSet was just scaled back up — no image pull needed!

---

### Task 2.4 — Scale the Deployment

```powershell
# Scale up
kubectl scale deployment web-app --replicas=6 -n lab2
kubectl get pods -n lab2 -w

# Scale down
kubectl scale deployment web-app --replicas=2 -n lab2
kubectl get pods -n lab2 -w

# Patch directly (another way to change replicas)
kubectl patch deployment web-app -p '{"spec":{"replicas":3}}' -n lab2
```

---

## Part 3 — The Recreate Strategy Comparison (20 min)

### Task 3.1 — Watch the Difference

```powershell
# Create a second deployment with Recreate strategy
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app-recreate
  namespace: lab2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app-recreate
  strategy:
    type: Recreate
  template:
    metadata:
      labels:
        app: web-app-recreate
    spec:
      containers:
      - name: nginx
        image: nginx:1.24
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"
EOF

# Watch in one terminal:
kubectl get pods -l app=web-app-recreate -n lab2 -w

# In another terminal, update the image:
kubectl set image deployment/web-app-recreate nginx=nginx:1.25 -n lab2
```

**Observation:** Did all 3 old pods die BEFORE any new pod started? That's the downtime window with Recreate.

---

## Part 4 — Pause and Resume (Batch Multiple Changes) (15 min)

```powershell
# Pause the deployment (no rollout will trigger)
kubectl rollout pause deployment/web-app -n lab2

# Make multiple changes — none will trigger a rollout yet
kubectl set image deployment/web-app nginx=nginx:1.25 -n lab2
kubectl set resources deployment/web-app -c nginx \
  --limits=cpu=300m,memory=256Mi --requests=cpu=150m,memory=128Mi -n lab2

# Check: no rollout happening
kubectl rollout status deployment/web-app -n lab2
kubectl get pods -n lab2   # Still old pods

# Resume — ONE rollout with ALL changes applied
kubectl rollout resume deployment/web-app -n lab2
kubectl rollout status deployment/web-app -n lab2
```

---

## 🧹 Cleanup

```powershell
kubectl delete namespace lab2
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] Explored all 3 layers: Deployment → ReplicaSet → Pods
- [ ] Completed the ownership chain table
- [ ] Witnessed self-healing (deleted pod auto-recreated)
- [ ] Performed rolling update and watched pods cycle
- [ ] Intentionally triggered `ImagePullBackOff` and performed rollback
- [ ] Compared RollingUpdate vs Recreate downtime
- [ ] Used pause/resume for batched changes

---

## 📝 Reflection

**The command I'll use most in production:**
```

```

**What surprised me most about rolling updates:**
```

```

**Why is `revisionHistoryLimit` important?**
```

```
