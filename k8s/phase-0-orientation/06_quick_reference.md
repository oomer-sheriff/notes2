# ☸️ Phase 0 — Quick Reference Cheat Sheet

> Keep this open in a side tab while doing labs. Print it if you're old school.

---

## Cluster Management (kind)

```powershell
kind create cluster --config kind-config.yaml   # Create cluster from config
kind get clusters                               # List all clusters
kind delete cluster --name k8s-multinode        # Delete a cluster
kind delete clusters --all                      # Nuke everything
kind load docker-image my-img --name k8s-multinode  # Push local image to cluster
```

---

## Context & Namespace

```powershell
kubectl config get-contexts                     # List all clusters/contexts
kubectl config current-context                  # What cluster am I on?
kubectl config use-context kind-k8s-multinode   # Switch cluster

kubectl get namespaces                          # List namespaces (short: kubectl get ns)
kubectl create namespace my-ns                  # Create namespace
kubectl config set-context --current --namespace=my-ns  # Set default namespace
```

---

## Get Resources

```powershell
kubectl get pods                   # Default namespace
kubectl get pods -n kube-system    # Specific namespace
kubectl get pods -A                # All namespaces
kubectl get pods -o wide           # With IP and node
kubectl get pods -w                # Watch live
kubectl get pods --show-labels     # Show all labels
kubectl get pods -l app=nginx      # Filter by label
kubectl get all                    # pods + svc + deploy + rs in namespace
kubectl get events --sort-by='.lastTimestamp'  # Sorted cluster events
```

---

## Describe & Debug

```powershell
kubectl describe pod <name>        # Full details + Events (use this first!)
kubectl describe node <name>       # Node details + allocated resources
kubectl describe svc <name>        # Service details + endpoints

kubectl logs <pod>                 # Container stdout
kubectl logs <pod> -f              # Follow live
kubectl logs <pod> --previous      # Crashed container logs
kubectl logs <pod> -c <container>  # Specific container (multi-container pod)
kubectl logs <pod> --tail=50       # Last 50 lines
kubectl logs <pod> --since=5m      # Last 5 minutes

kubectl exec -it <pod> -- bash     # Shell into container
kubectl exec <pod> -- <cmd>        # Run single command
```

---

## Apply & Delete

```powershell
kubectl apply -f file.yaml         # Create or update
kubectl apply -f ./                # Apply whole directory
kubectl delete -f file.yaml        # Delete what's in file
kubectl delete pod <name>          # Delete by name
kubectl delete pod <name> --force --grace-period=0  # Instant kill
kubectl delete pods --all          # Delete all pods in namespace
```

---

## Generate YAML (Dry Run — Your Best Friend)

```powershell
# Generate pod YAML without creating it
kubectl run mypod --image=nginx --dry-run=client -o yaml

# Generate deployment YAML
kubectl create deployment myapp --image=nginx --replicas=3 --dry-run=client -o yaml

# Generate service YAML
kubectl create service clusterip mysvc --tcp=80:80 --dry-run=client -o yaml

# Save to file (then edit as needed)
kubectl run mypod --image=nginx --dry-run=client -o yaml > pod.yaml
```

---

## Built-in Docs

```powershell
kubectl explain pod                        # Top-level object
kubectl explain pod.spec                   # Spec fields
kubectl explain pod.spec.containers        # Container fields
kubectl explain pod.spec.containers.livenessProbe
kubectl explain deployment
kubectl explain service
kubectl explain --recursive pod.spec       # All nested fields (long output!)
```

---

## Port Forwarding

```powershell
kubectl port-forward pod/<name> 8080:80    # Local:PodPort
kubectl port-forward svc/<name> 8080:80   # Via service
kubectl port-forward deploy/<name> 8080:80 # Via deployment
# Access at: http://localhost:8080
```

---

## Common Status Values

| Status | Meaning | Fix |
|--------|---------|-----|
| `Pending` | Not scheduled yet | Check node resources, `describe pod` Events |
| `ContainerCreating` | Starting up | Image pull in progress, check `describe pod` |
| `CrashLoopBackOff` | App keeps crashing | Check `logs --previous` |
| `ImagePullBackOff` | Can't pull image | Wrong image name? No registry auth? |
| `OOMKilled` | Out of memory | Increase memory limit |
| `Terminating` stuck | Pod won't die | `--force --grace-period=0` |

---

## Debug Runbook

```
Pod won't start?
  1. kubectl describe pod <name>     ← Read Events section
  2. kubectl logs <name>             ← Read app output
  3. kubectl logs <name> --previous  ← Read crashed container output

Service not routing traffic?
  1. kubectl get endpoints <svc>     ← Are there any IPs? If empty = selector mismatch
  2. kubectl get pods --show-labels  ← Do pod labels match service selector?
  3. kubectl describe svc <name>     ← Check Selector field

Node problems?
  1. kubectl get nodes               ← Check STATUS column
  2. kubectl describe node <name>    ← Check Conditions + Events
  3. kubectl top nodes               ← Check actual resource usage
```

---

## Architecture At a Glance

```
CONTROL PLANE          │  WORKER NODES
───────────────────    │  ─────────────────────
API Server             │  kubelet
  └─ The gateway       │    └─ Talks to API Server
  └─ All talk here     │    └─ Tells container runtime to act
                       │
etcd                   │  kube-proxy
  └─ The only DB       │    └─ Manages iptables for Services
  └─ Desired state     │
                       │  Container Runtime (containerd)
Scheduler              │    └─ Actually runs containers
  └─ Assigns pods      │
  └─ to nodes          │  Pods
                       │    └─ Your actual workloads
Controller Manager     │    └─ 1+ containers sharing network+storage
  └─ Reconcile loops   │
  └─ Self-healing       │
```
