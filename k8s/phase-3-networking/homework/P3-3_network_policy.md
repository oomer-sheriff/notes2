# Homework P3-3 — Network Policy: Zero-Trust Lab

> **Time:** 2 hours  
> **Goal:** Install a NetworkPolicy-capable CNI, apply default-deny policies, punch specific allow rules, and PROVE with debug pods that policies are enforced.
>
> ⚠️ **Important:** The default `kindnet` CNI does NOT enforce NetworkPolicy. This lab uses Killercoda (browser-based, pre-configured with Calico) for the enforcement parts. Read Part 0 carefully.

---

## Part 0 — Your Two Options

### Option A: Killercoda (Recommended for NetworkPolicy enforcement)

1. Go to: https://killercoda.com/playgrounds/scenario/kubernetes
2. This gives you a free browser-based K8s cluster with Calico pre-installed
3. NetworkPolicies ARE enforced here
4. Run all commands in the browser terminal
5. This is also how the CKA/CKAD exam works!

### Option B: Install Calico in your kind cluster (Advanced)

```powershell
# Delete existing cluster and recreate with NO CNI
kind delete cluster --name k8s-multinode

# Create kind config WITHOUT kindnet
# (See lab-files/kind-calico-config.yaml below)
kind create cluster --config lab-files/kind-calico-config.yaml

# Install Calico
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.28.0/manifests/calico.yaml

# Wait for Calico to be ready (~2 minutes)
kubectl get pods -n calico-system -w
```

Save as `lab-files/kind-calico-config.yaml`:
```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: k8s-calico
networking:
  disableDefaultCNI: true    # Don't use kindnet
  podSubnet: "192.168.0.0/16"  # Calico default pod CIDR
nodes:
- role: control-plane
- role: worker
- role: worker
```

---

## Part 1 — The Default Open Network (10 min)

### Task 1.1 — Prove Default Allow-All

```bash
# Create two namespaces
kubectl create namespace ns-a
kubectl create namespace ns-b

# Deploy an app in ns-a
kubectl create deployment web --image=nginx:1.25 -n ns-a
kubectl expose deployment web --port=80 -n ns-a

# Deploy a debug pod in ns-b
kubectl run curl-test --image=curlimages/curl -n ns-b \
  --restart=Never -it --rm \
  -- curl http://web.ns-a.svc.cluster.local

# Expected: Welcome to nginx! (proves cross-ns traffic works by default)
```

**Write down:** Can a pod in ns-b reach a service in ns-a before any NetworkPolicy?

---

## Part 2 — Default Deny Everything (20 min)

### Task 2.1 — Apply Default Deny for ns-a

```yaml
# Save as lab-files/default-deny.yaml
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: ns-a
spec:
  podSelector: {}       # Selects ALL pods in ns-a
  policyTypes:
  - Ingress             # Control incoming traffic
  # No ingress rules = deny ALL ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: ns-a
spec:
  podSelector: {}
  policyTypes:
  - Egress
  # No egress rules = deny ALL egress
```

```bash
kubectl apply -f lab-files/default-deny.yaml

# Now try again from ns-b:
kubectl run curl-test --image=curlimages/curl -n ns-b \
  --restart=Never -it --rm \
  -- curl --max-time 5 http://web.ns-a.svc.cluster.local
# Expected: curl: (28) Connection timed out
```

**NetworkPolicy is enforced!**  
Notice: there's no "refused" — it just times out silently. This is characteristic of firewall drops.

---

## Part 3 — Punch Specific Holes (40 min)

### Task 3.1 — Allow Only From Specific Pod

```bash
# Create an "allowed" pod in ns-b with a specific label
kubectl run allowed-client --image=curlimages/curl -n ns-b \
  --labels="role=trusted-client" \
  --restart=Never -- sleep 3600

# Create a "rogue" pod in ns-b without that label
kubectl run rogue-client --image=curlimages/curl -n ns-b \
  --restart=Never -- sleep 3600
```

```yaml
# Save as lab-files/allow-trusted.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-trusted
  namespace: ns-a
spec:
  podSelector:
    matchLabels:
      app: web              # This policy applies to web pods
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ns-b   # From ns-b namespace
      podSelector:
        matchLabels:
          role: trusted-client                # AND only from trusted-client pods
    ports:
    - protocol: TCP
      port: 80
```

```bash
kubectl apply -f lab-files/allow-trusted.yaml

# Label ns-b so it can be selected (K8s auto-adds metadata.name label in newer versions)
kubectl label namespace ns-b kubernetes.io/metadata.name=ns-b

# Test from ALLOWED pod:
kubectl exec allowed-client -n ns-b -- curl --max-time 5 http://web.ns-a.svc.cluster.local
# Expected: Welcome to nginx! (ALLOWED ✅)

# Test from ROGUE pod:
kubectl exec rogue-client -n ns-b -- curl --max-time 5 http://web.ns-a.svc.cluster.local
# Expected: timeout (BLOCKED ❌)
```

**This is zero-trust networking in action.**

---

### Task 3.2 — The AND vs OR Selector Trap

```yaml
# Save as lab-files/selector-or.yaml  (OR — more permissive)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: selector-or-demo
  namespace: ns-a
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:             # SEPARATE items in the list = OR
        matchLabels:
          role: trusted-client
    - namespaceSelector:       # (any pod in ns-b) OR (any pod with role=trusted-client)
        matchLabels:
          kubernetes.io/metadata.name: ns-b
```

```yaml
# Save as lab-files/selector-and.yaml  (AND — more restrictive)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: selector-and-demo
  namespace: ns-a
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:             # SAME list item = AND
        matchLabels:
          role: trusted-client
      namespaceSelector:       # must be BOTH: in ns-b AND have role=trusted-client
        matchLabels:
          kubernetes.io/metadata.name: ns-b
```

```bash
# Apply the OR version and test with rogue-client (different ns same pod selector won't apply)
kubectl apply -f lab-files/selector-or.yaml

# With OR: rogue-client is in ns-b, and ns-b is allowed → rogue-client gets in!
kubectl exec rogue-client -n ns-b -- curl --max-time 5 http://web.ns-a.svc.cluster.local
# Expected: nginx page (ALLOWED — even though rogue!)
# The OR policy says: ns-b OR trusted-client. rogue-client IS in ns-b.

# Switch to AND version:
kubectl delete networkpolicy selector-or-demo -n ns-a
kubectl apply -f lab-files/selector-and.yaml

kubectl exec rogue-client -n ns-b -- curl --max-time 5 http://web.ns-a.svc.cluster.local
# Expected: timeout (BLOCKED — rogue-client is in ns-b BUT doesn't have role=trusted-client)
```

**This is the most important lesson in NetworkPolicy.**

---

## Part 4 — Egress Control + DNS Gotcha (20 min)

### Task 4.1 — Restrict Egress From a Pod

```yaml
# Save as lab-files/egress-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-egress
  namespace: ns-a
spec:
  podSelector:
    matchLabels:
      app: web
  policyTypes:
  - Egress
  egress:
  # ALLOW DNS! If you forget this, nothing resolves.
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

```bash
kubectl apply -f lab-files/egress-policy.yaml

# Shell into the web pod
WEB_POD=$(kubectl get pods -n ns-a -l app=web -o jsonpath='{.items[0].metadata.name}')
kubectl exec $WEB_POD -n ns-a -- curl --max-time 5 http://google.com
# Expected: timeout (external traffic blocked)

# But DNS still works:
kubectl exec $WEB_POD -n ns-a -- nslookup kubernetes.default
# Expected: resolves (DNS allowed via kube-system egress rule)
```

**Now comment out the DNS egress rule and reapply — watch DNS break.**

---

## 🧹 Cleanup

```bash
kubectl delete namespace ns-a
kubectl delete namespace ns-b
```

---

## ✅ Done When:

- [ ] Default open network proven — cross-namespace traffic worked
- [ ] Default-deny applied — traffic timed out (not refused)
- [ ] Trusted-client allowed, rogue-client blocked
- [ ] AND vs OR selector difference proven with actual curl tests
- [ ] Egress restriction applied — external traffic blocked but DNS preserved

## 📝 Reflection

**Why does a NetworkPolicy drop cause a timeout instead of an immediate connection refused?**
```

```

**What's the single most dangerous mistake you can make when writing egress policies?**
```

```

**If you're on a cluster that uses Flannel as CNI and you apply a NetworkPolicy — what actually happens?**
```

```
