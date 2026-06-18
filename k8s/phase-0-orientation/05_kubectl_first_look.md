# 05 — kubectl: Your First Look at a Live Cluster

> **Goal:** Get comfortable navigating a cluster. Understand what you're looking at. Build the habit of reading output before acting.

---

## 🎮 kubectl — The Universal Remote Control

kubectl (pronounced "kube-control" or "kube-cuddle" — both are acceptable!) is the command-line client for Kubernetes. It talks to the API Server on your behalf.

```
You type:          kubectl get pods
                        │
                        ▼
             ┌──────────────────────┐
             │    API Server        │
             │    (your cluster)    │
             └──────────┬───────────┘
                        │
                reads from etcd
                        │
                        ▼
             Returns pod list to kubectl
                        │
                        ▼
You see:       NAME        READY   STATUS    RESTARTS   AGE
               nginx-pod   1/1     Running   0          5m
```

---

## 🧱 kubectl Command Structure

Every kubectl command follows this pattern:

```
kubectl  [command]  [resource-type]  [resource-name]  [flags]
   │         │            │               │               │
   │         │            │               │               └── Options: -n, -o, --watch
   │         │            │               └── Optional: specific object name
   │         │            └── pods, deployments, services, nodes...
   │         └── get, describe, apply, delete, exec, logs...
   └── The CLI tool

Examples:
kubectl  get      pods                          # all pods, default namespace
kubectl  get      pods     nginx-pod            # specific pod
kubectl  get      pods     nginx-pod  -o yaml   # output as YAML
kubectl  describe node     node-1               # detailed description
kubectl  delete   pod      nginx-pod            # delete a pod
```

---

## 📊 The Most Important Commands (Phase 0)

### `kubectl get` — List Resources

```powershell
# Pods
kubectl get pods                        # Default namespace
kubectl get pods -n kube-system         # Specific namespace
kubectl get pods --all-namespaces       # Every namespace
kubectl get pods -A                     # Same as --all-namespaces (shorthand)
kubectl get pods -o wide                # Extra info: node, IP
kubectl get pods -o yaml                # Full YAML output
kubectl get pods --show-labels          # Show all labels
kubectl get pods -w                     # Watch for real-time changes (Ctrl+C to stop)

# Nodes
kubectl get nodes
kubectl get nodes -o wide               # Shows kernel version, OS, container runtime

# Everything (useful for exploring)
kubectl get all                         # pods, services, deployments, replicasets
kubectl get all -A                      # Everything, all namespaces
```

**Reading `kubectl get pods` output:**

```
NAME            READY   STATUS    RESTARTS   AGE
nginx-pod       1/1     Running   0          5m
broken-pod      0/1     Error     3          2m

│               │       │         │           └─ How long it's been running
│               │       │         └─────────── Times the container has restarted
│               │       └───────────────────── Current lifecycle state
│               └───────────────────────────── running containers / total containers
└───────────────────────────────────────────── Object name
```

**Common STATUS values and what they mean:**

| Status | Meaning |
|--------|---------|
| `Pending` | Pod created, waiting to be scheduled or for image pull |
| `ContainerCreating` | Scheduled, pulling image or starting container |
| `Running` | At least one container is running |
| `Completed` | All containers ran to completion (Jobs) |
| `Error` | Container exited with non-zero code |
| `CrashLoopBackOff` | Container keeps crashing; K8s is backing off retries |
| `ImagePullBackOff` | Can't pull the container image (wrong name, no auth) |
| `OOMKilled` | Container exceeded memory limit, killed by OS |
| `Terminating` | Pod is being deleted |
| `Evicted` | Node was low on resources; pod was evicted |

---

### `kubectl describe` — The Debug Command

`kubectl describe` is your most powerful debugging tool. It shows:
- The object's full spec
- Computed values (like which node a pod is on)
- **The Events section** — this is WHERE problems show up

```powershell
kubectl describe pod nginx-pod
kubectl describe node k8s-multinode-worker
kubectl describe deployment web-app
kubectl describe service my-service
```

**Anatomy of `kubectl describe pod` output:**

```
Name:             nginx-pod            ← Pod name
Namespace:        default
Priority:         0
Node:             worker-1/10.0.0.3   ← Which node it's on
Start Time:       Wed, 11 Jun 2026
Labels:           app=nginx
Status:           Running
IP:               10.244.1.5          ← Pod IP (ephemeral!)
Containers:
  nginx:
    Image:        nginx:1.25          ← What image it's running
    Port:         80/TCP
    State:        Running
    Ready:        True
    Restart Count: 0
Conditions:
  Type              Status
  Initialized       True
  Ready             True
  ContainersReady   True
  PodScheduled      True
Volumes:
  ...
Events:                               ← ← ← READ THIS FIRST WHEN DEBUGGING
  Type    Reason     Age   From               Message
  ----    ------     ----  ----               -------
  Normal  Scheduled  5m    default-scheduler  Successfully assigned default/nginx-pod to worker-1
  Normal  Pulling    5m    kubelet            Pulling image "nginx:1.25"
  Normal  Pulled     4m    kubelet            Successfully pulled image
  Normal  Created    4m    kubelet            Created container nginx
  Normal  Started    4m    kubelet            Started container nginx
```

> 💡 **Pro tip:** The Events section tells the story of what happened to a pod. When a pod won't start, scroll straight to Events. The error message is almost always there.

---

### `kubectl logs` — Container Output

```powershell
# Get logs from a pod (single container)
kubectl logs nginx-pod

# Follow logs live (like `tail -f`)
kubectl logs -f nginx-pod

# Get logs from a CRASHED container (the previous run)
kubectl logs nginx-pod --previous

# Get logs from a specific container (multi-container pods)
kubectl logs nginx-pod -c sidecar-container

# Last 50 lines only
kubectl logs nginx-pod --tail=50

# Logs from the last 5 minutes
kubectl logs nginx-pod --since=5m
```

---

### `kubectl exec` — Get Inside a Container

```powershell
# Open an interactive shell inside a running container
kubectl exec -it nginx-pod -- bash

# Run a single command and exit
kubectl exec nginx-pod -- ls /etc/nginx/

# Multi-container pod: specify which container
kubectl exec -it nginx-pod -c nginx -- bash
```

What you can do inside:
```bash
# Check if a service is reachable (from inside the cluster network)
curl http://my-service:80
curl http://other-app.other-namespace.svc.cluster.local

# Check DNS
nslookup my-service
cat /etc/resolv.conf

# Check env vars (ConfigMaps/Secrets mounted as env)
env | grep DATABASE

# Check mounted files
ls /etc/config/
cat /etc/config/app.properties
```

---

### `kubectl explain` — Built-in Documentation

This is massively underused. Every field in every K8s object is documented right in the CLI:

```powershell
# What is a Pod?
kubectl explain pod

# What fields does pod.spec have?
kubectl explain pod.spec

# What's in pod.spec.containers?
kubectl explain pod.spec.containers

# What resource limits look like
kubectl explain pod.spec.containers.resources

# Full recursive documentation
kubectl explain pod --recursive | head -50
```

> 💡 **Exam tip:** During the CKA/CKAD exam, `kubectl explain` is allowed (it uses local docs, no internet needed) and is often faster than searching the docs website.

---

### `kubectl apply` and `kubectl delete`

```powershell
# Apply a manifest (create or update)
kubectl apply -f pod.yaml
kubectl apply -f ./                  # Apply all YAML files in a directory
kubectl apply -f https://some-url    # Apply from URL (careful with this)

# Delete resources
kubectl delete -f pod.yaml           # Delete what's described in the file
kubectl delete pod nginx-pod         # Delete by name
kubectl delete pods --all            # Delete all pods in current namespace
kubectl delete pod nginx-pod --force --grace-period=0   # Instant delete (skip graceful shutdown)
```

---

### `kubectl port-forward` — Access Cluster Services Locally

Since your kind cluster runs inside Docker, you can't directly hit pod IPs from your Windows browser. `port-forward` creates a tunnel:

```powershell
# Forward local port 8080 to port 80 of a pod
kubectl port-forward pod/nginx-pod 8080:80

# Forward to a service (distributes across pods)
kubectl port-forward service/my-service 8080:80

# Now open: http://localhost:8080 in your browser

# Run in background (Ctrl+C to stop)
kubectl port-forward service/my-service 8080:80 &
```

---

## 🔍 Exploring the System Namespace

The `kube-system` namespace contains the core K8s components themselves. Let's explore them:

```powershell
kubectl get pods -n kube-system
```

Expected output in a kind cluster:
```
NAME                                                READY   STATUS    RESTARTS
coredns-xxxx                                        1/1     Running   0         ← DNS server
coredns-yyyy                                        1/1     Running   0         ← DNS server (redundant)
etcd-k8s-multinode-control-plane                    1/1     Running   0         ← etcd database!
kube-apiserver-k8s-multinode-control-plane          1/1     Running   0         ← API server!
kube-controller-manager-k8s-multinode-control-plane 1/1     Running   0         ← Controller manager!
kube-proxy-xxxx                                     1/1     Running   0         ← kube-proxy on node 1
kube-proxy-yyyy                                     1/1     Running   0         ← kube-proxy on node 2
kube-scheduler-k8s-multinode-control-plane          1/1     Running   0         ← Scheduler!
kindnet-xxxx                                        1/1     Running   0         ← CNI plugin (kind's network)
kindnet-yyyy                                        1/1     Running   0
```

> 🔑 **The architecture is alive!** All those components you studied in `02_architecture.md` are right there as pods. etcd, the API server, the scheduler — they're all containers running in your cluster!

```powershell
# Look at the actual API server container
kubectl describe pod kube-apiserver-k8s-multinode-control-plane -n kube-system

# Look at the etcd container
kubectl describe pod etcd-k8s-multinode-control-plane -n kube-system
# Note the --data-dir and cert file paths — you'll need these for backup/restore later!
```

---

## 📐 Output Formats — Getting the Data You Need

```powershell
# YAML output (full object definition + status)
kubectl get pod nginx-pod -o yaml

# JSON output (useful for piping to jq)
kubectl get pod nginx-pod -o json

# Extract specific field with jsonpath
kubectl get pod nginx-pod -o jsonpath='{.status.podIP}'
kubectl get pods -o jsonpath='{.items[*].metadata.name}'

# Custom columns
kubectl get pods -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName

# Wide output (most common extra-info format)
kubectl get pods -o wide
```

---

## ⚡ Time-Saving Aliases (Set These Up Now)

Add these to your PowerShell profile (`$PROFILE`):

```powershell
# Open profile for editing
notepad $PROFILE

# Add these lines:
Set-Alias k kubectl
function kgp { kubectl get pods $args }
function kgpa { kubectl get pods -A $args }
function kgs { kubectl get services $args }
function kgd { kubectl get deployments $args }
function kgn { kubectl get nodes $args }
function kdp { kubectl describe pod $args }
function kl { kubectl logs $args }
function kex { kubectl exec -it $args }
function kaf { kubectl apply -f $args }
function kdf { kubectl delete -f $args }

# Shorthand dry-run (you'll use this constantly for exam)
function kdry { kubectl $args --dry-run=client -o yaml }
```

Reload: `. $PROFILE`

---

## 🧪 Test Yourself

After doing the homework, answer these from memory:

1. What command shows you all pods across all namespaces?
2. A pod shows `0/1` in the READY column. What does that mean?
3. Where do you look FIRST when a pod won't start? (Hint: it's a section in `describe`)
4. What's the difference between `kubectl logs pod-name --previous` and just `kubectl logs pod-name`?
5. Why can't you directly curl a pod IP from your browser when using kind on Windows?
6. What does `kubectl explain pod.spec.containers.livenessProbe` show you?
7. You want to see what node each pod is running on without `-o yaml`. What flag do you add?
