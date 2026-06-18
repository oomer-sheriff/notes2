# Homework P3-1 — DNS & Service Discovery Lab

> **Time:** 1.5 hours  
> **Goal:** Dig into how DNS resolution works in the cluster, prove the search domain behaviour, trace queries through CoreDNS, and see headless service DNS records.

---

## 🚀 Setup

```powershell
kubectl create namespace lab-dns
kubectl create namespace lab-dns-b    # Second namespace for cross-ns testing
kubectl config set-context --current --namespace=lab-dns
```

---

## Part 1 — Deploy Services to Query Against (10 min)

```powershell
# Deploy an echo server and expose it
kubectl create deployment echo-app --image=hashicorp/http-echo --replicas=3 -n lab-dns
kubectl patch deployment echo-app -n lab-dns --type='json' \
  -p='[{"op":"add","path":"/spec/template/spec/containers/0/args","value":["-text=Hello from echo-app pod"]}]'
kubectl expose deployment echo-app --port=80 --target-port=5678 -n lab-dns

# Deploy something in the second namespace too
kubectl create deployment cross-ns-app --image=nginx:1.25 -n lab-dns-b
kubectl expose deployment cross-ns-app --port=80 -n lab-dns-b
```

---

## Part 2 — The DNS Debug Pod (30 min)

### Task 2.1 — Launch and Explore

```powershell
# Launch the DNS debug image (has dig, nslookup, curl)
kubectl run dns-debug --image=gcr.io/kubernetes-e2e-test-images/dnsutils:1.3 `
  --restart=Never -it --rm -n lab-dns -- sh
```

Inside the shell, run ALL of these and fill in the tables:

```sh
# See your pod's DNS config
cat /etc/resolv.conf
```

**Fill in from /etc/resolv.conf:**

| Field | Value |
|-------|-------|
| nameserver | |
| search domains (list all) | |
| options | |

---

```sh
# Test 1: Resolve a service in the SAME namespace (short name)
nslookup echo-app
```

**What IP did it return?**  
Is this the ClusterIP or a pod IP?

---

```sh
# Test 2: Full FQDN  
nslookup echo-app.lab-dns.svc.cluster.local
```

**Same result?**

---

```sh
# Test 3: Observe the search domain expansion with dig
dig +search echo-app
# Look at the QUESTION SECTION — what name was actually queried?
# Look at the ANSWER SECTION — what IP was returned?
```

**Write down the QUESTION SECTION query:**

---

```sh
# Test 4: Cross-namespace — short name (should fail!)
nslookup cross-ns-app
# What error do you get?
```

**Fill in:**

| Query | Result | Reason |
|-------|--------|--------|
| `cross-ns-app` | | |
| `cross-ns-app.lab-dns-b` | | |
| `cross-ns-app.lab-dns-b.svc.cluster.local` | | |

---

```sh
# Test 5: CoreDNS itself
nslookup kubernetes.default.svc.cluster.local
# This is the kubernetes API service — always exists at 10.96.0.1

# Test 6: External DNS through CoreDNS's forwarder
nslookup google.com
# Should resolve! (CoreDNS forwards external queries to node's DNS)
```

---

### Task 2.2 — Observe Search Domain Expansion

This is the `ndots:5` behaviour in action:

```sh
# Count the dots in each query and predict whether search domains are tried first:

# 0 dots — search domains tried first
nslookup echo-app                           # 0 dots → tries echo-app.lab-dns.svc.cluster.local first

# 1 dot — still fewer than 5 → search domains tried
nslookup echo-app.lab-dns                   # 1 dot → tries echo-app.lab-dns.lab-dns.svc.cluster.local first (fails)
                                            # then tries echo-app.lab-dns.svc.cluster.local (succeeds!)

# 4 dots — still fewer than 5 → search domains tried first
nslookup echo-app.lab-dns.svc.cluster       # 4 dots → search domains tried first, then raw

# 5+ dots — treated as FQDN, no search domains
nslookup echo-app.lab-dns.svc.cluster.local # 5 dots → queried directly, no search domain expansion
```

**Observation:** Adding a trailing dot forces absolute (no search expansion):
```sh
nslookup echo-app.    # trailing dot = FQDN = no search domains
# This should fail (echo-app. doesn't exist globally)
```

Exit the shell: `exit`

---

## Part 3 — CoreDNS Inspection (15 min)

```powershell
# See CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns

# Read the CoreDNS ConfigMap (the Corefile)
kubectl get configmap coredns -n kube-system -o yaml
```

**Fill in from the Corefile:**

| Config Element | Value/What It Does |
|---------------|-------------------|
| What port does CoreDNS listen on? | |
| What cluster domain is configured? | |
| Where does CoreDNS forward external queries? | |
| What is the DNS TTL/cache setting? | |

---

## Part 4 — Headless Service DNS (20 min)

### Task 4.1 — Create and Query a Headless Service

```powershell
# Create a headless service for echo-app
kubectl apply -f - @"
apiVersion: v1
kind: Service
metadata:
  name: echo-app-headless
  namespace: lab-dns
spec:
  clusterIP: None        # This makes it headless
  selector:
    app: echo-app
  ports:
  - port: 80
    targetPort: 5678
"@

kubectl get service echo-app-headless -n lab-dns
# Notice: CLUSTER-IP shows "None"
```

```powershell
# Query the headless service
kubectl run dns-debug --image=gcr.io/kubernetes-e2e-test-images/dnsutils:1.3 `
  --restart=Never -it --rm -n lab-dns -- sh
```

```sh
# Regular service DNS — returns single ClusterIP
nslookup echo-app
# Returns: one IP (the ClusterIP virtual IP)

# Headless service DNS — returns multiple pod IPs
nslookup echo-app-headless
# Returns: 3 IPs (one per pod replica)!

# See the difference with dig:
dig echo-app.lab-dns.svc.cluster.local      # One A record
dig echo-app-headless.lab-dns.svc.cluster.local   # Multiple A records!
```

**Fill in:**

| Query | Type of Response | # of IPs Returned |
|-------|-----------------|-------------------|
| Regular service (`echo-app`) | Single ClusterIP | |
| Headless service (`echo-app-headless`) | Multiple pod IPs | |

**Why would you need direct pod IPs instead of a virtual IP?**
```

```

Exit: `exit`

---

## 🧹 Cleanup

```powershell
kubectl delete namespace lab-dns
kubectl delete namespace lab-dns-b
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] `/etc/resolv.conf` table completed
- [ ] Cross-namespace DNS table completed (all 3 DNS name formats tested)
- [ ] Search domain expansion behaviour observed with dig
- [ ] CoreDNS ConfigMap read and table filled in
- [ ] Headless vs regular service DNS comparison done

## 📝 Reflection

**Why does K8s inject search domains into /etc/resolv.conf?**
```

```

**When would you choose a headless service over a regular ClusterIP service?**
```

```
