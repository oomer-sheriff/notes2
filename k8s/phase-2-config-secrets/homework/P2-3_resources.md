# Homework P2-3 — Resource Management & OOM Lab

> **Time:** 1.5 hours  
> **Goal:** Set resource requests/limits, trigger an OOMKill deliberately, use `kubectl top` to observe real usage, and see QoS classes in action.

---

## 🚀 Setup

```powershell
# First, make sure metrics-server is running (from Phase 0 setup)
kubectl top nodes
# If this errors, apply metrics-server:
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' `
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
# Wait ~60 seconds before kubectl top works

kubectl create namespace lab-res
kubectl config set-context --current --namespace=lab-res
```

---

## Part 1 — QoS Class Inspection (20 min)

### Task 1.1 — Create All Three QoS Class Pods

```yaml
# Save as lab-files/qos-pods.yaml
---
# Pod 1: Guaranteed (requests == limits, both set, for all containers)
apiVersion: v1
kind: Pod
metadata:
  name: guaranteed-pod
  namespace: lab-res
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'sleep 3600']
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "64Mi"    # Same as requests = Guaranteed
        cpu: "100m"       # Same as requests = Guaranteed
---
# Pod 2: Burstable (requests != limits)
apiVersion: v1
kind: Pod
metadata:
  name: burstable-pod
  namespace: lab-res
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'sleep 3600']
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "256Mi"   # Limits > requests = Burstable
        cpu: "500m"
---
# Pod 3: BestEffort (no resources at all)
apiVersion: v1
kind: Pod
metadata:
  name: besteffort-pod
  namespace: lab-res
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'sleep 3600']
    # No resources block = BestEffort
```

```powershell
kubectl apply -f lab-files/qos-pods.yaml

# Wait for all 3 to be Running
kubectl get pods -n lab-res

# Check QoS class for each pod
kubectl get pod guaranteed-pod -n lab-res -o jsonpath='{.status.qosClass}'; echo
kubectl get pod burstable-pod -n lab-res -o jsonpath='{.status.qosClass}'; echo
kubectl get pod besteffort-pod -n lab-res -o jsonpath='{.status.qosClass}'; echo
```

**Fill in the table:**

| Pod Name | Expected QoS | Actual QoS (from output) | Eviction Priority |
|----------|-------------|--------------------------|------------------|
| guaranteed-pod | Guaranteed | | Last |
| burstable-pod | Burstable | | Middle |
| besteffort-pod | BestEffort | | First |

---

## Part 2 — Trigger an OOMKill (30 min)

This is one of those things you MUST have seen to understand fully.

### Task 2.1 — Build the OOM Scenario

```yaml
# Save as lab-files/oom-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: oom-demo
  namespace: lab-res
spec:
  containers:
  - name: memory-eater
    image: polinux/stress
    command: ['stress']
    args:
    - '--vm'
    - '1'
    - '--vm-bytes'
    - '200M'      # Try to allocate 200MB
    - '--vm-hang'
    - '1'
    resources:
      requests:
        memory: "50Mi"
        cpu: "100m"
      limits:
        memory: "100Mi"   # ← LIMIT: 100MB. App tries 200MB → OOMKilled!
        cpu: "200m"
```

```powershell
kubectl apply -f lab-files/oom-pod.yaml

# Watch the pod — it will start, get OOMKilled, restart, repeat
kubectl get pods -n lab-res -w
# Look for: STATUS cycling between OOMKilled → CrashLoopBackOff → Running
# (Ctrl+C after you see at least one OOMKilled event)
```

---

### Task 2.2 — Read the OOM Evidence

```powershell
# See the restart count and last state
kubectl describe pod oom-demo -n lab-res
# Look for:
# - Restart Count: (should be > 0)
# - Last State → Reason: OOMKilled
# - Exit Code: 137 (SIGKILL = 128 + 9)
```

**Fill in from `kubectl describe`:**

| Field | Value |
|-------|-------|
| Restart Count | |
| Last State Reason | |
| Last State Exit Code | |
| Container State (current) | |

---

### Task 2.3 — Fix the OOMKill

```powershell
# Option 1: Increase the memory limit
kubectl patch pod oom-demo -n lab-res \
  --type='json' \
  -p='[{"op":"replace","path":"/spec/containers/0/resources/limits/memory","value":"300Mi"}]'

# Note: Patching a pod spec directly requires pod recreation for some fields
# Better approach: delete and recreate with fixed YAML

kubectl delete pod oom-demo -n lab-res

# Edit the YAML: change limits.memory from 100Mi to 300Mi
# Then reapply:
# kubectl apply -f lab-files/oom-pod.yaml

# The pod should now stay Running
kubectl get pod oom-demo -n lab-res -w
```

---

## Part 3 — CPU Throttling (Not OOMKill) (20 min)

### Task 3.1 — See CPU Throttling in Action

CPU limits throttle (slow down) but don't kill. Let's see this:

```yaml
# Save as lab-files/cpu-throttle.yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-demo
  namespace: lab-res
spec:
  containers:
  - name: cpu-burner
    image: polinux/stress
    command: ['stress']
    args: ['--cpu', '4', '--timeout', '120']   # Try to use 4 CPUs!
    resources:
      requests:
        memory: "32Mi"
        cpu: "100m"
      limits:
        memory: "64Mi"
        cpu: "200m"     # Hard cap: 0.2 CPU. App wants 4 CPU.
```

```powershell
kubectl apply -f lab-files/cpu-throttle.yaml

# Wait ~10 seconds for it to start, then check actual CPU usage
kubectl top pod cpu-demo -n lab-res
# Expected: actual CPU is capped near 200m, NOT the 4000m the app wants

# The pod should stay Running (not restarted) — CPU throttling doesn't kill
kubectl get pod cpu-demo -n lab-res
```

**Key observation:** The pod stays `Running` despite trying to use far more CPU than its limit. CPU throttling is gentle — just slower. Memory limits are brutal — immediate kill.

---

## Part 4 — Real-World Sizing (20 min)

### Task 4.1 — Measure an Actual Workload

```yaml
# Deploy a real nginx with some config
# Save as lab-files/measure-nginx.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-measure
  namespace: lab-res
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx-measure
  template:
    metadata:
      labels:
        app: nginx-measure
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "32Mi"     # Start low — we'll observe real usage
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "200m"
```

```powershell
kubectl apply -f lab-files/measure-nginx.yaml
kubectl expose deployment nginx-measure --port=80 -n lab-res

# Generate some traffic
kubectl run load-gen --image=busybox --restart=Never -n lab-res \
  -- sh -c 'for i in $(seq 1 100); do wget -q -O- http://nginx-measure; done'

# Measure actual usage
kubectl top pods -n lab-res
kubectl top pods -n lab-res --containers
```

**Fill in:**

| Pod | CPU (actual) | Memory (actual) | CPU Request | Memory Request |
|-----|-------------|----------------|-------------|---------------|
| nginx-measure-* (pod 1) | | | 50m | 32Mi |
| nginx-measure-* (pod 2) | | | 50m | 32Mi |

**Based on what you measured, what would you set for requests and limits in production?**
```
requests.cpu: 
requests.memory: 
limits.cpu: 
limits.memory: 

Reasoning:
```

---

## 🧹 Cleanup

```powershell
kubectl delete namespace lab-res
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] QoS class table filled in (confirmed via jsonpath)
- [ ] OOMKill triggered and evidence read from `describe`
- [ ] OOM fixed by increasing memory limit
- [ ] CPU throttle tested — pod stays Running despite exceeding CPU want
- [ ] Nginx measurement done and sizing recommendation written

## 📝 Reflection

**In your own words: why is OOMKill more disruptive than CPU throttling?**
```

```

**A Java application is OOMKilled repeatedly. Before increasing the memory limit, what should you investigate first?**
```

```
