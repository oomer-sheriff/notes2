# Homework P0-2 — kubectl Exploration Lab

> **Time:** 1–1.5 hours  
> **Prerequisites:** A working kind cluster (from `04_environment_setup.md`)  
> **Rule:** Don't copy-paste commands. Type every one. Your fingers need to learn this too.

---

## 🚀 Setup — Start Your Cluster

```powershell
# Make sure Docker Desktop is running first, then:
kind create cluster --config d:\learning\k8s\phase-0-orientation\kind-config.yaml

# Verify it's up
kubectl get nodes
# Expected: 3 nodes (1 control-plane, 2 workers) all STATUS=Ready
```

If you already have the cluster running:
```powershell
kubectl config use-context kind-k8s-multinode
kubectl get nodes
```

---

## 🔍 Part 1 — Explore the System (20 min)

**Task 1.1:** List all pods across ALL namespaces and answer these questions:

```powershell
kubectl get pods --all-namespaces -o wide
```

Fill in this table from the output:

| Question | Your Answer |
|----------|------------|
| How many pods are in `kube-system`? | |
| What node is the etcd pod on? | |
| What node is the kube-scheduler on? | |
| What is the IP of the coredns pods? | |
| Are there any pods in the `default` namespace? | |

---

**Task 1.2:** Describe the control-plane node:

```powershell
kubectl describe node k8s-multinode-control-plane
```

Find and write down:

| Question | Your Answer |
|----------|------------|
| What is the node's internal IP? | |
| How many CPUs are allocatable? | |
| How much memory is allocatable? | |
| What OS and kernel version is it running? | |
| What container runtime is it using? | |
| What pods are currently scheduled on it? | |

---

**Task 1.3:** Inspect the API Server pod:

```powershell
kubectl describe pod kube-apiserver-k8s-multinode-control-plane -n kube-system
```

Find the `Events` section and the `Command` section. Write down:
- 3 flags the API server is running with
- What TLS cert files does it use?

---

## 🏗️ Part 2 — Your First Pod (25 min)

**Task 2.1:** Create a pod from the command line (no YAML file):

```powershell
kubectl run my-first-pod --image=nginx:1.25
```

Now investigate it:

```powershell
# Watch it come alive (Ctrl+C when Running)
kubectl get pods -w

# Once Running, get full details
kubectl get pod my-first-pod -o wide

# Describe it — read EVERY section
kubectl describe pod my-first-pod
```

Answer these questions:

| Question | Your Answer |
|----------|------------|
| What node did the scheduler pick? | |
| What is the pod's IP address? | |
| What event happened first? (look at Events) | |
| How long did the image pull take? | |
| What is the READY count showing (e.g., 1/1)? | |

---

**Task 2.2:** Get inside the pod and explore:

```powershell
kubectl exec -it my-first-pod -- bash
```

Inside the container, run these commands and write what they return:

```bash
# Inside the container:
hostname                          # What is the hostname?
cat /etc/hostname                 # Same as hostname?
ip addr show                      # What IP does the container see?
cat /etc/resolv.conf              # What DNS config does K8s inject?
env | grep KUBERNETES             # What env vars does K8s inject?
ls /etc/nginx/                    # What files are in nginx config?
exit                              # Back to Windows
```

**Key observation:** Compare the pod's IP (from `kubectl get pod -o wide`) with the IP you saw inside the container (`ip addr show`). They should match. This is the pod's "flat network" — the container sees the same IP that K8s assigned.

---

**Task 2.3:** View and follow the logs:

```powershell
# Get the nginx access log
kubectl logs my-first-pod

# Follow live (Ctrl+C to stop)
kubectl logs -f my-first-pod
```

In a SECOND terminal, generate a log entry:

```powershell
kubectl port-forward pod/my-first-pod 8080:80
# In browser: http://localhost:8080
# Or: curl http://localhost:8080
```

Go back to the first terminal — you should see a log line appear live.

---

## 🔬 Part 3 — kubectl explain Deep Dive (15 min)

**Task 3.1:** Use `kubectl explain` to look up 3 fields you haven't learned yet:

```powershell
# Start broad
kubectl explain pod

# Drill down
kubectl explain pod.spec
kubectl explain pod.spec.containers
kubectl explain pod.spec.containers.livenessProbe
kubectl explain pod.spec.containers.resources
kubectl explain pod.spec.tolerations
```

For each of these, write a one-line explanation in your own words:

| Field | What It Does (your words) |
|-------|--------------------------|
| `pod.spec.restartPolicy` | |
| `pod.spec.containers.imagePullPolicy` | |
| `pod.spec.containers.resources.requests` | |
| `pod.spec.containers.resources.limits` | |
| `pod.spec.hostNetwork` | |

---

**Task 3.2:** Generate a pod YAML template without creating anything:

```powershell
kubectl run template-pod --image=nginx --dry-run=client -o yaml
```

Read through the output. Notice:
- The fields K8s would add automatically (like `creationTimestamp: null`)
- The structure: apiVersion, kind, metadata, spec
- Where would you add resource limits?
- Where would you add labels?

Save this as a YAML file to reference:
```powershell
kubectl run template-pod --image=nginx --dry-run=client -o yaml > d:\learning\k8s\phase-0-orientation\homework\pod-template.yaml
```

---

## 🧹 Part 4 — Cleanup and Verification (5 min)

```powershell
# Delete what you created
kubectl delete pod my-first-pod

# Verify it's gone
kubectl get pods

# List all resources in default namespace
kubectl get all

# The namespace should be empty now (except for the kubernetes service)
```

---

## 📝 Lab Report

Fill this in before marking the homework complete:

**What I learned:**
```
(Write 3-5 sentences about what surprised you or what was new)
```

**Commands I struggled with:**
```
(Be honest — which commands needed multiple tries?)
```

**Questions I still have:**
```
(Write any confusion or "why does it work this way?" moments)
```

---

## ✅ Done When:

- [ ] Cluster is running with 3 nodes
- [ ] All tables above are filled in
- [ ] You went inside a container with `kubectl exec`
- [ ] You watched live logs while generating traffic
- [ ] You ran `kubectl explain` on at least 5 different fields
- [ ] You generated a YAML template with `--dry-run=client -o yaml`
- [ ] `pod-template.yaml` file exists in your homework folder
- [ ] Lab Report is written

---

## 🎯 Bonus Challenges (Optional)

If you finished early and want more:

**Bonus 1:** Create a pod with a custom label and then use a label selector to find it:
```powershell
kubectl run labeled-pod --image=nginx --labels="team=frontend,env=dev"
kubectl get pods -l team=frontend
kubectl get pods -l env=dev,team=frontend
```

**Bonus 2:** See the raw API response (this is what kubectl actually receives):
```powershell
kubectl get pods -o json | python -m json.tool | head -60
# Or without Python:
kubectl get pod my-first-pod -o json
```

**Bonus 3:** Watch events cluster-wide in real time:
```powershell
kubectl get events --sort-by='.lastTimestamp' -w
# In another terminal, create and delete a pod
kubectl run test-pod --image=nginx
kubectl delete pod test-pod
# Watch the events appear!
```
