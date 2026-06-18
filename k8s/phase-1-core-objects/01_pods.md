# 01 — Pods: The Atomic Unit of Kubernetes

> **The most important thing to get right in Phase 1.** Everything else — Deployments, StatefulSets, Jobs — is just "a controller that manages Pods." If you understand Pods deeply, the rest follows naturally.

---

## 🧬 What Is a Pod?

A **Pod** is the **smallest deployable unit in Kubernetes** — not a container.

This surprises people. Docker runs containers. But Kubernetes doesn't schedule containers — it schedules **Pods**, and each Pod contains one or more containers.

> **Why not just schedule containers directly?**  
> Because some workloads genuinely need multiple containers to work together as a single unit — sharing the same network interface, the same localhost, the same mounted volumes. A Pod is the wrapper that makes this co-location possible.

```
Without Pods (what you might expect):
  Node → Container A
  Node → Container B
  (A and B have separate IPs, can't share localhost)

With Pods (what K8s actually does):
  Node → Pod → [Container A] [Container B]
                  └──────── shared network ──────┘
                  └──────── shared volumes ───────┘
                  (A and B share localhost and volumes)
```

---

## 🌐 What Pods Share

All containers within a single Pod share:

```
┌────────────────────────────────────────────────────┐
│                        POD                         │
│                                                    │
│  ┌──────────────┐      ┌──────────────┐           │
│  │  Container A │      │  Container B │           │
│  │              │      │              │           │
│  │  port: 8080  │      │  port: 9090  │           │
│  └──────────────┘      └──────────────┘           │
│          │                     │                   │
│  ─────── Shared Network Namespace ─────────────   │
│          Single IP: 10.244.1.5                    │
│          localhost = localhost for ALL containers  │
│          (Container A can curl localhost:9090!)   │
│                                                    │
│  ─────── Shared Volumes ────────────────────────  │
│          /shared-data visible to both containers  │
└────────────────────────────────────────────────────┘
```

**What they do NOT share:**
- The filesystem (each container has its own unless you mount a volume)
- Processes (you can't `ps aux` in A and see B's processes)
- CPU/Memory limits (each container has its own)

> **Analogy:** A Pod is like a **shipping container on a cargo ship**.  
> Inside one shipping container, you might have multiple pallets (containers).  
> The pallets share the same physical space, the same temperature, the same destination.  
> But each pallet holds different goods (different apps).  
> The ship (node) carries many shipping containers (pods), each going to a different "slot."

---

## 🔄 Pod Lifecycle — States Explained

A pod moves through states as it's created, scheduled, and eventually terminated.

```
                    kubectl apply -f pod.yaml
                              │
                              ▼
                         ┌─────────┐
                         │ Pending │  ← Pod exists in etcd, not yet running
                         └────┬────┘
                              │  Scheduler assigns a node
                              │  kubelet pulls image
                              ▼
                    ┌──────────────────┐
                    │ ContainerCreating│  ← Image pulled, container starting
                    └────────┬─────────┘
                             │  Container starts successfully
                             ▼
                         ┌─────────┐
                         │ Running │  ← At least one container is running
                         └────┬────┘
                              │
              ┌───────────────┼──────────────────┐
              │               │                  │
              ▼               ▼                  ▼
        ┌──────────┐   ┌──────────────┐   ┌──────────┐
        │Succeeded │   │   Failed     │   │ Unknown  │
        │ (exit 0) │   │  (exit !=0)  │   │(node lost│
        └──────────┘   └──────┬───────┘   └──────────┘
                              │
                              ▼ (if restartPolicy: Always)
                    ┌─────────────────────┐
                    │  CrashLoopBackOff   │  ← Keeps failing, K8s backs off retries
                    └─────────────────────┘
```

**Detailed status values you'll see in the wild:**

| Status | Cause | How to Debug |
|--------|-------|-------------|
| `Pending` | No node has enough resources; node selector doesn't match | `kubectl describe pod` → Events |
| `ContainerCreating` | Pulling image; setting up volumes | `kubectl describe pod` → Events |
| `Running` | All good — at least one container is running | — |
| `CrashLoopBackOff` | Container exits non-zero repeatedly | `kubectl logs <pod> --previous` |
| `ImagePullBackOff` | Wrong image name, or private registry without auth | `kubectl describe pod` → Events |
| `OOMKilled` | Container exceeded memory limit | `kubectl describe pod` → look for `OOMKilled: true` |
| `Terminating` | Pod is being gracefully shut down | Wait for `terminationGracePeriodSeconds` (default 30s) |
| `Evicted` | Node ran out of memory/disk; K8s evicted lowest priority pods | `kubectl describe pod` → `Reason: Evicted` |
| `Unknown` | Node is unreachable; K8s doesn't know pod state | Check node health |

---

## ⏱️ Pod Restart Policies

The `restartPolicy` field controls what happens when a container exits:

```yaml
spec:
  restartPolicy: Always     # Default. Always restart. Good for web servers.
  # restartPolicy: OnFailure # Restart only if exit code != 0. Good for Jobs.
  # restartPolicy: Never     # Never restart. Good for one-off tasks.
```

| Policy | Container exits 0 | Container exits non-0 |
|--------|-------------------|----------------------|
| `Always` | Restart | Restart |
| `OnFailure` | Don't restart | Restart |
| `Never` | Don't restart | Don't restart |

> **Analogy:** Imagine a vending machine employee (container).  
> `Always` = If they finish work or quit, always hire a replacement immediately.  
> `OnFailure` = Only hire a replacement if they were fired (failed). If they retired cleanly (success), leave the slot empty.  
> `Never` = Run the task once; whether they succeed or fail, don't replace them.

---

## 🏗️ Multi-Container Pod Patterns

These are well-recognized design patterns used in production systems. They appear in CKAD exam questions.

### Pattern 1: Sidecar

A helper container that **extends** the main container's behavior without changing it.

```
┌────────────────────────────────────────────────────┐
│                        POD                         │
│                                                    │
│  ┌──────────────────┐   ┌──────────────────────┐  │
│  │   Main Container │   │  Sidecar Container   │  │
│  │   (nginx)        │   │  (log-shipper)       │  │
│  │                  │   │                      │  │
│  │  writes logs to  │   │  reads from          │  │
│  │  /var/log/nginx/ ├──►│  /var/log/nginx/     │  │
│  │                  │   │  ships to Elastic    │  │
│  └──────────────────┘   └──────────────────────┘  │
│          │                         │               │
│          └──── Shared Volume ───────┘              │
└────────────────────────────────────────────────────┘
```

**Real-world use:**
- Log shipping (Fluentd sidecar reads your app's logs and ships to Elasticsearch)
- Service mesh proxies (Istio injects an Envoy proxy sidecar to handle all network traffic)
- Config refreshers (sidecar watches Git and reloads app config when it changes)

> **Analogy:** A sidecar is like the **support crew** that follows a race car driver.  
> The driver (main app) focuses on racing (business logic).  
> The pit crew (sidecar) handles tires, fuel, telemetry — without changing how the car drives.

---

### Pattern 2: Init Containers

Containers that run **sequentially before** the main containers. The main containers only start after ALL init containers exit successfully.

```
┌────────────────────────────────────────────────────┐
│                        POD                         │
│                                                    │
│  Phase 1: INIT CONTAINERS (run to completion)      │
│  ┌──────────────────┐   ┌──────────────────────┐  │
│  │  init-wait-db    │   │  init-migrations      │  │
│  │  (checks if DB   │──►│  (runs DB schema      │  │
│  │   is ready)      │   │   migrations)         │  │
│  └──────────────────┘   └──────────────────────┘  │
│               Both exit 0                          │
│                      ↓                             │
│  Phase 2: MAIN CONTAINERS (start running)          │
│  ┌────────────────────────────────────────────┐   │
│  │           my-app                           │   │
│  │  (can safely connect to DB — it's ready!)  │   │
│  └────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

**Real-world use:**
- Wait for a database to be ready before starting the app
- Download configuration or secrets before app needs them
- Register the service with a service registry before going live

```yaml
spec:
  initContainers:
  - name: wait-for-db
    image: busybox
    command: ['sh', '-c', 
      'until nc -z postgres-service 5432; do echo waiting; sleep 2; done']
  containers:
  - name: my-app
    image: my-app:latest
```

> **Analogy:** Init containers are like **prep cooks**.  
> Before the head chef (main container) arrives, prep cooks chop vegetables, preheat ovens, and lay out ingredients.  
> The head chef only starts cooking (the main app only starts) once all prep work is done.

---

### Pattern 3: Ambassador

A proxy container that acts as a **local gateway** to an external resource. The main app always talks to `localhost`, and the ambassador handles complexity like routing, retries, authentication.

```
┌────────────────────────────────────────────────────┐
│                        POD                         │
│                                                    │
│  ┌──────────────────┐   ┌──────────────────────┐  │
│  │   Main App       │   │  Ambassador Proxy    │  │
│  │                  │   │                      │  │
│  │  connects to     │   │  handles:            │  │
│  │  localhost:5432  ├──►│  - connection pool   │  │  
│  │  (always local!) │   │  - SSL termination   │  │
│  │                  │   │  - retry logic       │  │
│  │                  │   │  → real DB server    │  │
│  └──────────────────┘   └──────────────────────┘  │
└────────────────────────────────────────────────────┘
```

> **Analogy:** The Ambassador is like your **personal assistant**.  
> Instead of you dealing with the complexity of booking flights, hotels, visas (the DB connection pool, SSL certs, retries), your assistant handles all of it.  
> You just say "I need to be in Tokyo on Friday" (connect to localhost:5432) and they make it happen.

---

## 🏥 Health Probes — Teaching K8s When Your App Is "Ready"

K8s can't just look at a process running and know your app is healthy. You need to tell it HOW to check. That's what probes do.

### The Three Probe Types

```
┌───────────────────────────────────────────────────────────────────┐
│                         PROBE TIMELINE                            │
│                                                                   │
│  Container Starts                                                 │
│       │                                                           │
│       │◄────── startupProbe ─────────────────────────►│          │
│       │   (is the app done starting up yet?)           │          │
│       │                       (once startupProbe      │          │
│       │                        succeeds, it stops)    │          │
│       │                                               │          │
│       │◄──── livenessProbe ──────────────────────────────────►  │
│       │   (is the app still alive? restart if not)              │
│       │                                                          │
│       │◄──── readinessProbe ────────────────────────────────►   │
│       │   (is the app ready for traffic? route to it or not)    │
└───────────────────────────────────────────────────────────────────┘
```

### livenessProbe — "Is the App Stuck?"

If this probe fails, **K8s kills and restarts the container**.  
Use it to detect deadlocked processes that are running but not actually doing anything.

```yaml
livenessProbe:
  httpGet:
    path: /healthz      # K8s hits this endpoint
    port: 8080
  initialDelaySeconds: 10  # Wait 10s after start before checking
  periodSeconds: 5         # Check every 5 seconds
  failureThreshold: 3      # Fail 3 times in a row before restart
```

> **Analogy:** Liveness is like a **"Are you alive?" ping** to an employee over Slack.  
> If they don't respond after 3 attempts, you assume they've gone AFK and replace them (restart container).  
> It doesn't mean they're doing GOOD work — just that they're responsive.

---

### readinessProbe — "Is the App Ready for Traffic?"

If this probe fails, **the pod is removed from the Service's endpoint list** — no traffic is sent to it.  
The pod keeps running but receives zero requests until it's ready again.

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 10
  failureThreshold: 3
```

> **Analogy:** Readiness is like a **"Open" sign** on a shop door.  
> Even if the shop is physically present (liveness OK), customers (traffic) should only enter if the sign is on (readiness OK).  
> During inventory restocking (app warming up cache), flip the sign to "Closed" — customers wait elsewhere.

**Key difference: Liveness vs Readiness**

| | livenessProbe | readinessProbe |
|--|--|--|
| Fail action | Restart container | Remove from Service endpoints |
| Use case | Detect deadlock/stuck state | Control when traffic arrives |
| Pod killed? | YES | NO |

---

### startupProbe — "Has the App Finished Starting?"

Some apps (Java, legacy apps) take 30-90 seconds to start. Without startupProbe, livenessProbe would kill them before they even finish loading!

```yaml
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30    # Allow up to 30 * 10s = 5 minutes to start
  periodSeconds: 10
```

Once the startupProbe succeeds once, it stops running and hands off to liveness/readiness.

---

### Three Probe Mechanisms

Probes aren't just HTTP. You can check in 3 ways:

```yaml
# 1. HTTP GET — most common
livenessProbe:
  httpGet:
    path: /health
    port: 8080
    httpHeaders:
    - name: Authorization
      value: Bearer mytoken

# 2. TCP Socket — just checks the port is open
livenessProbe:
  tcpSocket:
    port: 3306   # Great for databases that don't have HTTP

# 3. Exec Command — runs a command inside the container
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy   # If this file exists, probe succeeds (exit 0)
```

---

## 📦 Resource Requests & Limits

Every container should declare how much CPU and memory it needs and the maximum it can use.

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:latest
    resources:
      requests:        # ← What the SCHEDULER uses for placement decisions
        memory: "128Mi"
        cpu: "250m"    # 250m = 0.25 CPU cores (m = millicores)
      limits:          # ← Hard cap. Container CANNOT exceed this.
        memory: "256Mi"
        cpu: "500m"
```

```
                   Scheduler's view of a node:
                   
Node capacity:   ████████████████████████  (4000m CPU, 8Gi RAM)
Pod A requests:  ████                      (1000m CPU, 2Gi RAM)
Pod B requests:  ██                        (500m CPU, 1Gi RAM)
Pod C requests:  ██                        (500m CPU, 1Gi RAM)
                 ─────────────────────────
Remaining:       ██████████████████        (2000m CPU, 4Gi RAM)

Note: Scheduler uses REQUESTS for placement, not actual usage.
If Pod A requests 1000m but only uses 200m, remaining looks like 
3800m but scheduler thinks only 2000m is left.
```

**What happens at the limits:**
- **CPU limit exceeded?** Container is **throttled** (slowed down). It doesn't die.
- **Memory limit exceeded?** Container is **OOMKilled** (killed immediately by the OS). K8s then restarts it.

> **Analogy:**  
> `requests` = the parking spot you reserve at work. Whether you use it or not, it's yours.  
> `limits` = the maximum speed on a highway. CPU limit is a speed camera (you slow down). Memory limit is a cliff (you go over, you crash).

**Quality of Service (QoS) Classes** — K8s assigns these automatically:

| QoS Class | Condition | Eviction Priority |
|-----------|-----------|-----------------|
| `Guaranteed` | requests == limits for ALL containers | Last to be evicted |
| `Burstable` | requests < limits (or only requests set) | Middle |
| `BestEffort` | NO requests or limits set | First to be evicted |

---

## 📄 A Complete, Annotated Pod YAML

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-server                      # Unique name in the namespace
  namespace: production                 # Which namespace it lives in
  labels:                               # Labels — used by Selectors to find this pod
    app: web-server
    version: v2
    team: frontend
  annotations:                          # Non-queryable metadata (notes, tool config)
    prometheus.io/scrape: "true"
    last-updated-by: "alice"
spec:
  restartPolicy: Always                 # Always restart on failure (default)

  initContainers:                       # Run before main containers
  - name: wait-for-config
    image: busybox:1.35
    command: ['sh', '-c', 'until wget -q http://config-server/ready; do sleep 2; done']

  containers:
  - name: nginx                         # Container name (unique within pod)
    image: nginx:1.25                   # Image from registry (hub.docker.com by default)
    imagePullPolicy: IfNotPresent       # Pull only if not already on the node

    ports:
    - containerPort: 80                 # Informational only — doesn't actually open port
      name: http

    env:                                # Environment variables
    - name: LOG_LEVEL
      value: "info"
    - name: DB_HOST
      valueFrom:                        # From a ConfigMap (we'll learn in Phase 2)
        configMapKeyRef:
          name: app-config
          key: database-host

    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"

    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10

    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 5

    volumeMounts:                       # Where to mount volumes inside this container
    - name: config-vol
      mountPath: /etc/nginx/conf.d/

  volumes:                              # Volumes available to containers in this pod
  - name: config-vol
    configMap:                          # ConfigMap as a file (Phase 2)
      name: nginx-config
```

---

## 🧪 Test Yourself

1. **Why does K8s schedule Pods instead of scheduling individual containers directly?** Pods are the smallest deployable units in Kubernetes. It is a wrapper that makes it possible for multiple containers to run together as a single unit — sharing the same network interface, the same localhost, the same mounted volumes.

2. **Two containers are in the same Pod. Container A runs on port 8080. Can Container B reach it via `curl localhost:8080`?** Why? yes they share the same network namespace and localhost.

3. **What is the difference between `livenessProbe` and `readinessProbe`?** What does each one do when it fails? liveness checks if the pod is alive and should be restarted if it is not. Readiness checks if the pod is ready to receive traffic and should be removed from the service if it is not.

4. **Your Java app takes 90 seconds to start. The livenessProbe kills it after 30s. What do you add to fix this?** add initialDelaySeconds to livenessProbe to be greater than 30s

5. **A pod shows `OOMKilled` in its status. What does that mean, and what two things can you do to fix it?** OOMKilled means the container exceeded its memory limit. We can fix this by increasing the memory limit or reducing the memory usage of the application.

6. **What is the Sidecar pattern? Give a real-world example.**adding a helper container to a pod to assist the main application container. For example, a logging sidecar container that collects logs from the main container and sends them to a central logging system.

7. **Your container has `requests.memory: 128Mi` and `limits.memory: 256Mi`. What QoS class does K8s assign? When would this pod be evicted before a Guaranteed pod?** Burstable. This pod would be evicted before a Guaranteed pod if the node runs out of memory or disk space.

8. **Trace what happens between `kubectl apply -f pod.yaml` and the pod showing `Running` — naming every K8s component involved.**kubectl to etcd to controller manager to kubelet to container runtime
