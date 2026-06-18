# 04 — Environment Setup

> **Goal:** Get a real, working Kubernetes cluster running locally on Windows. By the end of this file, you'll have a cluster you can break, experiment on, and learn from freely — with zero cloud costs.

---

## 🛠️ What You Need to Install

| Tool | What It Is | Why You Need It |
|------|-----------|----------------|
| **Docker Desktop** | Container runtime + Docker CLI | Provides containerd for kind to use |
| **kind** | Kubernetes IN Docker | Lightweight local K8s cluster |
| **kubectl** | K8s CLI | How you talk to any cluster |
| **Helm** | Package manager for K8s | You'll use this heavily in Phase 8+ |
| **k9s** | Terminal UI for K8s | HIGHLY recommended — makes cluster navigation fast |
| **kubectx + kubens** | Context/namespace switcher | Fast switching, saves time |

---

## 📥 Step 1 — Install Docker Desktop

Docker Desktop is the foundation. Everything else runs on top of it.

1. Download from: https://www.docker.com/products/docker-desktop/
2. Install with defaults
3. After install, open Docker Desktop settings:
   - Go to **Settings → Resources → WSL Integration**
   - Enable integration with your WSL2 distro (if using WSL)
   - Allocate at least: **4 CPUs, 8GB RAM, 20GB disk**
4. Verify:
```powershell
docker --version
# Expected: Docker version 24.x.x or higher

docker run hello-world
# Expected: "Hello from Docker!" message
```

> ⚠️ **If Docker Desktop is slow or heavy:** Consider using [Rancher Desktop](https://rancherdesktop.io/) as an alternative — it's open-source and lighter weight.

---

## 📥 Step 2 — Install kubectl

kubectl is the command-line tool for controlling Kubernetes clusters.

**Option A — Via Chocolatey (recommended if you have choco):**
```powershell
choco install kubernetes-cli -y
```

**Option B — Via winget:**
```powershell
winget install Kubernetes.kubectl
```

**Option C — Direct download:**
```powershell
# Download the latest kubectl
curl.exe -LO "https://dl.k8s.io/release/v1.30.0/bin/windows/amd64/kubectl.exe"
# Move it to a directory that's in your PATH
Move-Item .\kubectl.exe C:\Windows\System32\kubectl.exe
```

**Verify:**
```powershell
kubectl version --client
# Expected: Client Version: v1.30.x
```

---

## 📥 Step 3 — Install kind

kind (Kubernetes IN Docker) creates K8s clusters as Docker containers. It's the fastest way to spin up and destroy test clusters.

```powershell
# Via Chocolatey
choco install kind -y

# OR via winget
winget install Kubernetes.kind

# OR manual
curl.exe -Lo kind.exe "https://kind.sigs.k8s.io/dl/v0.23.0/kind-windows-amd64"
Move-Item .\kind.exe C:\Windows\System32\kind.exe
```

**Verify:**
```powershell
kind --version
# Expected: kind version 0.23.x
```

---

## 📥 Step 4 — Install Helm

```powershell
# Via Chocolatey
choco install kubernetes-helm -y

# Via winget
winget install Helm.Helm
```

**Verify:**
```powershell
helm version
# Expected: version.BuildInfo{Version:"v3.x.x", ...}
```

---

## 📥 Step 5 — Install k9s (Highly Recommended!)

k9s is a terminal UI for navigating your cluster. Once you use it, you'll wonder how you lived without it.

```powershell
choco install k9s -y
# OR
winget install Derailed.k9s
# OR via Scoop:
scoop install k9s
```

After installing, just run `k9s` to open the dashboard.

---

## 🏗️ Step 6 — Create Your First Cluster

### Simple Single-Node Cluster (Start Here)

```powershell
kind create cluster --name k8s-lab
```

This creates one Docker container that acts as both control plane AND worker node. Great for learning.

**Expected output:**
```
Creating cluster "k8s-lab" ...
 ✓ Ensuring node image (kindest/node:v1.30.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-k8s-lab"
You can now use your cluster with:
kubectl cluster-info --context kind-k8s-lab
```

**Verify:**
```powershell
kubectl cluster-info
kubectl get nodes
# Expected: NAME               STATUS   ROLES           AGE   VERSION
#           k8s-lab-control-plane   Ready    control-plane   1m    v1.30.x
```

---

### Multi-Node Cluster (Recommended for Phase 1+)

Create a config file first. Save it as `kind-config.yaml` in your k8s learning folder:

```yaml
# d:\learning\k8s\phase-0-orientation\kind-config.yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: k8s-multinode
nodes:
  - role: control-plane
    # Port mappings let you access NodePort services from your browser
    extraPortMappings:
      - containerPort: 30080
        hostPort: 30080
        protocol: TCP
      - containerPort: 30443
        hostPort: 30443
        protocol: TCP
  - role: worker
    labels:
      disktype: ssd        # We'll use this in Phase 6 affinity labs
  - role: worker
    labels:
      disktype: hdd
```

Create the cluster:
```powershell
kind create cluster --config d:\learning\k8s\phase-0-orientation\kind-config.yaml
```

**Verify multi-node:**
```powershell
kubectl get nodes
# Expected:
# NAME                          STATUS   ROLES           AGE
# k8s-multinode-control-plane   Ready    control-plane   2m
# k8s-multinode-worker          Ready    <none>          90s
# k8s-multinode-worker2         Ready    <none>          90s
```

---

## 🧩 Step 7 — Install Metrics Server (Needed for Phase 6 HPA Labs)

The default kind cluster doesn't have the metrics server. Install it now so it's ready:

```powershell
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# kind clusters need an insecure TLS flag for metrics-server to work
kubectl patch deployment metrics-server -n kube-system --type='json' `
  -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

# Wait ~1 minute, then verify:
kubectl top nodes
# Expected: NAME  CPU(cores)  CPU%  MEMORY(bytes)  MEMORY%
```

---

## 📋 Useful kind Commands Reference

```powershell
# List your clusters
kind get clusters

# Delete a cluster
kind delete cluster --name k8s-lab

# Load a local Docker image into kind (so pods can use it)
kind load docker-image my-app:local --name k8s-multinode

# Get the kubeconfig for a cluster
kind get kubeconfig --name k8s-multinode

# List nodes in a cluster
kind get nodes --name k8s-multinode
```

---

## 🗂️ Understanding kubeconfig

When you create a kind cluster, it automatically updates your `~/.kube/config` file (the **kubeconfig**). This file tells kubectl:
- Where your clusters are (API server URLs)
- What credentials to use
- What the current context is

```
kubeconfig structure:

clusters:          ← "Here are the clusters I know about"
  - name: kind-k8s-lab
    server: https://127.0.0.1:43861

users:             ← "Here are the credentials for each"
  - name: kind-k8s-lab
    client-certificate-data: ...
    client-key-data: ...

contexts:          ← "A context = cluster + user + default namespace"
  - name: kind-k8s-lab
    cluster: kind-k8s-lab
    user: kind-k8s-lab

current-context: kind-k8s-lab   ← "This is the active cluster"
```

**Important commands:**
```powershell
# See all contexts (clusters you can talk to)
kubectl config get-contexts

# Switch to a different cluster
kubectl config use-context kind-k8s-multinode

# See current context
kubectl config current-context

# See full kubeconfig file
kubectl config view
```

---

## 🔧 Optional But Recommended Tools

### kubectx + kubens (Fast Context/Namespace Switching)

```powershell
# Install via scoop
scoop install kubectx kubens

# Usage:
kubectx                          # List contexts
kubectx kind-k8s-multinode       # Switch context
kubens                           # List namespaces
kubens kube-system               # Switch default namespace
```

### stern (Multi-pod Log Tailing)

```powershell
scoop install stern

# Tail all pods matching a pattern
stern web-app                    # All pods with "web-app" in name
stern -n kube-system .           # All pods in kube-system namespace
```

---

## ✅ Environment Verification Checklist

Run through this checklist. If anything fails, fix it before moving to the homework:

```powershell
# 1. Docker is running
docker ps

# 2. kubectl is installed and points to your cluster
kubectl version
kubectl config current-context     # Should say "kind-k8s-multinode" or similar

# 3. Nodes are Ready
kubectl get nodes                  # All STATUS = Ready

# 4. System pods are running
kubectl get pods -n kube-system    # All STATUS = Running

# 5. You can describe a node
kubectl describe node <node-name>  # Should show detailed node info

# 6. kubectl explain works
kubectl explain pod                # Should show Pod documentation
```

**All green?** You're ready for the homework!

---

## 🧹 Cleanup When You're Done Learning

```powershell
# Delete all clusters when done for the day (saves resources)
kind delete clusters --all

# Or delete just one
kind delete cluster --name k8s-multinode

# Re-create anytime in seconds
kind create cluster --config d:\learning\k8s\phase-0-orientation\kind-config.yaml
```

> 💡 **The disposable cluster advantage:** Because kind clusters are just Docker containers, you can nuke your entire cluster and start fresh in 60 seconds. Don't be afraid to break things!
