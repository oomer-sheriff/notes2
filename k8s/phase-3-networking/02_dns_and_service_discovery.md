# 02 — DNS & Service Discovery

> **Why this matters:** You never hardcode pod IPs. You use DNS names. Understanding how those names resolve — and why sometimes they don't — is essential for debugging microservice communication.

---

## 🧠 CoreDNS — The Cluster DNS Server

Every Kubernetes cluster runs **CoreDNS** as a Deployment in `kube-system`. It's the cluster's internal DNS server — every pod uses it for all name resolution.

```bash
kubectl get pods -n kube-system -l k8s-app=kube-dns
# NAME                      READY   STATUS    RESTARTS
# coredns-xxxx-aaaaa        1/1     Running   0
# coredns-xxxx-bbbbb        1/1     Running   0
# (runs as 2 replicas for redundancy)

kubectl get service -n kube-system kube-dns
# NAME       TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)
# kube-dns   ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP
```

Every pod's `/etc/resolv.conf` points to CoreDNS at `10.96.0.10`:

```bash
# Inside any pod:
cat /etc/resolv.conf
# nameserver 10.96.0.10          ← CoreDNS ClusterIP (always this)
# search default.svc.cluster.local svc.cluster.local cluster.local
# options ndots:5
```

---

## 🗺️ The Full DNS Name Structure

Every Service in Kubernetes gets a DNS record. The full format is:

```
<service-name>.<namespace>.svc.<cluster-domain>

Examples:
  my-api.production.svc.cluster.local
  postgres.database.svc.cluster.local
  redis.cache.svc.cluster.local

Breakdown:
  my-api          ← Service name (must match metadata.name)
  production      ← Namespace the Service is in
  svc             ← Literal — indicates this is a Service record
  cluster.local   ← The cluster domain (configurable, default: cluster.local)
```

---

## 🔎 The `ndots:5` and Search Domain Magic

This is what catches people out most often. Let's go deep.

When you query just `my-service` (no dots), CoreDNS doesn't know if it's a K8s service or an external hostname. The `ndots:5` option and search domains handle this:

```
/etc/resolv.conf:
  search default.svc.cluster.local svc.cluster.local cluster.local
  options ndots:5
```

**`ndots:5` means:** if the query has fewer than 5 dots, try the search domains FIRST before the bare name.

**So when you `curl http://my-service`:**

```
Query: "my-service"   (0 dots < 5)
       │
       ├─ Try: my-service.default.svc.cluster.local  ← FOUND if in "default" ns!
       │  (if not found)
       ├─ Try: my-service.svc.cluster.local
       │  (if not found)
       ├─ Try: my-service.cluster.local
       │  (if not found)
       └─ Try: my-service  ← raw, like Google DNS
```

**Cross-namespace — why `my-service` fails:**
```
You are in namespace "frontend"
Query: "my-service"  →  tries my-service.frontend.svc.cluster.local → NOT FOUND
                     →  tries my-service.svc.cluster.local → NOT FOUND
                     →  tries my-service.cluster.local → NOT FOUND
                     →  tries my-service (external DNS) → NOT FOUND
                     →  NXDOMAIN / connection refused

Solution: use full DNS name
Query: "my-service.backend"  →  has 1 dot → still tries search domains:
         my-service.backend.default.svc.cluster.local → NOT FOUND
         my-service.backend.svc.cluster.local → FOUND! ✅
         
Or fully qualified: "my-service.backend.svc.cluster.local" → always works
```

> **Analogy:** The search domains are like your **phone's contact suggestions**.  
> When you type "John", your phone tries "John Smith" from your contacts first, then "John Doe", before searching the global phonebook.  
> `ndots:5` is the threshold — if the name has enough dots, it looks globally first (it assumes you already know what you're looking for).

---

## 📋 DNS Record Types in Kubernetes

### A/AAAA Records — Services

Standard Services get an A record (IPv4) pointing to their **ClusterIP**:

```
Service: backend-svc in namespace: production
DNS A record: backend-svc.production.svc.cluster.local → 10.96.45.21

Query returns:
  backend-svc.production.svc.cluster.local.  5  IN  A  10.96.45.21
```

### SRV Records — Port Discovery

Services also get SRV records that encode the port and protocol:

```
_http._tcp.backend-svc.production.svc.cluster.local → port 80, backend-svc.production.svc.cluster.local
```

Used by service discovery tools (less common to use directly).

### A Records for Pods (Rarely Used)

Individual pods get DNS names too — but using pod IPs with dashes:

```
Pod IP: 10.244.2.7
Pod DNS: 10-244-2-7.default.pod.cluster.local

Rarely used directly because pod IPs change.
```

### Headless Services — DNS Returns Pod IPs Directly

A headless service (`clusterIP: None`) returns **multiple A records** — one per pod:

```yaml
spec:
  clusterIP: None    # Headless
  selector:
    app: postgres
```

```
nslookup postgres-headless
# postgres-headless.default.svc.cluster.local   → 10.244.1.5 (postgres-0)
# postgres-headless.default.svc.cluster.local   → 10.244.2.8 (postgres-1)
# postgres-headless.default.svc.cluster.local   → 10.244.3.2 (postgres-2)

# Each pod also gets its OWN DNS record:
# postgres-0.postgres-headless.default.svc.cluster.local → 10.244.1.5
# postgres-1.postgres-headless.default.svc.cluster.local → 10.244.2.8
```

**This is how StatefulSets enable stable pod addressing.** You can connect to `postgres-0.postgres-headless` specifically — even though the pod IP might change, the DNS name is stable.

---

## 🔧 CoreDNS Configuration (Corefile)

CoreDNS is configured by a ConfigMap in `kube-system`:

```bash
kubectl get configmap coredns -n kube-system -o yaml
```

The Corefile looks like this:

```
.:53 {
    errors
    health {
       lameduck 5s
    }
    ready
    kubernetes cluster.local in-addr.arpa ip6.arpa {
       pods insecure
       fallthrough in-addr.arpa ip6.arpa
       ttl 30
    }
    prometheus :9153
    forward . /etc/resolv.conf {
       max_concurrent 1000
    }
    cache 30
    loop
    reload
    loadbalance
}
```

**Key parts:**
- `kubernetes cluster.local` — handles all `*.cluster.local` queries (cluster-internal)
- `forward . /etc/resolv.conf` — for everything NOT cluster-internal, forward to the node's DNS (so pods can reach google.com, etc.)
- `cache 30` — cache results for 30 seconds (TTL)

**Customizing CoreDNS** — add a stub zone for an internal service:
```
# Add after the kubernetes block:
my-company.internal:53 {
    forward . 10.100.0.2   # Internal DNS server for your company domain
}
```

---

## 🌐 ExternalName Services — Mapping to External DNS

An ExternalName service doesn't get a ClusterIP or load balance. It creates a CNAME:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-database
  namespace: production
spec:
  type: ExternalName
  externalName: prod-db.us-east-1.rds.amazonaws.com
```

Inside the cluster:
```bash
nslookup my-database.production.svc.cluster.local
# Returns CNAME: prod-db.us-east-1.rds.amazonaws.com
# Then resolves that to: 52.x.x.x

# Your app uses:
curl http://my-database:5432      # → connects to RDS!
```

**Use case:** Migrate a DB from external to in-cluster. Update ExternalName → ClusterIP. App code never changes.

---

## 🐛 Debugging DNS — Systematic Approach

```bash
# 1. Launch a DNS debug pod (has dig, nslookup, curl)
kubectl run dns-debug --image=gcr.io/kubernetes-e2e-test-images/dnsutils:1.3 \
  --restart=Never -it --rm -- sh

# 2. Inside: test the full stack
# Test CoreDNS is reachable:
nslookup kubernetes.default
# Should return: 10.96.0.1

# Test a service in the same namespace:
nslookup my-service

# Test cross-namespace:
nslookup my-service.other-namespace.svc.cluster.local

# Test external resolution works:
nslookup google.com

# Test with dig (more detail):
dig my-service.default.svc.cluster.local
dig +search my-service   # Forces search domain expansion

# See what search domains are configured:
cat /etc/resolv.conf
```

### Common DNS Problems and Fixes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `NXDOMAIN` for `my-service` from different namespace | Missing full DNS name | Use `my-service.namespace.svc.cluster.local` |
| `NXDOMAIN` even with full name | Service doesn't exist OR wrong namespace | Check `kubectl get svc -A` |
| `SERVFAIL` | CoreDNS pod unhealthy | `kubectl get pods -n kube-system -l k8s-app=kube-dns` |
| External DNS doesn't resolve (`google.com`) | Node's DNS unreachable | Check CoreDNS `forward` config |
| Very slow DNS resolution | `ndots:5` causing many search domain retries | Use FQDN (trailing dot): `my-service.default.svc.cluster.local.` |

---

## 🧪 Test Yourself

1. **What is CoreDNS? Where does it run, and what IP does it listen on?**

2. **A pod queries `my-api`. With `ndots:5` and `search default.svc.cluster.local svc.cluster.local cluster.local`, list EVERY DNS query that gets attempted, in order.**

3. **What is a headless service?** How does its DNS response differ from a regular ClusterIP service?

4. **You have a StatefulSet called `postgres` with a headless service also called `postgres`. What DNS name addresses pod #1 specifically?** Write the full FQDN.

5. **An app in namespace `frontend` can reach `backend-api.backend.svc.cluster.local` but NOT `backend-api`. Explain why.**

6. **What does the `forward . /etc/resolv.conf` line in CoreDNS's Corefile do?** What would happen if you removed it?

7. **You want all cluster pods to resolve `db.mycompany.internal` to `10.100.0.50`. Where do you configure this and what do you add?**

8. **A pod does `curl http://my-service`. It fails. `kubectl get svc my-service` shows it exists. `kubectl get endpoints my-service` shows `<none>`. What's wrong?**
