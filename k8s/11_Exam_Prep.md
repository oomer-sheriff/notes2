# ☸️ CKA/CKAD Exam Prep

> "The exam is 2 hours, 15-20 tasks, performance-based (no MCQ). Speed is survival."

---

## 🎯 Which Cert Should You Take?

| Cert | Focus | Audience |
|------|-------|----------|
| **CKAD** | Designing and deploying apps | Developers |
| **CKA** | Administering clusters | Ops/DevOps |
| **CKS** | Security specialist | After CKA |

**Recommended order:** CKAD → CKA → CKS

---

## 🗂️ CKAD Exam Domains

| Domain | Weight | Key Topics |
|--------|--------|-----------|
| Application Design & Build | 20% | Multi-container pods, Jobs, CronJobs, init containers |
| Application Deployment | 20% | Rolling updates, Helm, Deployments |
| Application Observability | 15% | Logs, probes, metrics |
| Application Environment, Config, Security | 25% | ConfigMaps, Secrets, SecurityContext, ServiceAccounts |
| Services & Networking | 20% | Services, Ingress, NetworkPolicy |

## 🗂️ CKA Exam Domains

| Domain | Weight | Key Topics |
|--------|--------|-----------|
| Cluster Architecture, Installation & Config | 25% | kubeadm, etcd backup, RBAC, kubeconfig |
| Workloads & Scheduling | 15% | Deployments, DaemonSets, CronJobs, resource limits |
| Services & Networking | 20% | Services, Ingress, CoreDNS, CNI |
| Storage | 10% | PV/PVC, StorageClass |
| Troubleshooting | 30% | Debug nodes, pods, networking, logs |

---

## ⚡ Speed Drills — Do These Daily

The exam is time-pressured. You need muscle memory, not thinking.

### Imperative Commands (Fastest Way to Create Resources)

```bash
# Pod
kubectl run mypod --image=nginx --restart=Never

# Deployment
kubectl create deployment myapp --image=nginx --replicas=3

# Service (expose deployment)
kubectl expose deployment myapp --port=80 --type=ClusterIP

# Generate YAML without creating (DRY RUN = your best friend)
kubectl run mypod --image=nginx --dry-run=client -o yaml > pod.yaml
kubectl create deployment myapp --image=nginx --dry-run=client -o yaml > deploy.yaml

# Job
kubectl create job myjob --image=busybox -- echo "hello"

# CronJob
kubectl create cronjob mycron --image=busybox \
  --schedule="*/5 * * * *" -- echo "hello"

# ConfigMap
kubectl create configmap myconfig --from-literal=KEY=VALUE
kubectl create configmap myconfig --from-file=config.properties

# Secret
kubectl create secret generic mysecret --from-literal=password=abc123

# ServiceAccount
kubectl create serviceaccount mysa

# Role + RoleBinding
kubectl create role myrole --verb=get,list --resource=pods
kubectl create rolebinding myrb --role=myrole --serviceaccount=default:mysa
```

### Edit on the Fly
```bash
# Edit a running resource
kubectl edit deployment myapp

# Patch without opening editor
kubectl patch deployment myapp -p '{"spec":{"replicas":5}}'

# Replace (apply updated yaml)
kubectl replace -f deploy.yaml

# Scale quickly
kubectl scale deployment myapp --replicas=5

# Set image quickly
kubectl set image deployment/myapp nginx=nginx:1.25
```

---

## 🛠️ Exam Environment Setup (Do This at Exam Start)

```bash
# 1. Set up aliases — saves MINUTES
alias k=kubectl
export do="--dry-run=client -o yaml"
export now="--force --grace-period 0"

# 2. Enable kubectl autocompletion
source <(kubectl completion bash)
complete -F __start_kubectl k

# 3. Verify your context — ALWAYS check before each question
kubectl config current-context
kubectl config get-contexts

# 4. Switch context/namespace for each question
kubectl config use-context <context-name>
kubectl config set-context --current --namespace=<namespace>
```

---

## 🔧 Troubleshooting Playbook (CKA Heavy)

### Pod Won't Start
```bash
kubectl get pod <pod> -o yaml          # Full spec + status
kubectl describe pod <pod>             # Events section — most important
kubectl logs <pod>                     # Container logs
kubectl logs <pod> --previous          # Logs from dead container
kubectl logs <pod> -c <container>      # Multi-container pod
```

### Service Not Working
```bash
kubectl get svc <svc>                  # Check selector labels
kubectl get endpoints <svc>            # Are there endpoints? (If empty, selector mismatch)
kubectl get pod --show-labels          # Do pod labels match selector?
# Debug from inside cluster:
kubectl run test --image=curlimages/curl -it --rm -- curl http://<svc>.<ns>.svc.cluster.local
```

### Node Issues
```bash
kubectl get nodes                      # STATUS column
kubectl describe node <node>           # Conditions, events, allocatable resources
kubectl top nodes                      # Actual CPU/memory usage
# SSH into node (if allowed in exam):
journalctl -u kubelet -f               # kubelet logs
systemctl status kubelet               # Is kubelet running?
```

### Networking / DNS Issues
```bash
kubectl run dnstest --image=busybox -it --rm -- nslookup kubernetes
kubectl run nettest --image=nicolaka/netshoot -it --rm -- bash
# Inside netshoot: ping, curl, tcpdump, nslookup, dig all available
```

### etcd Backup/Restore (CKA Required)
```bash
# Backup
ETCDCTL_API=3 etcdctl snapshot save /backup/snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify
etcdctl snapshot status /backup/snapshot.db --write-out=table

# Restore
ETCDCTL_API=3 etcdctl snapshot restore /backup/snapshot.db \
  --data-dir /var/lib/etcd-restore
# Then update the etcd static pod manifest to point to new --data-dir
```

---

## 📋 Quick Reference Card

### Object Shortnames
```
po = pods
deploy = deployments
svc = services
ns = namespaces
cm = configmaps
sa = serviceaccounts
pv = persistentvolumes
pvc = persistentvolumeclaims
ing = ingress
netpol = networkpolicies
ds = daemonsets
rs = replicasets
sts = statefulsets
cj = cronjobs
```

### Most Used kubectl Flags
```
-n <namespace>       target namespace
-A / --all-namespaces all namespaces
-o yaml              output as YAML
-o wide              extra columns
-o jsonpath=         extract specific field
-o json | jq         pipe to jq
-w / --watch         live updates
--dry-run=client     don't apply, just show
--force --grace-period 0   instant delete
--show-labels        show all labels
--selector=          filter by label
--field-selector=    filter by field
```

### Useful JSONPath Examples
```bash
# Get pod IPs
kubectl get pods -o jsonpath='{.items[*].status.podIP}'

# Get container images
kubectl get pods -o jsonpath='{.items[*].spec.containers[*].image}'

# Get node names and status
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.conditions[-1].type}{"\n"}{end}'
```

---

## 📚 Exam Allowed Resources
**Only `kubernetes.io/docs` is allowed during the exam.**

Key pages to bookmark:
- https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- https://kubernetes.io/docs/concepts/services-networking/
- https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/

---

## 🧪 Mock Exam Resources

| Resource | Free? | Notes |
|----------|-------|-------|
| [Killer.sh](https://killer.sh) | ~$30 (or included with exam) | Hardest, most realistic |
| [KodeKloud Mock Exams](https://kodekloud.com) | Paid subscription | Great for both CKA+CKAD |
| [Killercoda CKAD Scenarios](https://killercoda.com/killer-shell-ckad) | Free | Good for targeted practice |
| [GitHub: dgkanatsios/CKAD-exercises](https://github.com/dgkanatsios/CKAD-exercises) | Free | Huge question bank |
| [GitHub: alijahnas/CKA-practice](https://github.com/alijahnas/CKA-practice-exercises) | Free | CKA-focused |

---

## 🏁 "Am I Ready?" Checklist

You're ready to book the exam when:

- [ ] You can create any object from scratch using only imperative commands (no copy-pasting YAML)
- [ ] You can debug a broken cluster and identify the root cause in < 5 minutes
- [ ] You've done killer.sh and scored > 70%
- [ ] You can perform an etcd backup and restore without notes (CKA)
- [ ] You've done at least 3 full timed mock exams
- [ ] You can switch context and namespace without thinking
- [ ] The official docs feel like home — you can find anything in < 60 seconds

**Good luck! You've got this. 🚀**
