# 04 — Network Policies: Zero-Trust Networking

> **The default is dangerous:** Without NetworkPolicies, every pod in your cluster can talk to every other pod — including your production database from a development namespace, or a compromised pod reaching internal APIs it has no business touching. NetworkPolicies are the firewall rules of K8s.

---

## 🔓 The Default: Open by Default

Remember from Phase 1 namespaces lab — you proved that a pod in `dev` can freely reach a service in `prod`. This is the flat network model being both a feature AND a risk.

```
WITHOUT NetworkPolicy (default):
  
  dev-pod ──────────────────────────────→ prod-database ✅ (bad!)
  hacker-pod (compromised) ─────────────→ api-server ✅ (very bad!)
  frontend-pod ─────────────────────────→ any-other-pod ✅ (probably too permissive)

WITH NetworkPolicy:
  
  dev-pod ──────────────────────────────→ prod-database ❌ (blocked)
  hacker-pod ───────────────────────────→ api-server ❌ (blocked)
  frontend-pod ──────────────────────────→ backend-pod ✅ (explicitly allowed)
  frontend-pod ──────────────────────────→ database-pod ❌ (blocked)
```

---

## 🧱 What Is a NetworkPolicy?

A NetworkPolicy is a K8s object that **selects a group of pods and specifies what traffic they can receive (ingress) and/or send (egress)**.

```
                   ┌─────────────────────────────────────┐
                   │         NetworkPolicy                │
                   │                                     │
                   │  podSelector: (which pods I govern) │
                   │    matchLabels:                     │
                   │      app: backend                   │
                   │                                     │
                   │  policyTypes:                       │
                   │    - Ingress    ← control incoming  │
                   │    - Egress     ← control outgoing  │
                   │                                     │
                   │  ingress:       ← who can reach me? │
                   │    - from:                          │
                   │        podSelector:                 │
                   │          app: frontend              │
                   │                                     │
                   │  egress:        ← where can I go?  │
                   │    - to:                            │
                   │        podSelector:                 │
                   │          app: postgres              │
                   └─────────────────────────────────────┘
```

---

## ⚠️ CNI Requirement

**NetworkPolicy is enforced by the CNI plugin, NOT by K8s itself.**  
If your CNI doesn't support NetworkPolicy (like `kindnet`), your policies will be accepted by the API server but silently ignored — traffic flows freely regardless.

**CNI plugins that support NetworkPolicy:** Calico, Cilium, Weave, Antrea  
**CNI plugins that do NOT:** Flannel (alone), kindnet

For your kind cluster labs, you have two options:
1. **Replace kindnet with Calico** (shown in the homework lab)
2. **Use Killercoda or killer.sh** (pre-configured with Calico — better for exam prep)

---

## 📐 The Three Selectors

NetworkPolicies use three types of selectors to specify allowed traffic sources/destinations:

### 1. `podSelector` — Select by pod labels

```yaml
from:
- podSelector:
    matchLabels:
      app: frontend    # Only pods with label app=frontend can reach me
```

Same namespace by default. Combine with `namespaceSelector` for cross-namespace.

### 2. `namespaceSelector` — Select by namespace labels

```yaml
from:
- namespaceSelector:
    matchLabels:
      environment: production   # Pods from ANY namespace labeled environment=production
```

**Must label the namespace first:**
```bash
kubectl label namespace production environment=production
```

### 3. `ipBlock` — Select by IP range (CIDR)

```yaml
from:
- ipBlock:
    cidr: 10.0.0.0/8       # Allow from entire 10.x.x.x range
    except:
    - 10.100.0.0/16         # But block this subnet within that range
```

Use for external traffic that has a known IP range (e.g., corporate VPN, office network).

---

## 🔐 Policy Types and the Default-Deny Pattern

### `policyTypes` field

This tells K8s which traffic direction is being controlled:

```yaml
policyTypes:
- Ingress          # This policy controls INCOMING traffic to selected pods
- Egress           # This policy controls OUTGOING traffic from selected pods
```

**Critical rule:** As soon as AT LEAST ONE NetworkPolicy selects a pod, that pod moves from "allow all" to "deny all UNLESS explicitly allowed by a policy".

```
Pod with NO policies selecting it:
  incoming: ALL ALLOWED
  outgoing: ALL ALLOWED

Pod with 1+ Ingress policy selecting it:
  incoming: ONLY what the policies allow
  outgoing: STILL ALL ALLOWED (egress not restricted yet)

Pod with 1+ Egress policy selecting it:
  incoming: STILL ALL ALLOWED
  outgoing: ONLY what the policies allow
```

### The Default-Deny Pattern (Zero-Trust)

The standard production approach: deny everything first, then punch specific holes.

```yaml
# Step 1: Default deny ALL ingress for a namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}          # {} = selects ALL pods in this namespace
  policyTypes:
  - Ingress
  # No ingress rules = deny all ingress
```

```yaml
# Step 2: Default deny ALL egress for a namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress
  # No egress rules = deny all egress
```

After applying both — all pods in `production` are completely isolated.  
Now you punch specific holes:

---

## 📄 Complete Example — Three-Tier App

```
  internet → frontend → backend → database
  
  Rules:
  - frontend: can receive from anywhere, can only talk to backend
  - backend: can only receive from frontend, can only talk to database
  - database: can only receive from backend, egress only for DNS
```

```yaml
# ─── Policy for Frontend pods ──────────────────────────────────────
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: frontend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: frontend

  policyTypes:
  - Ingress
  - Egress

  ingress:
  - {}             # {} in a rule = allow from anywhere (no restrictions on source)

  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend      # Frontend can ONLY talk to backend
    ports:
    - protocol: TCP
      port: 8080
  - to:                     # Also allow DNS resolution (MUST explicitly allow!)
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53

---
# ─── Policy for Backend pods ───────────────────────────────────────
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: backend

  policyTypes:
  - Ingress
  - Egress

  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend      # ONLY frontend can reach backend
    ports:
    - protocol: TCP
      port: 8080

  egress:
  - to:
    - podSelector:
        matchLabels:
          app: database      # Backend can ONLY talk to database
    ports:
    - protocol: TCP
      port: 5432
  - to:                      # DNS
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53

---
# ─── Policy for Database pods ──────────────────────────────────────
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: database-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: database

  policyTypes:
  - Ingress
  - Egress

  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: backend       # ONLY backend can reach the database
    ports:
    - protocol: TCP
      port: 5432

  egress:
  - to:                      # DNS only
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
```

---

## ⚡ Tricky Selector Combinations

### AND vs OR — The Most Important Nuance

```yaml
from:
- podSelector:
    matchLabels:
      app: frontend
  namespaceSelector:          # SAME list item = AND
    matchLabels:
      environment: production

# Reads as: "FROM pods labelled app=frontend AND in a namespace labelled environment=production"
# Both conditions must be true simultaneously
```

```yaml
from:
- podSelector:
    matchLabels:
      app: frontend
- namespaceSelector:          # DIFFERENT list items = OR
    matchLabels:
      environment: production

# Reads as: "FROM pods labelled app=frontend OR from any pod in a namespace labelled environment=production"
# Either condition being true is enough
```

> **This is the most common NetworkPolicy mistake.** YAML list items (`-`) create OR. Fields on the same item create AND.

---

## 🐛 Debugging NetworkPolicy

NetworkPolicy issues are silent — traffic just gets blocked, no error message is sent back.

```bash
# 1. Check if your CNI supports NetworkPolicy
kubectl get pods -n kube-system
# Look for calico, cilium, or weave pods

# 2. Check what policies apply to a pod
# (Get all policies in the namespace, check selectors manually)
kubectl get networkpolicies -n production
kubectl describe networkpolicy backend-policy -n production

# 3. Test from a debug pod
kubectl run debug --image=nicolaka/netshoot -it --rm -- bash
# Inside:
curl http://backend-svc:8080    # Should work from frontend pod context
curl http://database-svc:5432   # Should be blocked from frontend

# 4. Check namespace labels (used in namespaceSelector)
kubectl get namespace --show-labels

# 5. Check pod labels (used in podSelector)
kubectl get pods --show-labels -n production
```

---

## 🧪 Test Yourself

1. **Without any NetworkPolicy applied, can a pod in `namespace-a` reach a pod in `namespace-b`?** Is this dangerous? Why?

2. **A NetworkPolicy with `podSelector: {}` and `policyTypes: [Ingress]` and NO `ingress` rules — what does this do?**

3. **Explain the difference between:**
   ```yaml
   from:
   - podSelector:
       matchLabels: { app: frontend }
     namespaceSelector:
       matchLabels: { env: prod }
   ```
   **and:**
   ```yaml
   from:
   - podSelector:
       matchLabels: { app: frontend }
   - namespaceSelector:
       matchLabels: { env: prod }
   ```

4. **You apply a default-deny-egress policy. Your pod can no longer resolve DNS. What was missing from your egress rules?**

5. **Your CNI is Flannel (no NetworkPolicy support). You apply a NetworkPolicy. What happens?**

6. **You want ONLY pods from the `monitoring` namespace to be able to scrape your backend pods on port 9090. Write the NetworkPolicy.**

7. **After applying a NetworkPolicy, how do you test that it's actually blocking traffic?** Describe the exact commands.

8. **What is `ipBlock`? Give a real-world scenario where you'd use it instead of `podSelector` or `namespaceSelector`.**
