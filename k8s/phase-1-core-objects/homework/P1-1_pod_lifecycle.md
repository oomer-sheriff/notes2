# Homework P1-1 — Pod Lifecycle Deep Dive

> **Time:** 2–3 hours  
> **Goal:** Get hands-on with every part of a Pod's lifecycle — creation, health, probes, multi-container patterns, and failure scenarios.  
> **Rule:** Type every command. Don't copy-paste. Read the output before moving on.

---

## 🚀 Setup

```powershell
# Make sure your cluster is running
kubectl get nodes
# Should show 3 Ready nodes

# Create a working namespace for this lab
kubectl create namespace lab1
# Set it as default for this session
kubectl config set-context --current --namespace=lab1
```

---

## Part 1 — Pod Basics (30 min)

### Task 1.1 — Create and Inspect Your First Pod from YAML

Save this file as `d:\learning\k8s\phase-1-core-objects\homework\lab-files\nginx-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-basic
  namespace: lab1
  labels:
    app: web
    version: v1
    team: frontend
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
      name: http
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
```

```powershell
kubectl apply -f lab-files/nginx-pod.yaml

# Watch it come up (Ctrl+C when Running)
kubectl get pods -w -n lab1

# Once Running:
kubectl get pod nginx-basic -o wide     # Note the IP and NODE
kubectl describe pod nginx-basic        # Read EVERY section — take your time
```

**Fill in from the output:**

| Field | Value |
|-------|-------|
| What node was it scheduled on? | |
| What is its pod IP? | |
| What QoS class was it assigned? | |
| What events happened during startup? | |
| Is it Guaranteed, Burstable, or BestEffort? Why? | |

---

### Task 1.2 — Explore Inside the Pod

```powershell
# Open a shell inside the container
kubectl exec -it nginx-basic -- bash

# Run these INSIDE the container:
hostname                    # Note this = pod name
ip addr show eth0           # What IP does the container see?
cat /etc/resolv.conf        # Note the nameserver and search domains
env | grep KUBERNETES       # What K8s env vars are injected?
ps aux                      # What processes are running?
exit
```

**Write down:**
- Does the container IP match what `kubectl get pod -o wide` showed?
- What is the nameserver address? (This is CoreDNS!)
- What search domains are listed?

---

### Task 1.3 — Pod IP Lifecycle (The Ephemeral IP Demo)

```powershell
# Note the current pod IP
kubectl get pod nginx-basic -o jsonpath='{.status.podIP}'
echo ""

# Delete the pod
kubectl delete pod nginx-basic

# Immediately re-create it
kubectl apply -f lab-files/nginx-pod.yaml
kubectl get pod nginx-basic -o wide

# Compare the IP
kubectl get pod nginx-basic -o jsonpath='{.status.podIP}'
echo ""
```

**Observation:** Did the IP change? This is WHY Services exist.

---

## Part 2 — Health Probes (45 min)

### Task 2.1 — Build a Pod With All Three Probes

Save as `lab-files/probes-pod.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: probes-demo
  namespace: lab1
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"

    startupProbe:
      httpGet:
        path: /
        port: 80
      failureThreshold: 10
      periodSeconds: 5
      # Allows up to 10 × 5s = 50 seconds for startup

    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 5
      failureThreshold: 3

    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 10
      periodSeconds: 10
      failureThreshold: 3
```

```powershell
kubectl apply -f lab-files/probes-pod.yaml
kubectl describe pod probes-demo
# Look for probe configuration in the container spec section
```

---

### Task 2.2 — Break the Readiness Probe

```powershell
# First, create a Deployment (so pods have endpoints via a Service)
kubectl create deployment probe-deploy --image=nginx:1.25 --replicas=2 -n lab1
kubectl expose deployment probe-deploy --port=80 --target-port=80 -n lab1

# Check endpoints — should show 2 IPs
kubectl get endpoints probe-deploy -n lab1

# Now break one pod — delete nginx's default content
POD=$(kubectl get pods -n lab1 -l app=probe-deploy -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -n lab1 -- rm /usr/share/nginx/html/index.html

# Watch the pod readiness change (Ctrl+C after ~30 seconds)
kubectl get pods -n lab1 -w

# Check endpoints — it should be REMOVED from the endpoint list!
kubectl get endpoints probe-deploy -n lab1

# Restore the file
kubectl exec $POD -n lab1 -- sh -c 'echo "Hello World" > /usr/share/nginx/html/index.html'

# Watch it rejoin (Ctrl+C after ~30 seconds)
kubectl get pods -n lab1 -w
kubectl get endpoints probe-deploy -n lab1
```

**Key observation:** When readiness fails, the pod is NOT killed. It's only removed from service routing. When it recovers, it rejoins automatically.

---

### Task 2.3 — Trigger a Liveness Kill

```powershell
# Create a pod with a liveness probe checking for a specific file
kubectl apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: liveness-demo
  namespace: lab1
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'touch /tmp/healthy; sleep 30; rm /tmp/healthy; sleep 600']
    livenessProbe:
      exec:
        command:
        - cat
        - /tmp/healthy
      initialDelaySeconds: 5
      periodSeconds: 5
      failureThreshold: 3
    resources:
      requests:
        memory: "32Mi"
        cpu: "50m"
      limits:
        memory: "64Mi"
        cpu: "100m"
EOF

# Watch what happens over the next ~60 seconds
kubectl get pod liveness-demo -n lab1 -w

# After it restarts:
kubectl describe pod liveness-demo -n lab1
# Look at Events and Restart Count
```

**Fill in:**
- How long after the `/tmp/healthy` file was deleted did the pod restart?
- What does the Events section say caused the restart?
- What is the RESTART count after the incident?

---

## Part 3 — Init Container (30 min)

### Task 3.1 — Simulate Service Dependency with Init Container

This lab simulates an app waiting for a dependency before starting.

```yaml
# Save as: lab-files/init-container.yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-init
  namespace: lab1
spec:
  initContainers:
  - name: wait-for-service
    image: busybox:1.35
    command:
    - sh
    - -c
    - |
      echo "Checking if 'myservice' is available..."
      until nslookup myservice.lab1.svc.cluster.local; do
        echo "myservice not ready — waiting 3s..."
        sleep 3
      done
      echo "myservice is UP! Proceeding..."

  containers:
  - name: main-app
    image: nginx:1.25
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
```

```powershell
kubectl apply -f lab-files/init-container.yaml

# Watch the pod — it will be in "Init:0/1" state
kubectl get pod app-with-init -n lab1 -w

# Read init container logs
kubectl logs app-with-init -n lab1 -c wait-for-service

# Now create the service it's waiting for!
kubectl create service clusterip myservice --tcp=80:80 -n lab1

# Watch the init container succeed and main container start
kubectl get pod app-with-init -n lab1 -w
kubectl logs app-with-init -n lab1 -c wait-for-service
```

**Key observation:** Notice the pod was stuck in `Init:0/1` until the service existed. The main container only started AFTER the init container succeeded.

---

## Part 4 — Sidecar Pattern (30 min)

### Task 4.1 — Log Aggregation Sidecar

Build a pod where the main container writes logs to a shared volume, and a sidecar reads and processes them.

```yaml
# Save as: lab-files/sidecar-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: sidecar-demo
  namespace: lab1
spec:
  containers:
  - name: log-writer                        # Main container — writes logs
    image: busybox:1.35
    command:
    - sh
    - -c
    - |
      i=1
      while true; do
        echo "$(date): Request #$i processed successfully" >> /var/log/app/app.log
        i=$((i+1))
        sleep 2
      done
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app

  - name: log-reader                        # Sidecar — reads and "ships" logs
    image: busybox:1.35
    command:
    - sh
    - -c
    - |
      echo "Log shipper started. Watching for new entries..."
      tail -f /var/log/app/app.log
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app               # SAME mountPath = shared volume!

  volumes:
  - name: shared-logs
    emptyDir: {}                            # Temporary volume, lives for pod lifetime
```

```powershell
kubectl apply -f lab-files/sidecar-pod.yaml
kubectl get pod sidecar-demo -n lab1
# Note: READY shows 2/2 — both containers must be ready

# View logs from each container separately
kubectl logs sidecar-demo -n lab1 -c log-writer
kubectl logs sidecar-demo -n lab1 -c log-reader

# Follow the sidecar's output live
kubectl logs sidecar-demo -n lab1 -c log-reader -f
# (Ctrl+C to stop)
```

---

## 🧹 Cleanup

```powershell
# Delete everything in the lab namespace
kubectl delete namespace lab1

# Reset default namespace back to default
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] Tasks 1.1 – 1.3: Pod creation, inspection, and IP lifecycle complete
- [ ] All fill-in tables completed
- [ ] Task 2.2: Witnessed readiness probe removing pod from endpoints, then restoring it
- [ ] Task 2.3: Witnessed liveness probe killing and restarting a pod
- [ ] Task 3.1: Init container waited for a service to exist before main app started
- [ ] Task 4.1: Sidecar pattern working — shared volume between two containers

---

## 📝 Reflection

**Most surprising thing I learned:**
```

```

**Command I need to practice more:**
```

```

**Concept I'm still fuzzy on:**
```

```
