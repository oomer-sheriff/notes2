# ☸️ Kubernetes Capstone Projects

> These are real-world, portfolio-worthy builds.  
> Each one tests multiple K8s domains at once.  
> **Do them in order** — each one builds on the last.

---

## 🏗️ Project 1 — "Hello, Cluster" (Week 3)
**Difficulty:** ⭐  
**Time:** ~4 hours  
**Tests:** Pods, Deployments, Services, namespaces

### What You'll Build
A multi-tier web app (frontend + backend) deployed across two namespaces with proper service communication.

### Requirements
- [ ] `frontend` namespace: Deploy an NGINX pod serving a custom HTML page
- [ ] `backend` namespace: Deploy a simple API (use `hashicorp/http-echo` or similar)
- [ ] Frontend can reach the backend API using K8s DNS
- [ ] Both apps are exposed via Services
- [ ] All resources have `labels`, `requests`, and `limits` set

### Architecture
```
User
 │
 ▼
frontend-service (NodePort)
 │
frontend-pod (nginx, custom HTML)
 │ (HTTP call to backend API)
 ▼
backend-service (ClusterIP)
 │
backend-pod (http-echo)
```

### Acceptance Criteria
- `kubectl get pods -A` shows all pods `Running`
- `curl http://<node-ip>:<nodeport>` returns the frontend HTML
- From inside the frontend pod, `curl http://backend-service.backend.svc.cluster.local` returns API response
- Each pod has resource requests/limits and a readinessProbe
- Deleting the frontend pod auto-recreates it (Deployment handles this)

### Bonus Challenges
- Add a ConfigMap to manage the NGINX config without rebuilding the image
- Add an initContainer that waits for the backend to be ready before starting nginx

---

## 🏗️ Project 2 — "The Twelve-Factor App" (Week 7)
**Difficulty:** ⭐⭐  
**Time:** ~8 hours  
**Tests:** Config, Secrets, Ingress, Health Probes, NetworkPolicy

### What You'll Build
A production-style deployment of a 3-tier app (web + api + database) following 12-factor app principles.

### Stack
- **Frontend:** NGINX (or any static site)
- **API:** A simple Node.js/Go/Python REST API (find a sample on DockerHub)
- **Database:** PostgreSQL (StatefulSet)

### Requirements
- [ ] All sensitive config (DB password, API keys) in Secrets, never in env vars directly in YAML
- [ ] All non-sensitive config (DB host, port, log level) in ConfigMaps
- [ ] Ingress routes:
  - `app.localhost/` → frontend
  - `app.localhost/api` → api service
- [ ] TLS terminated at Ingress (self-signed cert is fine)
- [ ] PostgreSQL uses a PVC for data persistence
- [ ] All 3 tiers have `readinessProbe` and `livenessProbe`
- [ ] NetworkPolicy: API can only accept traffic from frontend; DB only from API

### Acceptance Criteria
- [ ] Destroy and recreate the DB pod — data still exists
- [ ] `kubectl auth can-i` proves NetworkPolicy is enforced (use a debug pod)
- [ ] All health probe endpoints return 200
- [ ] Secrets are not visible in pod spec YAML (they should be referenced, not embedded)

---

## 🏗️ Project 3 — "Chaos & Resilience" (Week 9)
**Difficulty:** ⭐⭐⭐  
**Time:** ~6 hours  
**Tests:** HPA, PodDisruptionBudgets, Affinity, Resource Management

### What You'll Build
Make your Project 2 cluster survive chaos. Then prove it.

### Requirements
- [ ] **HPA** on the API tier (scale from 2 to 20 replicas at 60% CPU)
- [ ] **PodDisruptionBudget** — ensure at least 50% of API pods are always available
- [ ] **PodAntiAffinity** on the API — replicas must spread across different nodes
- [ ] **PriorityClass** — mark database as `high-priority`, frontend as `low-priority`

### Chaos Experiments
Run each test and document what happened and why:

1. **Node drain:** `kubectl drain <node> --ignore-daemonsets` — do your pods reschedule?
2. **Load test:** Generate traffic until HPA fires. Watch it scale up AND back down.
3. **Kill pods:** `kubectl delete pod -l app=api` — do they come back? How fast?
4. **Kill DB pod:** Does the PVC keep data? How long until the app recovers?
5. **Resource starvation:** Deploy a "noisy neighbor" pod consuming 80% CPU. Does your app survive?

### Acceptance Criteria
A written `chaos-report.md` documenting:
- What you broke
- What K8s did automatically to recover
- What required manual intervention and why

---

## 🏗️ Project 4 — "Zero Trust Security Audit" (Week 11)
**Difficulty:** ⭐⭐⭐  
**Time:** ~6 hours  
**Tests:** RBAC, SecurityContext, PodSecurity, Audit Logs

### What You'll Build
Lock down your cluster from Project 2 using defense-in-depth.

### Requirements
- [ ] **Namespace PSA labels:** Set `pod-security.kubernetes.io/enforce: restricted` on the `production` namespace
- [ ] Fix any pods that violate the Restricted policy (non-root, no privilege escalation, etc.)
- [ ] Create RBAC roles:
  - `developer-role` — deploy to `dev` namespace only
  - `ops-role` — deploy to any namespace, view secrets in `prod`
  - `readonly-role` — only list/get, no creates
- [ ] All pods run as non-root with `readOnlyRootFilesystem: true`
- [ ] No pods use `serviceAccountName: default` — each tier has its own SA with least-privilege RBAC

### Acceptance Criteria
Run these checks and paste the output in your README:
```bash
# No pods running as root
kubectl get pods -o json | jq '.items[].spec.containers[].securityContext'

# Check all SAs have minimal permissions
kubectl auth can-i --list --as=system:serviceaccount:prod:api-sa

# PSA enforced — this should FAIL:
kubectl run bad-pod --image=nginx --privileged=true -n production
```

---

## 🏗️ Project 5 — "Full Observability Stack" (Week 13)
**Difficulty:** ⭐⭐⭐  
**Time:** ~10 hours  
**Tests:** Prometheus, Grafana, Loki, Alerting, Debugging

### What You'll Build
Deploy a complete observability stack on your cluster.

### Requirements
- [ ] **kube-prometheus-stack** deployed via Helm
- [ ] **Loki + Promtail** for log aggregation (Grafana Loki Helm chart)
- [ ] Custom Grafana dashboard showing:
  - Pod CPU/memory usage per namespace
  - HTTP request rate and latency (if your app exposes metrics)
  - Pod restart count
- [ ] **Alerts configured:**
  - PodCrashLooping → page (Slack webhook or email)
  - NodeCPUHigh (>80%) → warning
  - PVCAlmostFull (>85%) → warning

### Deliverable
A `monitoring/` directory in your Git repo with:
```
monitoring/
├── dashboards/
│   └── my-custom-dashboard.json
├── alerts/
│   └── custom-alerts.yaml
└── README.md   # How to import the dashboard + screenshots
```

---

## 🏗️ Project 6 — "GitOps Everything" (Week 15)
**Difficulty:** ⭐⭐⭐  
**Time:** ~8 hours  
**Tests:** Helm, ArgoCD, GitHub Actions

### What You'll Build
A full GitOps pipeline where a git push to `main` automatically deploys to your cluster.

### Pipeline Architecture
```
Developer pushes code
       │
       ▼
GitHub Actions:
  1. Build Docker image
  2. Push to GHCR (GitHub Container Registry)
  3. Update image tag in Helm values.yaml
  4. Git commit + push values.yaml
       │
       ▼
ArgoCD detects change in Git
  ├── Syncs Helm chart to cluster
  └── New pods rolling update
```

### Requirements
- [ ] Helm chart for your entire stack (frontend, api, db, monitoring)
- [ ] ArgoCD App of Apps pattern:
  - `apps/` parent app
  - `apps/frontend`, `apps/api`, `apps/database` child apps
- [ ] GitHub Actions workflow that:
  1. Runs on push to `main`
  2. Builds + pushes image with git SHA as tag
  3. Updates `values.yaml` with new tag
  4. Commits and pushes back to repo
- [ ] ArgoCD auto-syncs within 3 minutes of the push

### Acceptance Criteria
- Change the NGINX welcome page HTML
- Push to main
- See the change live in your cluster without running a single `kubectl` command
- ArgoCD UI shows the sync history

---

## 🏗️ Project 7 — "The Production Cluster" (Weeks 16-22)
**Difficulty:** ⭐⭐⭐⭐⭐  
**Time:** ~20+ hours  
**This is your capstone. Everything combined.**

### What You'll Build
Deploy Google's **Online Boutique** microservices demo (11 services) with full production tooling.

### Source App
```bash
git clone https://github.com/GoogleCloudPlatform/microservices-demo
```

### Your Mission
Transform this app from a "just works" demo into a production-grade K8s deployment:

| Layer | What to Add |
|-------|-------------|
| **Packaging** | Helm chart for each service |
| **GitOps** | ArgoCD managing all 11 services via App of Apps |
| **Service Mesh** | Istio with mTLS enabled, traffic visible in Kiali |
| **Canary** | Istio VirtualService: 90% → v1, 10% → v2 of frontend |
| **Autoscaling** | HPA on checkout, cart, and frontend services |
| **Security** | NetworkPolicy: only allow expected service-to-service traffic |
| **RBAC** | Operator SA, Developer SA, Readonly SA |
| **Security Context** | All pods non-root, readOnlyRootFilesystem |
| **Observability** | Prometheus + Grafana + Loki + Jaeger (distributed tracing) |
| **Alerting** | At least 5 meaningful alerts |
| **Chaos** | Run the chaos experiments from Project 3 — document results |
| **Backups** | etcd snapshot automation (CronJob) |

### Final Deliverable
A GitHub repo with:
```
production-cluster/
├── README.md             (architecture diagram, how to deploy, lessons learned)
├── charts/               (Helm charts for each service)
├── argocd/               (App of Apps manifests)
├── istio/                (VirtualServices, DestinationRules)
├── monitoring/           (Prometheus rules, Grafana dashboards)
├── security/             (NetworkPolicies, RBAC, PodSecurity)
└── docs/
    ├── architecture.md
    ├── chaos-report.md
    └── runbook.md        (how to handle common incidents)
```

**This project IS your Kubernetes portfolio.** Link it on your resume.

---

## 📝 Project Submission Checklist

For each project, before marking it "done":

- [ ] All manifests committed to Git
- [ ] `README.md` explains what was built and why decisions were made
- [ ] A `lessons-learned.md` section: what broke, what surprised you
- [ ] Key commands documented (so future-you can repeat it)
- [ ] Screenshots of dashboards, ArgoCD UI, or terminal output proving it works
