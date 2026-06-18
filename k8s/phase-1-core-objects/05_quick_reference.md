# ☸️ Phase 1 — Quick Reference Cheat Sheet

> Everything you need at your fingertips during Phase 1 labs. Print this or keep it open in a second window.

---

## Pods

```bash
# Create
kubectl run mypod --image=nginx:1.25
kubectl run mypod --image=nginx --dry-run=client -o yaml > pod.yaml
kubectl apply -f pod.yaml

# Inspect
kubectl get pods
kubectl get pods -o wide                          # Show IP and Node
kubectl get pods -w                               # Watch live
kubectl describe pod <name>                       # Full details + Events
kubectl get pod <name> -o yaml                    # Full YAML with status

# Debug
kubectl logs <pod>                                # Container stdout
kubectl logs <pod> --previous                     # Crashed container logs
kubectl logs <pod> -c <container>                 # Multi-container pod
kubectl exec -it <pod> -- bash                    # Shell in
kubectl exec <pod> -- <cmd>                       # Single command

# Delete
kubectl delete pod <name>
kubectl delete pod <name> --force --grace-period=0   # Instant

# Useful one-liners
kubectl get pod <name> -o jsonpath='{.status.podIP}'    # Get IP
kubectl get pods --show-labels                           # See labels
kubectl get pods -l app=nginx                            # Filter by label
```

---

## Deployments

```bash
# Create
kubectl create deployment myapp --image=nginx --replicas=3
kubectl apply -f deployment.yaml

# Update
kubectl set image deployment/myapp nginx=nginx:1.25
kubectl edit deployment myapp                        # Interactive edit
kubectl apply -f deployment.yaml                     # Apply changes from file

# Rollout
kubectl rollout status deployment/myapp
kubectl rollout history deployment/myapp
kubectl rollout history deployment/myapp --revision=2
kubectl rollout undo deployment/myapp                # Roll back to previous
kubectl rollout undo deployment/myapp --to-revision=1

# Scale
kubectl scale deployment myapp --replicas=5
kubectl patch deployment myapp -p '{"spec":{"replicas":5}}'

# Pause/Resume (batch changes)
kubectl rollout pause deployment/myapp
kubectl rollout resume deployment/myapp

# Inspect layers
kubectl get deployments
kubectl get replicasets                              # See RSets
kubectl get pods -l app=myapp                        # See owned pods

# Delete (cascades to RS and Pods)
kubectl delete deployment myapp
```

---

## Services

```bash
# Create
kubectl expose deployment myapp --port=80 --target-port=8080
kubectl expose deployment myapp --port=80 --type=NodePort
kubectl apply -f service.yaml

# Inspect
kubectl get services
kubectl get svc                                      # Shorthand
kubectl describe svc <name>                          # Details + selector
kubectl get endpoints <svc>                          # REAL pod IPs (use for debugging!)

# Test from inside cluster
kubectl run curl-test --image=curlimages/curl -it --rm -- curl http://<svc>

# Access locally
kubectl port-forward svc/<name> 8080:80

# Delete
kubectl delete service <name>
```

---

## Namespaces

```bash
# Create
kubectl create namespace dev
kubectl apply -f namespace.yaml

# List
kubectl get namespaces
kubectl get ns

# Work in a namespace
kubectl get pods -n dev
kubectl apply -f file.yaml -n dev
kubectl delete pod nginx -n dev

# Change default namespace
kubectl config set-context --current --namespace=dev
kubens dev                                           # (if kubens installed)

# All namespaces
kubectl get pods -A
kubectl get pods --all-namespaces

# Delete (WARNING: deletes EVERYTHING inside!)
kubectl delete namespace dev
```

---

## DNS Name Formats

```
Within same namespace:
  curl http://my-service
  
Cross-namespace:
  curl http://my-service.<namespace>.svc.cluster.local
  
Full format breakdown:
  <service-name> . <namespace> . svc . cluster . local
```

---

## Pod Status Quick Reference

| Status | Meaning | Debug Command |
|--------|---------|--------------|
| `Pending` | Not scheduled | `kubectl describe pod` → Events |
| `ContainerCreating` | Image pulling | `kubectl describe pod` → Events |
| `Running` | ✅ All good | — |
| `CrashLoopBackOff` | App crashing | `kubectl logs <pod> --previous` |
| `ImagePullBackOff` | Wrong image name | `kubectl describe pod` → Events |
| `OOMKilled` | Out of memory | Increase `limits.memory` |
| `Terminating` | Shutting down | Wait or `--force --grace-period=0` |
| `Evicted` | Node out of resources | `kubectl describe pod` → message |

---

## Probe YAML Templates

```yaml
# Startup (protect slow-starting apps)
startupProbe:
  httpGet:
    path: /healthz
    port: 8080
  failureThreshold: 30
  periodSeconds: 10

# Liveness (restart if stuck)
livenessProbe:
  httpGet:
    path: /healthz
    port: 8080
  initialDelaySeconds: 10
  periodSeconds: 10
  failureThreshold: 3

# Readiness (control traffic)
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 3
```

---

## Resources Template

```yaml
resources:
  requests:
    memory: "128Mi"    # Scheduler uses this for placement
    cpu: "250m"        # 250 millicores = 0.25 CPU
  limits:
    memory: "256Mi"    # OOMKilled if exceeded
    cpu: "500m"        # Throttled if exceeded (NOT killed)
```

---

## Generate YAML Quickly (Dry Run)

```bash
# Pod
kubectl run mypod --image=nginx --dry-run=client -o yaml

# Deployment
kubectl create deployment myapp --image=nginx --replicas=3 --dry-run=client -o yaml

# Service (ClusterIP)
kubectl create service clusterip mysvc --tcp=80:8080 --dry-run=client -o yaml

# Service (NodePort)
kubectl create service nodeport mysvc --tcp=80:8080 --node-port=30080 --dry-run=client -o yaml

# ConfigMap
kubectl create configmap myconfig --from-literal=KEY=VALUE --dry-run=client -o yaml

# Save to file:
kubectl run mypod --image=nginx --dry-run=client -o yaml > pod.yaml
```

---

## Ownership Chain Mental Model

```
You create:  Deployment
              └── creates: ReplicaSet
                              └── creates: Pod (×replicas)

Delete Deployment → ReplicaSet deleted → Pods deleted (cascade)
Delete Pod only   → ReplicaSet notices → Recreates Pod (self-healing!)
Delete ReplicaSet → Pods deleted, but Deployment recreates the RS

Never delete pods directly to "remove" a workload — delete the Deployment!
```

---

## Service Type Decision Tree

```
Need external access?
├── NO  → ClusterIP (default)
└── YES → Is this on a cloud with a LB available?
          ├── YES → LoadBalancer
          └── NO  → NodePort (dev/kind clusters)

Is this an external service you're aliasing?
└── YES → ExternalName

Is this for a StatefulSet with per-pod DNS?
└── YES → Headless (clusterIP: None)
```
