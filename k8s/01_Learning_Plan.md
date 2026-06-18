# ☸️ Kubernetes Mastery — Complete Learning Plan

> **Philosophy:** Learn by doing. Every concept is paired with a hands-on task.  
> **Approach:** "Labs-first" — get your hands dirty before reading theory.  
> **Benchmark:** Can you do it without Googling in 2 minutes? That's mastery.

---

## 🏁 Prerequisites Checklist

Before touching K8s, make sure you have solid footing in:

| Skill | Why It Matters | Min Level Needed |
|-------|---------------|-----------------|
| Linux CLI | All K8s tooling is terminal-based | Comfortable |
| Docker / Containers | K8s orchestrates containers | Know how to build & run images |
| Networking basics | TCP/IP, DNS, ports, load balancing | Conceptual understanding |
| YAML | All K8s config is YAML | Must be able to write/read it |
| Git | GitOps phases require it | Basic add/commit/push |

**If you're shaky on any of these, spend time there first. K8s confusion is often really Docker or Linux confusion.**

---

## 📐 Environment Setup (Do This First!)

### Option A — Local (Recommended for Learning)

```bash
# Install Docker Desktop (includes WSL2 on Windows)
# Then install kind (Kubernetes IN Docker) — fast, free, no cloud needed
choco install kind          # Windows with Chocolatey
# OR
scoop install kind

# Install kubectl
choco install kubernetes-cli

# Install Helm
choco install kubernetes-helm

# Create your first cluster
kind create cluster --name k8s-lab
kubectl cluster-info
```

### Option B — Free Cloud Playgrounds
- **Killercoda:** https://killercoda.com/playgrounds/scenario/kubernetes  (best free option)
- **Play with Kubernetes:** https://labs.play-with-k8s.com/
- **Google Cloud Shell:** Has a 1-node K8s cluster free

### Verify Your Setup
```bash
kubectl get nodes          # Should show Ready
kubectl get pods -A        # Should show system pods running
kubectl version --client   # Should show v1.28+
```

---

# PHASE 0 — Orientation (Week 1)
**Goal:** Understand _what_ K8s is, _why_ it exists, and how the pieces fit together.

## 🧠 Concepts to Learn

### The "Why" of Kubernetes
- Problems before K8s: manual scaling, single points of failure, no self-healing
- What an orchestrator does: scheduling, health checks, service discovery, scaling
- K8s vs Docker Compose vs Docker Swarm

### The Architecture (MEMORIZE THIS)

```
┌─────────────────────────────────────────────────────┐
│                    CONTROL PLANE                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────┐ │
│  │ API      │  │ etcd     │  │ Controller Manager │ │
│  │ Server   │  │ (state)  │  │ (reconcile loops)  │ │
│  └──────────┘  └──────────┘  └────────────────────┘ │
│  ┌──────────────────────────────────────────────────┐ │
│  │          Scheduler (pod placement)               │ │
│  └──────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
         │ API calls          │ API calls
┌────────▼────────┐  ┌────────▼────────┐
│   WORKER NODE   │  │   WORKER NODE   │
│ ┌─────────────┐ │  │ ┌─────────────┐ │
│ │   kubelet   │ │  │ │   kubelet   │ │
│ │  kube-proxy │ │  │ │  kube-proxy │ │
│ │ container   │ │  │ │ container   │ │
│ │  runtime    │ │  │ │  runtime    │ │
│ └─────────────┘ │  │ └─────────────┘ │
│   [Pod][Pod]    │  │   [Pod][Pod]    │
└─────────────────┘  └─────────────────┘
```

### Key Mental Models
1. **Desired State vs Actual State** — K8s constantly reconciles these
2. **Everything is an object** — Pods, Deployments, Services are all API objects with spec/status
3. **Controllers watch and act** — The Deployment controller sees your desired replicas and makes it happen
4. **kubectl = API client** — It talks to the API server, not directly to nodes

## 📚 Resources
- 📺 **Watch:** "Kubernetes Explained in 15 Minutes" — TechWorld with Nana (YouTube)
- 📺 **Watch:** "Kubernetes Architecture Explained" — KodeKloud (YouTube)
- 📖 **Read:** https://kubernetes.io/docs/concepts/overview/
- 📖 **Read:** https://kubernetes.io/docs/concepts/architecture/

## 🏠 Homework — Phase 0

### Task P0-1: Architecture Diagram (30 min)
Draw the K8s architecture from memory on paper. Label every component.  
Write 1-2 sentences on what each component does.  
**Done when:** You can explain it to someone else without notes.

### Task P0-2: Play with kubectl (1 hr)
```bash
# Explore a real cluster (use Killercoda if no local setup yet)
kubectl get nodes -o wide
kubectl get pods --all-namespaces
kubectl describe node <node-name>
kubectl explain pod
kubectl explain pod.spec
kubectl explain pod.spec.containers
```
**Done when:** You understand what `kubectl explain` does and have read the node description.

---

# PHASE 1 — Core Objects (Weeks 2-3)
**Goal:** Create, manage, and understand Pods, Deployments, ReplicaSets, and Services.

## 🧠 Concepts to Learn

### Pods
- The atomic unit of K8s — one or more containers that share network/storage
- Pod lifecycle: Pending → Running → Succeeded/Failed
- Init containers vs regular containers
- Multi-container pod patterns: Sidecar, Ambassador, Adapter

### ReplicaSets & Deployments
- ReplicaSet: ensures N copies of a pod are always running
- Deployment: manages ReplicaSets, adds rolling updates + rollback
- Rolling update strategy vs Recreate strategy
- `maxSurge` and `maxUnavailable`

### Services
- Why Services exist: pod IPs are ephemeral, Services give a stable endpoint
- **ClusterIP** — internal only, default
- **NodePort** — exposes on every node's IP:port (30000-32767)
- **LoadBalancer** — provisions a cloud LB (or MetalLB locally)
- **ExternalName** — DNS alias to external service
- How kube-proxy makes Services work (iptables/IPVS)

### Namespaces
- Virtual clusters within a cluster
- Resource isolation, quota, RBAC scope
- `default`, `kube-system`, `kube-public`, `kube-node-lease`

## 📚 Resources
- 📖 **Read:** https://kubernetes.io/docs/concepts/workloads/pods/
- 📖 **Read:** https://kubernetes.io/docs/concepts/workloads/controllers/deployment/
- 📖 **Read:** https://kubernetes.io/docs/concepts/services-networking/service/
- 📺 **Watch:** KodeKloud "Core Concepts" section (free on YouTube)

## 🏠 Homework — Phase 1

### Task P1-1: Pod Lifecycle Lab (2 hrs)
```yaml
# Create this file: nginx-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: web
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "100m"
      limits:
        memory: "128Mi"
        cpu: "200m"
```
**Tasks:**
1. Apply it, watch it come up: `kubectl get pods -w`
2. Exec into it: `kubectl exec -it nginx-pod -- bash`
3. View logs: `kubectl logs nginx-pod`
4. Delete and recreate — notice pod IP changes
5. Add an `initContainer` that runs `echo "init done"` before nginx starts

**Done when:** You can explain what happened at each step.

### Task P1-2: Deployment + Rolling Update (2 hrs)
```yaml
# Create: web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.24   # deliberately old version
        ports:
        - containerPort: 80
```
**Tasks:**
1. Deploy it, verify 3 pods are running
2. Update image to `nginx:1.25` and watch the rollout: `kubectl rollout status deploy/web-app`
3. Roll back: `kubectl rollout undo deploy/web-app`
4. Scale up to 5 replicas: `kubectl scale deploy/web-app --replicas=5`
5. Check rollout history: `kubectl rollout history deploy/web-app`

### Task P1-3: Services Lab (2 hrs)
1. Expose your deployment as a ClusterIP service
2. Expose it as a NodePort service
3. Use `kubectl port-forward` to access ClusterIP locally
4. Use `kubectl run curl-pod --image=curlimages/curl -it --rm -- sh` and curl the ClusterIP service from inside the cluster
5. **Challenge:** Create a second deployment (busybox) and make it talk to the nginx service by DNS name

**Done when:** You understand why internal DNS (`web-app.default.svc.cluster.local`) works.

### Task P1-4: Namespace Isolation (1 hr)
```bash
kubectl create namespace dev
kubectl create namespace prod
# Deploy the same app in both namespaces
kubectl apply -f web-deployment.yaml -n dev
kubectl apply -f web-deployment.yaml -n prod
# Verify isolation
kubectl get pods -n dev
kubectl get pods -n prod
kubectl get pods  # default namespace — should be empty
```

---

# PHASE 2 — Configuration & Secrets (Weeks 4-5)
**Goal:** Manage app config properly — no hardcoded values, no leaked secrets.

## 🧠 Concepts to Learn

### ConfigMaps
- Store non-sensitive config data as key-value pairs or files
- Mount as environment variables or volume (file)
- When to use each approach

### Secrets
- Base64 encoded (NOT encrypted by default — know this!)
- Types: Opaque, docker-registry, TLS, service-account-token
- Encryption at rest with KMS providers
- External secret managers: Vault, AWS Secrets Manager, External Secrets Operator

### Resource Requests & Limits
- `requests`: what the scheduler guarantees
- `limits`: hard cap (OOMKilled if exceeded)
- QoS classes: Guaranteed, Burstable, BestEffort
- Why Limits ≠ Requests is often correct

### Health Probes
- **livenessProbe**: restart container if unhealthy
- **readinessProbe**: remove from Service endpoints if not ready
- **startupProbe**: protect slow-starting apps from liveness killing them
- Probe types: HTTP, TCP, exec

## 📚 Resources
- 📖 https://kubernetes.io/docs/concepts/configuration/configmap/
- 📖 https://kubernetes.io/docs/concepts/configuration/secret/
- 📖 https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- 📖 https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/

## 🏠 Homework — Phase 2

### Task P2-1: ConfigMap & Secret Lab (2 hrs)
Build a Python/Node app (or use a pre-built image) that reads config from env vars:

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_HOST: "postgres.default.svc.cluster.local"
  DATABASE_PORT: "5432"
  LOG_LEVEL: "info"
  app.properties: |
    server.port=8080
    feature.dark-mode=true
---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:          # K8s auto-encodes to base64
  DATABASE_PASSWORD: "supersecret123"
  API_KEY: "sk-abc123xyz"
```

Mount both as environment variables AND as files in a volume. Verify inside the pod.

### Task P2-2: Health Probes Lab (2 hrs)
1. Deploy nginx with a `readinessProbe` on HTTP port 80
2. Temporarily break it: `kubectl exec <pod> -- rm /usr/share/nginx/html/index.html`
3. Watch the pod leave the Service endpoints: `kubectl get endpoints`
4. Restore the file — watch it rejoin
5. **Challenge:** Set a `livenessProbe` that runs a command. Make it fail intentionally and observe pod restarts.

### Task P2-3: Resource Management (1 hr)
1. Set requests and limits on your deployment
2. Use `kubectl top pods` (requires metrics-server) to see actual usage
3. Intentionally trigger an OOMKill: use a stress-test container with a memory limit of 50Mi
4. Observe `kubectl describe pod` — find the OOMKilled reason

---

# PHASE 3 — Networking Deep Dive (Weeks 6-7)
**Goal:** Understand how traffic actually flows in and out of a cluster.

## 🧠 Concepts to Learn

### Cluster Networking Fundamentals
- Every pod gets its own IP (flat network model)
- Pod-to-pod communication (same node vs. cross-node)
- CNI plugins: Flannel (simple), Calico (NetworkPolicy), Cilium (eBPF)

### DNS in Kubernetes (CoreDNS)
- Pod DNS format: `<pod-ip-dashes>.<namespace>.pod.cluster.local`
- Service DNS: `<service>.<namespace>.svc.cluster.local`
- Headless services (StatefulSet use case)

### Ingress
- Ingress resource vs Ingress Controller (NGINX, Traefik, AWS ALB)
- Path-based routing (`/api` → api-service, `/` → frontend-service)
- Host-based routing (`api.example.com` vs `app.example.com`)
- TLS termination with cert-manager

### Network Policies
- Default: all pods can talk to all pods (open!)
- NetworkPolicy = firewall rules at the CNI level
- Ingress rules (who can reach this pod)
- Egress rules (where this pod can go)
- Requires a CNI that supports it (Calico, Cilium, Weave)

## 📚 Resources
- 📖 https://kubernetes.io/docs/concepts/services-networking/
- 📖 https://kubernetes.io/docs/concepts/services-networking/network-policies/
- 📖 https://kubernetes.io/docs/concepts/services-networking/ingress/
- 📺 **Watch:** "Kubernetes Networking Explained" — TechWorld with Nana

## 🏠 Homework — Phase 3

### Task P3-1: DNS Discovery (1 hr)
```bash
# Launch a debug pod
kubectl run dnsutils --image=gcr.io/kubernetes-e2e-test-images/dnsutils:1.3 \
  --restart=Never -it --rm -- sh

# Inside the pod:
nslookup kubernetes.default
nslookup <your-service-name>.<namespace>.svc.cluster.local
cat /etc/resolv.conf
```
**Done when:** You can explain what `ndots:5` means and how K8s DNS search domains work.

### Task P3-2: Ingress Lab (3 hrs)
1. Install NGINX Ingress Controller in your kind cluster
2. Deploy two apps: "frontend" (nginx) and "api" (httpd or any other)
3. Write an Ingress resource that routes:
   - `/` → frontend service
   - `/api` → api service
4. Test by curling with the correct Host header
5. **Challenge:** Add a second Ingress for a different hostname and use TLS with a self-signed cert

### Task P3-3: Network Policy (2 hrs)
```yaml
# Deny all ingress to a namespace, then add specific allows
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: production
spec:
  podSelector: {}  # matches ALL pods
  policyTypes:
  - Ingress
  - Egress
```
1. Apply the deny-all policy to a namespace
2. Verify: a pod in another namespace can no longer curl your app
3. Add a policy that ONLY allows traffic from pods with label `role: frontend`
4. Verify the allow works, but everything else is still blocked

---

# PHASE 4 — Storage & Stateful Apps (Weeks 8-9)
**Goal:** Run databases and stateful workloads properly.

## 🧠 Concepts to Learn

### Volume Basics
- `emptyDir` — temporary, pod-lifetime storage
- `hostPath` — dangerous, mounts host directory
- `configMap` / `secret` volumes — we already know these

### PersistentVolumes (PV) & PersistentVolumeClaims (PVC)
- PV: the actual storage resource (admin creates)
- PVC: the claim/request (developer creates)
- Access modes: ReadWriteOnce, ReadOnlyMany, ReadWriteMany
- Reclaim policies: Delete, Retain, Recycle

### StorageClasses & Dynamic Provisioning
- StorageClass = a "profile" for how to provision storage
- Dynamic provisioning: PVC automatically creates PV via StorageClass
- Cloud: `gp2` (AWS EBS), `standard` (GCP PD)
- Local: `local-path-provisioner` for kind/minikube

### StatefulSets
- Pods get stable, predictable names: `db-0`, `db-1`, `db-2`
- Pods get their own PVC that persists across restarts
- Ordered creation and deletion (crucial for databases)
- Headless service for direct pod DNS access

## 🏠 Homework — Phase 4

### Task P4-1: Stateful PostgreSQL (3 hrs)
Deploy a single-node PostgreSQL using a StatefulSet with PVC:

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        env:
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: POSTGRES_DB
          value: myapp
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 1Gi
```
1. Deploy it, create a table, insert data
2. Delete the pod (not the StatefulSet): `kubectl delete pod postgres-0`
3. Watch it come back — verify your data is still there!
4. **Done when:** You understand why data survived pod deletion.

### Task P4-2: Storage Destruction Test (1 hr)
1. Delete the StatefulSet (NOT the PVC)
2. Verify PVC still exists: `kubectl get pvc`
3. Redeploy the StatefulSet — verify data is still there
4. Now delete the PVC too, redeploy — what happens? Why?

---

# PHASE 5 — Security & RBAC (Weeks 10-11)
**Goal:** Lock down your cluster. Understand the identity system.

## 🧠 Concepts to Learn

### Authentication vs Authorization
- K8s doesn't manage user accounts — it uses certificates/tokens
- ServiceAccounts = K8s-native identities for pods
- Authentication: Who are you? (certs, OIDC, static tokens)
- Authorization: What can you do? (RBAC)

### RBAC (Role-Based Access Control)
- **Role** — permissions within a namespace
- **ClusterRole** — permissions cluster-wide
- **RoleBinding** — grants a Role to a user/group/SA in a namespace
- **ClusterRoleBinding** — grants a ClusterRole cluster-wide
- Verbs: get, list, watch, create, update, patch, delete

### Pod Security
- **SecurityContext** — per-pod/container security settings
  - `runAsUser`, `runAsNonRoot`, `readOnlyRootFilesystem`
  - `capabilities` (drop ALL, add specific ones)
- **Pod Security Standards** (PSA) — Restricted, Baseline, Privileged
- Secrets encryption at rest

## 📚 Resources
- 📖 https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- 📖 https://kubernetes.io/docs/concepts/security/
- 📖 https://kubernetes.io/docs/tasks/configure-pod-container/security-context/

## 🏠 Homework — Phase 5

### Task P5-1: RBAC Lab (3 hrs)
Create a "developer" ServiceAccount that can only:
- `get`, `list`, `watch` pods in the `dev` namespace
- `create`, `update`, `delete` deployments in the `dev` namespace
- Cannot do ANYTHING in `prod` namespace

```bash
# Test your RBAC with impersonation
kubectl auth can-i get pods --namespace=dev \
  --as=system:serviceaccount:dev:developer
kubectl auth can-i delete pods --namespace=prod \
  --as=system:serviceaccount:dev:developer
```
**Done when:** All `can-i` checks return the expected yes/no.

### Task P5-2: Least-Privilege Pod (2 hrs)
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```
1. Apply these security contexts to your nginx pod
2. nginx will fail (needs to write to `/var/run` and `/var/cache/nginx`) — debug and fix using emptyDir volumes
3. Verify the pod runs as a non-root user: `kubectl exec <pod> -- id`

### Task P5-3: Secret Scanning (1 hr)
1. Encode a secret and store it in a K8s Secret
2. Retrieve the base64 value and decode it manually — prove it's NOT encrypted
3. Research: how would you enable KMS encryption at rest? Write a 1-page summary.

---

# PHASE 6 — Scheduling & Autoscaling (Week 12)
**Goal:** Control where pods run and automate scaling.

## 🧠 Concepts to Learn

### Scheduling Controls
- **nodeSelector** — simple label-based node selection
- **nodeAffinity** — flexible rules (required vs preferred)
- **podAffinity / podAntiAffinity** — schedule near/away from other pods
- **Taints & Tolerations** — mark nodes as special (GPU, spot), pods must tolerate
- **PriorityClasses** — critical pods evict lower-priority ones

### Autoscaling
- **HPA** (Horizontal Pod Autoscaler) — scales pod count based on metrics
- **VPA** (Vertical Pod Autoscaler) — adjusts CPU/memory requests
- **KEDA** — event-driven scaling (queue depth, Kafka lag, etc.)
- **Cluster Autoscaler** — adds/removes nodes based on pending pods

## 🏠 Homework — Phase 6

### Task P6-1: HPA Lab (2 hrs)
1. Install metrics-server: `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
2. Create an HPA that scales your deployment from 1 to 10 pods when CPU > 50%:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```
3. Generate load: `kubectl run load-gen --image=busybox --rm -it -- sh -c "while true; do wget -q -O- http://web-app; done"`
4. Watch the HPA scale up: `kubectl get hpa -w`

### Task P6-2: Affinity Lab (2 hrs)
1. Label a node: `kubectl label node <node> disktype=ssd`
2. Deploy a pod with `nodeAffinity` requiring `disktype=ssd`
3. Deploy a pod with `podAntiAffinity` — ensure replicas land on different nodes
4. Add a taint to a node and create a pod that tolerates it

---

# PHASE 7 — Observability (Week 13)
**Goal:** Know what your cluster is doing. Debug like a pro.

## 🧠 Concepts to Learn

### Metrics (Prometheus + Grafana)
- Prometheus scrapes `/metrics` endpoints
- Service monitors via prometheus-operator
- Alertmanager for routing alerts
- Grafana dashboards for visualization

### Logging (EFK/PLG Stack)
- **EFK:** Elasticsearch + Fluentd + Kibana
- **PLG:** Promtail + Loki + Grafana (lighter weight, better for K8s)
- DaemonSet-based log collection

### Tracing
- Distributed tracing with OpenTelemetry + Jaeger/Tempo
- Trace context propagation between services

### Debugging Techniques
```bash
# Pod stuck in Pending?
kubectl describe pod <pod>   # look at Events section

# CrashLoopBackOff?
kubectl logs <pod> --previous

# Network issue?
kubectl run debug --image=nicolaka/netshoot -it --rm

# Node issues?
kubectl top nodes
kubectl describe node <node>
```

## 🏠 Homework — Phase 7

### Task P7-1: Prometheus + Grafana Stack (3 hrs)
```bash
# Deploy kube-prometheus-stack via Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
# Login: admin/prom-operator
```
1. Explore the pre-built dashboards (Kubernetes / Compute Resources / Cluster)
2. Find your nginx pods in the metrics
3. Create a custom alert: fire if any pod has >3 restarts in 5 minutes

### Task P7-2: Debugging Gauntlet (2 hrs)
I'll give you broken manifests — fix them all:

**Broken #1:** Pod stuck in `ImagePullBackOff` — wrong image name  
**Broken #2:** Pod in `CrashLoopBackOff` — app crashes on startup  
**Broken #3:** Service not routing traffic — selector mismatch  
**Broken #4:** Pod stuck in `Pending` — insufficient resources  
**Broken #5:** Ingress returning 503 — backend not ready

Create these broken scenarios yourself and then fix them. Document the debug commands you used.

---

# PHASE 8 — GitOps & CI/CD (Weeks 14-15)
**Goal:** Never run `kubectl apply` by hand again.

## 🧠 Concepts to Learn

### Helm
- Package manager for K8s — templatized YAML
- Chart structure: `Chart.yaml`, `values.yaml`, `templates/`
- Overriding values: `helm install -f custom-values.yaml`
- Helm hooks for database migrations

### ArgoCD (GitOps)
- Continuous Delivery: cluster state defined in Git
- Detects drift and syncs automatically
- App of Apps pattern for managing multiple apps
- Sync waves and hooks

### CI/CD Pipeline
- GitHub Actions → build image → push to registry → update K8s manifest
- Image tag strategy: commit SHA vs semver

## 🏠 Homework — Phase 8

### Task P8-1: Build Your Own Helm Chart (3 hrs)
```bash
helm create my-webapp
# Edit templates/, values.yaml
helm install my-webapp ./my-webapp --values custom-values.yaml
helm upgrade my-webapp ./my-webapp --set image.tag=v2
helm rollback my-webapp 1
```
Create a Helm chart for your nginx deployment that supports:
- Configurable replica count
- Configurable image tag
- Toggle for HPA (enabled: true/false)
- Toggle for Ingress with configurable hostname

### Task P8-2: ArgoCD GitOps Setup (4 hrs)
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
1. Push your Helm chart to a GitHub repo
2. Create an ArgoCD Application pointing at it
3. Change a value in Git (e.g., replica count)
4. Watch ArgoCD detect the drift and sync it
5. **Done when:** You NEVER need to touch kubectl to deploy

---

# PHASE 9 — Advanced Topics (Weeks 16-18)
**Goal:** Understand K8s internals. Build extensions. Run production-grade workloads.

## 🧠 Concepts to Learn

### etcd Internals
- Raft consensus algorithm basics
- etcd backup: `etcdctl snapshot save`
- etcd restore: disaster recovery procedure
- What happens when etcd is unhealthy: API server becomes read-only

### Admission Controllers & Webhooks
- MutatingAdmissionWebhook: modify objects before persistence
- ValidatingAdmissionWebhook: reject invalid objects
- Examples: auto-inject sidecars, enforce labels, block latest tags

### Custom Resources & Operators
- CRD (CustomResourceDefinition): extend the K8s API
- Controller pattern: Watch → Reconcile → Act
- Operator = CRD + Controller (manages stateful app lifecycle)
- Tools: controller-runtime, Kubebuilder, Operator SDK

### Service Mesh (Istio/Linkerd)
- mTLS between all services automatically
- Traffic management: canary, A/B, circuit breaker
- Observability: distributed tracing, service graph
- Ambient mode vs sidecar mode

## 🏠 Homework — Phase 9

### Task P9-1: etcd Backup/Restore (2 hrs)
```bash
# Backup etcd (in a kubeadm cluster)
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

etcdctl snapshot status /backup/etcd-snapshot.db
```
1. Take a snapshot
2. Deploy some resources
3. Restore from snapshot
4. Verify those resources are gone (pre-backup state restored)

### Task P9-2: Build a Custom Operator (5 hrs — The Boss Fight)
Using Kubebuilder or the Operator SDK, build an operator that manages a `WebApp` CRD:
```yaml
apiVersion: myapps.io/v1
kind: WebApp
metadata:
  name: my-site
spec:
  image: nginx:latest
  replicas: 3
  port: 80
```
When this resource is created, your operator automatically creates:
- A Deployment with the specified image and replicas
- A ClusterIP Service exposing the port
When the CRD is deleted, cleanup happens automatically.

### Task P9-3: Istio Service Mesh (3 hrs)
```bash
# Install Istio
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled
```
1. Deploy the Bookinfo sample app
2. View the service graph in Kiali
3. Create a VirtualService that sends 10% of traffic to a v2 canary
4. Verify mTLS is active between all services

---

# PHASE 10 — Capstone Projects + Exam Prep (Weeks 19-22)
**See [10_Projects.md](./10_Projects.md) for full project specs.**

---

## 📊 Weekly Cadence (Template)

```
Monday    — Read/Watch: New concepts (1.5 hrs)
Tuesday   — Lab: Apply the concepts hands-on (2 hrs)
Wednesday — Review: Re-read docs, take notes (1 hr)
Thursday  — Lab: More complex version of Tuesday's lab (2 hrs)
Friday    — Homework project: Build something (2 hrs)
Weekend   — Review flashcards, light reading, community forums (1 hr)
```

---

## 🔗 Master Resource List

### Primary Learning
| Resource | Type | Cost | Best For |
|----------|------|------|----------|
| [KodeKloud](https://kodekloud.com) | Course + Labs | Paid ($20/mo) | Best overall, CKA/CKAD prep |
| [Killercoda](https://killercoda.com) | Browser Labs | Free | Quick practice scenarios |
| [kubernetes.io/docs](https://kubernetes.io/docs) | Official Docs | Free | Authoritative reference |
| [TechWorld with Nana](https://www.youtube.com/@TechWorldwithNana) | YouTube | Free | Excellent explanations |
| [40DaysOfKubernetes](https://github.com/40daysofkubernetes) | GitHub Course | Free | Structured free learning |

### Practice & Exams
| Resource | Type | Cost | Best For |
|----------|------|------|----------|
| [Killer.sh](https://killer.sh) | Exam Simulator | ~$30 | CKA/CKAD simulation |
| [KodeKloud Mock Exams](https://kodekloud.com) | Mock Exams | Paid | CKA/CKAD practice |

### Tools You'll Use
- `kind` — local K8s clusters
- `k9s` — terminal UI for K8s (install it, love it)
- `kubectx` + `kubens` — fast context/namespace switching
- `stern` — multi-pod log tailing
- `kubectl neat` — clean YAML output
