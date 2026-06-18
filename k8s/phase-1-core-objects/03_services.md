# 03 — Services: Stable Networking for Your Pods

> **The core problem:** Pod IPs are ephemeral. Every time a pod is restarted, deleted and recreated, or rescheduled to another node, its IP address changes. If App A hardcodes App B's pod IP, it breaks every time B restarts. **Services exist to solve this.**

---

## 🌊 Why Services Exist — The Ephemeral IP Problem

```
Time 0:
  App A (10.244.1.4) ──────────────► App B (10.244.2.7)
                          "I know App B's IP!"

Pod B crashes and is recreated on a different node:

Time 1:
  App A (10.244.1.4) ──────────────► App B (10.244.3.11)   ← NEW IP!
                          "Connection refused!" ❌
```

**The solution: a Service** — a stable virtual IP + DNS name that sits in front of your pods and load-balances across them.

```
Time 0:
  App A ───► Service "app-b" (10.96.45.21) ──────► Pod B (10.244.2.7)

Pod B crashes and is recreated with a NEW IP:

Time 1:
  App A ───► Service "app-b" (10.96.45.21) ──────► Pod B (10.244.3.11)
             (same stable IP!)                       (new pod IP)
             kube-proxy updated the routing rules automatically ✅
```

> **Analogy:** A Service is like a **company phone number**.  
> Employees (pods) come and go — they quit, get hired, change desks (nodes).  
> But you always call the same company phone number (Service IP/DNS).  
> The receptionist (kube-proxy) routes your call to whichever employee is currently available.

---

## 🧠 How Services Actually Work

Services don't run any actual process. They're a virtual construct that kube-proxy implements via **iptables rules on every node**.

```
When a Service is created:
1. API Server creates the Service object
2. Endpoints Controller creates an Endpoints object (list of pod IPs)
3. kube-proxy on EVERY node updates its iptables rules:
   "Traffic for 10.96.45.21:80 → forward to one of: [10.244.2.7, 10.244.1.9, 10.244.3.2]"

When a pod is added/removed:
1. Endpoints Controller updates the Endpoints object
2. kube-proxy updates iptables rules
→ Traffic routing updates automatically, cluster-wide
```

**The Service and its Endpoints are separate objects:**
```bash
kubectl get services          # Shows the virtual IP (ClusterIP)
kubectl get endpoints         # Shows the actual pod IPs behind it
```

If Endpoints shows `<none>`, your selector doesn't match any pods.

---

## 🔢 The Four Service Types

### Type 1: ClusterIP (Default)

**What it does:** Creates a virtual IP that's only reachable **from within the cluster**.

```
Internet
   │
   X  (can't reach ClusterIP from outside)
   
Within the cluster:

  Pod A ──────────────────────────────────► Service (ClusterIP: 10.96.45.21)
                                                        │
                                           ┌────────────┼────────────┐
                                           ▼            ▼            ▼
                                         Pod B1       Pod B2       Pod B3
```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-backend
spec:
  type: ClusterIP          # (this is the default, you can omit it)
  selector:
    app: backend           # Routes to pods with this label
  ports:
  - port: 80               # Port the Service listens on
    targetPort: 8080       # Port the Pod's container is actually listening on
```

**When to use:** Internal microservice communication. Database services. Anything that doesn't need to be reached from outside the cluster.

---

### Type 2: NodePort

**What it does:** Opens a port on **every node** in the cluster. External traffic hitting `<any-node-ip>:<nodeport>` reaches your service.

```
Internet
   │
   └──────────────► Node 1 IP:30080
                    Node 2 IP:30080     ← Any node's IP works!
                    Node 3 IP:30080
                         │
                    kube-proxy routes
                         │
                    ┌────┴────┐
                    ▼         ▼
                  Pod A     Pod B
```

```yaml
spec:
  type: NodePort
  selector:
    app: backend
  ports:
  - port: 80             # ClusterIP port (internal traffic)
    targetPort: 8080     # Pod's actual port
    nodePort: 30080      # External port (must be 30000-32767)
                         # Omit nodePort to get a random one assigned
```

**When to use:** Development/testing when you need external access without a cloud load balancer. Kind clusters for quick testing (with extraPortMappings).

**Limitation:** You need to know the node IP. If the node changes (cloud nodes rotate), your URL breaks. Not good for production public traffic.

---

### Type 3: LoadBalancer

**What it does:** Provisions an **external load balancer** (via the cloud provider) and assigns it a public IP.

```
Internet
   │
   ▼
[Cloud Load Balancer]  ← Gets a real public IP (e.g., 34.117.45.22)
   │
   ├──────────────────► Node 1
   │                      │
   ├──────────────────► Node 2
   │                      │
   └──────────────────► Node 3
                          │
                       kube-proxy
                          │
                       ┌──┴──┐
                       ▼     ▼
                     Pod A  Pod B
```

```yaml
spec:
  type: LoadBalancer
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8080
```

After applying, `kubectl get service` will show:
```
NAME         TYPE           CLUSTER-IP     EXTERNAL-IP     PORT(S)
my-service   LoadBalancer   10.96.45.21    34.117.45.22    80:31234/TCP
                                           ↑
                                           This appears after the cloud LB is provisioned
                                           (may take 1-2 minutes)
```

**In kind/local clusters:** LoadBalancer services get stuck in `<pending>` for EXTERNAL-IP because there's no cloud to provision from. Use MetalLB or just use NodePort instead.

**When to use:** Production public-facing services on cloud (GKE, EKS, AKS). One LB per Service — can get expensive if you have many services (use Ingress instead for HTTP).

---

### Type 4: ExternalName

**What it does:** Maps a Service name to an **external DNS name**. No proxying, no virtual IP — just a DNS CNAME alias.

```yaml
spec:
  type: ExternalName
  externalName: mydb.example.com   # External DNS name
```

Now inside your cluster, `my-service` resolves to `mydb.example.com`. Your pods can use `my-service` and K8s redirects to the real external host.

**When to use:** Abstracting external databases during migration. You plan to move the DB into the cluster later — code uses the same Service name, you just change the ExternalName.

---

## 🗺️ Service Types Visual Comparison

```
                                      INTERNET
                                          │
                              ┌───────────┼───────────────┐
                              │           │               │
                        LoadBalancer   NodePort      (ClusterIP — blocked)
                              │       port:3xxxx
                              │           │
                    ──────────────────────────────────────
                    │               CLUSTER                │
                    │                                      │
                    │   Service (ClusterIP: 10.96.x.x)   │
                    │              │                       │
                    │    ┌─────────┼─────────┐            │
                    │    ▼         ▼         ▼            │
                    │  [Pod]     [Pod]     [Pod]          │
                    └──────────────────────────────────────
```

| Type | Cluster-internal? | External? | When to use |
|------|-----------------|----------|------------|
| ClusterIP | ✅ | ❌ | Internal services |
| NodePort | ✅ | ✅ (node IP:port) | Dev/test, simple external access |
| LoadBalancer | ✅ | ✅ (dedicated IP) | Production public services on cloud |
| ExternalName | ✅ (as alias) | N/A | Abstracting external dependencies |

---

## 🌐 DNS — How Pods Find Services

CoreDNS runs inside the cluster and gives every Service a stable DNS name. This is the right way to communicate between services.

**DNS name format:**
```
<service-name>.<namespace>.svc.cluster.local

Examples:
  my-backend.default.svc.cluster.local
  postgres.production.svc.cluster.local
  redis.cache.svc.cluster.local
```

**The magic of search domains:** K8s injects search domains into every pod's `/etc/resolv.conf`:

```bash
# Inside any pod:
cat /etc/resolv.conf
# Output:
# nameserver 10.96.0.10          ← CoreDNS ClusterIP
# search default.svc.cluster.local svc.cluster.local cluster.local
# options ndots:5
```

Because of these search domains, **within the same namespace** you can use just the service name:

```bash
# These ALL resolve to the same service (within same namespace):
curl http://my-backend
curl http://my-backend.default
curl http://my-backend.default.svc
curl http://my-backend.default.svc.cluster.local

# Cross-namespace — must use at least: <name>.<namespace>
curl http://my-backend.production.svc.cluster.local
```

> **Analogy:** Search domains are like **auto-complete for DNS**.  
> Within your company network, you just dial extension 1234 (just the service name).  
> From outside the company, you need the full phone number including area code and country code (full DNS name with namespace).

---

## 🔌 Headless Services (StatefulSets use this)

A headless service has `clusterIP: None`. Instead of a virtual IP, DNS returns the actual pod IPs directly.

```yaml
spec:
  clusterIP: None   # Headless!
  selector:
    app: postgres
```

DNS for a headless service returns A records (individual IPs) instead of the virtual IP:
```bash
nslookup postgres-svc
# Returns:
# 10.244.1.5   (postgres-0 pod)
# 10.244.2.8   (postgres-1 pod)
# 10.244.3.2   (postgres-2 pod)
```

For StatefulSets, each pod gets its own stable DNS record:
```
postgres-0.postgres-svc.default.svc.cluster.local → 10.244.1.5
postgres-1.postgres-svc.default.svc.cluster.local → 10.244.2.8
postgres-2.postgres-svc.default.svc.cluster.local → 10.244.3.2
```

This lets you connect to a specific DB replica directly — essential for primary/replica setups.

---

## ⚙️ Exposing Services — Practical Commands

```bash
# ─── CREATE SERVICES ────────────────────────────────────────

# Expose an existing deployment as ClusterIP
kubectl expose deployment web-app --port=80 --target-port=8080

# Expose as NodePort
kubectl expose deployment web-app --port=80 --target-port=8080 --type=NodePort

# Expose as LoadBalancer
kubectl expose deployment web-app --port=80 --target-port=8080 --type=LoadBalancer

# Create service from YAML
kubectl apply -f service.yaml

# ─── INSPECT ────────────────────────────────────────────────

kubectl get services
kubectl get svc                     # Shorthand
kubectl get svc -o wide             # With more details
kubectl describe svc my-service     # Full details including selector and endpoints

# ─── VERIFY ENDPOINTS (critical for debugging!) ─────────────
kubectl get endpoints my-service    # Shows actual pod IPs being load-balanced

# ─── ACCESS FROM INSIDE CLUSTER ─────────────────────────────
# Run a debug pod and test connectivity
kubectl run curl-test --image=curlimages/curl -it --rm -- \
  curl http://my-service.default.svc.cluster.local

# ─── ACCESS LOCALLY (kind clusters) ─────────────────────────
kubectl port-forward svc/my-service 8080:80
# → Access http://localhost:8080
```

---

## 🔧 Connecting It All — A Realistic Multi-Service Setup

```
                User Browser
                     │
                     ▼ http://localhost:30080
         ┌─────────────────────────────────┐
         │  frontend-svc (NodePort:30080)  │
         └──────────────┬──────────────────┘
                        │ selector: app=frontend
                   ┌────┴────┐
                   ▼         ▼
               [nginx]   [nginx]   ← frontend pods
                   │         │
           (fetch /api/*)     │
                   │         │
         ┌─────────▼─────────────────────┐
         │   api-svc (ClusterIP:80)      │
         └──────────────┬────────────────┘
                        │ selector: app=api
                   ┌────┴────┐
                   ▼         ▼
             [api-pod] [api-pod]   ← API pods
                   │         │
         ┌─────────▼─────────────────────┐
         │   db-svc (ClusterIP:5432)     │
         └──────────────┬────────────────┘
                        │ selector: app=postgres
                        ▼
                  [postgres pod]   ← DB pod
```

---

## 🧪 Test Yourself

1. **A pod's IP address is `10.244.2.7`. After the pod restarts, it gets `10.244.3.11`. How does App A always find App B without caring about the IP change?**

2. **What is the difference between `port` and `targetPort` in a Service spec?** Give a concrete example.

3. **You created a ClusterIP service but `kubectl get endpoints my-service` shows `<none>`. What went wrong and how do you diagnose it?**

4. **You're running on a kind cluster and create a LoadBalancer service. The EXTERNAL-IP stays as `<pending>`. Why? What's the workaround?**

5. **Inside a pod in the `dev` namespace, you try `curl http://api-service` but it fails. Same command works as `curl http://api-service.production.svc.cluster.local`. Why?**

6. **What is a Headless Service (`clusterIP: None`)? When would you need one?**

7. **You have 3 pods behind a ClusterIP service. One pod becomes unhealthy (readinessProbe failing). Does traffic still go to it?** How does K8s handle this?

8. **Why is NodePort considered unsuitable for production public traffic (even though it works)?**

didnt quite get how this works,will look again tomorrow