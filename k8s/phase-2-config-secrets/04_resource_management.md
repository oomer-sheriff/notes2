# 04 — Resource Management In Depth

> **Why this matters:** Incorrect resource settings are the #1 cause of production incidents in K8s clusters. Either pods get OOMKilled (limits too low), or nodes get over-committed and become unstable (no limits at all). Getting this right is a core operations skill.

---

## 🔁 Quick Recap — Requests vs Limits

You saw this in Phase 1 but let's go deeper:

```
CPU and Memory have TWO settings each:

REQUESTS                    LIMITS
(Scheduler sees this)       (Kubelet enforces this)
"Reserve this much"         "Never exceed this much"

requests.cpu = 250m    →    limits.cpu = 500m
                            |           |
                        throttled    allowed
                        at 250m     up to 500m
                        (actually   (beyond = throttled
                        no, free    NOT killed)
                        to burst
                        if node
                        has spare)

requests.memory = 128Mi →   limits.memory = 256Mi
                            |              |
                        reserved       hard cap
                        but can        (OOMKilled
                        use more       if exceeded!)
```

### The Key Asymmetry: CPU vs Memory

| | CPU | Memory |
|--|-----|--------|
| Exceeds **request** | Can use more if node has free CPU | Can use more if node has free RAM |
| Exceeds **limit** | **Throttled** (slowed down, not killed) | **OOMKilled** (process killed immediately) |
| Recovery | Automatic (throttle lifts when load drops) | K8s restarts the container |

> **Why the asymmetry?**  
> CPU is a **compressible** resource — you can slow a process down without crashing it.  
> Memory is **incompressible** — a process can't "give back" memory it's already allocated. If it needs 300Mi but only has 256Mi, there's no graceful option. The OS kills it.

---

## 🎖️ QoS Classes — The Three Tiers

Kubernetes automatically assigns every pod to a **Quality of Service (QoS) class** based on its resource settings. This class determines eviction priority when a node runs low on resources.

### Class 1: Guaranteed (Best Protection)

**Rule:** Every container in the pod must have requests == limits for BOTH cpu AND memory.

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "500m"
  limits:
    memory: "256Mi"    # ← MUST equal requests
    cpu: "500m"        # ← MUST equal requests
```

```
    ┌─────────────────────────────────────────────┐
    │          GUARANTEED POD                     │
    │  - First to get resources                   │
    │  - LAST to be evicted (only evicted if      │
    │    it exceeds its own limits)               │
    │  - Most predictable performance             │
    └─────────────────────────────────────────────┘
```

**Use for:** Latency-sensitive production workloads (APIs, databases), anything that CANNOT be interrupted.

> **Analogy:** A **first-class airline ticket** — guaranteed seat, guaranteed overhead bin, guaranteed boarding first. The airline can't give your seat to someone else.

---

### Class 2: Burstable (Middle Ground)

**Rule:** At least one container has requests < limits (or has only requests, no limits, or only limits).

```yaml
resources:
  requests:
    memory: "128Mi"    # ← requests LESS THAN limits
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

```
    ┌─────────────────────────────────────────────┐
    │          BURSTABLE POD                      │
    │  - Gets guaranteed its requests             │
    │  - Can burst above requests if node has     │
    │    spare capacity                           │
    │  - Evicted when it exceeds requests and     │
    │    the node needs resources back            │
    └─────────────────────────────────────────────┘
```

**Use for:** Most typical workloads — web apps, background workers, services with variable load.

> **Analogy:** A **premium economy ticket** — better than basic, you have a reserved seat, but in an emergency the airline might ask you to give it up for a higher-priority passenger.

---

### Class 3: BestEffort (Lowest Priority)

**Rule:** Pod has NO resource requests OR limits at all.

```yaml
# Container with no resources block at all = BestEffort
containers:
- name: my-app
  image: my-app:latest
  # No resources: field!
```

```
    ┌─────────────────────────────────────────────┐
    │          BESTEFFORT POD                     │
    │  - First to be evicted under pressure       │
    │  - Can use whatever's available on the node │
    │  - No scheduling guarantees                 │
    │  - Scheduler places them freely             │
    └─────────────────────────────────────────────┘
```

**Use for:** Non-critical batch jobs, experimental workloads, dev namespaces where you don't care if pods die.

> **Analogy:** A **standby passenger** — you get on the plane only if there's a spare seat. If the plane fills up, you don't fly.

### QoS Eviction Order Under Node Pressure

```
Node runs low on memory:
  1. Evict BestEffort pods (no requests at all) — first to go
  2. Evict Burstable pods that are OVER their requests
  3. Evict Burstable pods that are AT their requests
  4. Evict Guaranteed pods (only if they exceed their own limits)
```

---

## ⚖️ Requests vs Limits — The Over-Commitment Model

One of Kubernetes's most powerful features — and biggest footguns — is **over-commitment**.

```
Node has: 4000m CPU, 8Gi RAM

Three pods with these requests:
  Pod A: request 1000m CPU, 2Gi RAM
  Pod B: request 1000m CPU, 2Gi RAM
  Pod C: request 1000m CPU, 2Gi RAM
  Total requests: 3000m, 6Gi   ← Fits on node ✅

But their limits are:
  Pod A: limit  2000m CPU, 4Gi RAM
  Pod B: limit  2000m CPU, 4Gi RAM
  Pod C: limit  2000m CPU, 4Gi RAM
  Total limits:  6000m CPU, 12Gi RAM  ← Exceeds node capacity!
```

**This is intentional.** K8s assumes not all pods will burst to their limits simultaneously. Like an airline overbooking flights, it works fine most of the time. But when everyone bursts simultaneously (traffic spike), pods get throttled (CPU) or OOMKilled (memory).

> **The key principle:** Set `requests` based on what your app typically uses. Set `limits` based on the maximum you'd ever allow it to consume. Don't set them the same unless you need Guaranteed QoS.

---

## 🔬 How to Right-Size Resource Requests

Don't guess. Measure.

### Step 1: Deploy with No Limits (Temporarily)

```yaml
resources:
  requests:
    memory: "64Mi"    # Small starting guess
    cpu: "100m"
  # No limits yet
```

### Step 2: Generate Real Load and Measure

```bash
# Install metrics-server first (patch for kind):
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment metrics-server -n kube-system --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

# See actual CPU/memory usage
kubectl top pods
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu

# Detailed metrics
kubectl top pods --containers    # Per-container breakdown
```

### Step 3: Use Observed Values to Set Requests

```
Observed peak CPU: 180m
Observed peak Memory: 210Mi

Set:
  requests.cpu: 200m        (slightly above peak to avoid throttle)
  requests.memory: 256Mi    (round up, above observed peak)
  limits.cpu: 500m          (2.5x request — room to burst)
  limits.memory: 512Mi      (2x request — reasonable burst budget)
```

### Step 4: Watch for OOMKills

```bash
# Check if any pods have been OOMKilled
kubectl get pods -o json | \
  python -c "import json,sys; pods=json.load(sys.stdin)['items'];
  [print(p['metadata']['name'],c['state']) 
   for p in pods 
   for c in p.get('status',{}).get('containerStatuses',[]) 
   if c.get('state',{}).get('terminated',{}).get('reason')=='OOMKilled']"

# Simpler: just describe pods and grep
kubectl describe pods | grep -A5 "OOMKilled\|Last State"
```

---

## 📊 Resource Units — The Notation

```
CPU:
  1000m  = 1 full CPU core
  500m   = half a core
  250m   = quarter core
  100m   = 10% of one core  (typical small service)
  2      = 2 cores (can write without "m")
  0.5    = 0.5 cores (decimal also works)

Memory:
  128Mi  = 128 mebibytes (1 MiB = 1,048,576 bytes)
  256Mi  = 256 mebibytes
  1Gi    = 1 gibibyte (1 GiB = 1,073,741,824 bytes)
  1G     = 1 gigabyte (1 GB = 1,000,000,000 bytes)
  
  ⚠️ 1Gi ≠ 1G — use Mi and Gi to avoid confusion!
  
  Common sizes:
  64Mi   → very small utility containers
  128Mi  → small single-purpose services
  256Mi  → typical web service
  512Mi  → medium app (Node.js, Go)
  1Gi    → Java app, ML model serving
  4Gi+   → databases, big data workloads
```

---

## 🚦 Namespace-Level Defaults — LimitRange Revisited

In Phase 1 you briefly saw LimitRange. Here's why it matters for resource management:

```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: dev
spec:
  limits:
  - type: Container
    default:              # Containers get these limits if none specified
      cpu: "200m"
      memory: "256Mi"
    defaultRequest:       # Containers get these requests if none specified
      cpu: "100m"
      memory: "128Mi"
    max:                  # No container can exceed this
      cpu: "2"
      memory: "2Gi"
    min:                  # No container can go below this
      cpu: "10m"
      memory: "32Mi"
  - type: Pod
    max:                  # Total for ALL containers in one pod
      cpu: "4"
      memory: "4Gi"
```

**Once a LimitRange is set:**
```
Pod spec has no resources? → LimitRange default values are applied
Pod spec exceeds max? → Rejected (admission error)
Pod spec below min? → Rejected

This means:
  - No pod can starve the namespace with 0 requests
  - No pod can consume more than the LimitRange max
  - All pods automatically get QoS class "Burstable" or better
```

---

## 🧪 Test Yourself

1. **What is the QoS class of a pod where all containers have `requests == limits`?** When is this pod evicted? guaranteed, and its evicted last

2. **Your pod has `limits.memory: 512Mi`. The app allocates 600Mi. What happens?** What does the container exit code look like in `kubectl describe pod`? It will get killed, and its exit code will be 137.

3. **Your pod has `limits.cpu: 500m`. The app needs 700m of CPU to process a request. What happens?** Does the pod die? it will be throttled and the request will be rejected, slows down but not dead.

4. **A pod has no resource spec at all. What QoS class does it get? When is it evicted relative to a Burstable pod?** bestEffort, and its evicted first

5. **You have a Java Spring Boot application. You observe it using 180m CPU and 350Mi RAM during load testing. Set appropriate requests and limits (with reasoning).** set 180m abd 350i requests, but limits should be higher based on burst if you want it to burst higher, like 250m and 512Mi

6. **What is the difference between `1Gi` and `1G` in a resource spec?** Why does this matter? 1Gi = 1024 * 1024 * 1024 bytes. 1G = 1,000,000,000 bytes. They are different, but for most workloads it doesn't matter.

7. **A namespace has a ResourceQuota of `limits.memory: 4Gi`. You have 3 pods each requesting 1Gi. You try to create a 4th pod requesting 2Gi. What happens?** What if the 4th pod requests 1Gi? admission error baby! on the 2 gi one, and no error on the 1 gi one.

8. **`kubectl top pods` shows your pod is using 400m CPU but its limit is 500m. Should you be worried?** At what percentage of limit should you be concerned? It depends on the application, but generally you should be concerned if your pod is using more than 80% of its limit for a sustained period of time. 
