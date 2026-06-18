# ☸️ Phase 3 — Quick Reference Cheat Sheet

---

## Cluster Networking

```bash
# Check pod CIDRs per node
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.podCIDR}{"\n"}{end}'

# Check service CIDR
kubectl describe pod kube-apiserver-<name> -n kube-system | grep service-cluster-ip-range

# Network debug pod (your Swiss army knife)
kubectl run netdebug --image=nicolaka/netshoot -it --rm -- bash
# Has: curl, ping, dig, nslookup, nc, traceroute, tcpdump, ss, ip

# Lightweight one-shot curl test
kubectl run curl-test --image=curlimages/curl -it --rm -- curl http://my-service
```

---

## DNS

```bash
# Launch DNS debug pod
kubectl run dns-debug \
  --image=gcr.io/kubernetes-e2e-test-images/dnsutils:1.3 \
  --restart=Never -it --rm -- sh

# Inside:
nslookup my-service                              # Short name (same namespace)
nslookup my-service.other-ns.svc.cluster.local  # Full FQDN (cross-namespace)
nslookup kubernetes.default                      # K8s API service (always works)
dig my-service.default.svc.cluster.local         # Detailed DNS lookup
cat /etc/resolv.conf                             # See search domains + nameserver

# CoreDNS ConfigMap
kubectl get configmap coredns -n kube-system -o yaml

# CoreDNS pods
kubectl get pods -n kube-system -l k8s-app=kube-dns
```

**DNS Name Format:**
```
<service>.<namespace>.svc.cluster.local
```

**DNS Resolution Order (ndots:5 with search domains):**
```
For query "my-svc" (< 5 dots):
  1. my-svc.<current-namespace>.svc.cluster.local
  2. my-svc.svc.cluster.local
  3. my-svc.cluster.local
  4. my-svc (external)
```

---

## Ingress

```bash
# Install NGINX Ingress (kind)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for it
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Check ingress
kubectl get ingress
kubectl describe ingress my-ingress

# Get ingress ports
kubectl get svc -n ingress-nginx ingress-nginx-controller

# Test with Host header (when no real DNS)
curl -H "Host: myapp.local" http://localhost:<nodeport>/
curl -H "Host: myapp.local" http://localhost:<nodeport>/api

# Create TLS secret
kubectl create secret tls my-tls \
  --cert=tls.crt \
  --key=tls.key
```

**Minimal Ingress YAML:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-svc
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-svc
            port:
              number: 80
```

**Path Types:**
```
Prefix: /api  → matches /api, /api/, /api/v1, /api/users
Exact:  /api  → matches /api ONLY (not /api/)
```

---

## NetworkPolicy

```bash
# List policies
kubectl get networkpolicies
kubectl get netpol            # Short form

# Inspect
kubectl describe networkpolicy my-policy -n my-ns

# Check namespace labels (important for namespaceSelector)
kubectl get namespace --show-labels

# Check pod labels (important for podSelector)
kubectl get pods --show-labels -n my-ns

# Test connectivity from a debug pod
kubectl run test --image=curlimages/curl -it --rm -- curl --max-time 5 http://my-svc
# Timeout = blocked by NetworkPolicy
# Success = allowed
```

**Default Deny All Ingress:**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: my-ns
spec:
  podSelector: {}     # All pods
  policyTypes:
  - Ingress
  # No rules = deny all
```

**Default Deny All Egress (remember: always allow DNS!):**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: my-ns
spec:
  podSelector: {}
  policyTypes:
  - Egress
  egress:
  - to:                     # ALWAYS include DNS!
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
```

---

## The AND vs OR Rule (Critical!)

```yaml
# AND — SAME list item (more restrictive)
from:
- podSelector:
    matchLabels: { role: frontend }
  namespaceSelector:          # ← same dash
    matchLabels: { env: prod }
# Means: FROM pods with role=frontend AND in a namespace with env=prod

# OR — SEPARATE list items (less restrictive)
from:
- podSelector:
    matchLabels: { role: frontend }
- namespaceSelector:          # ← different dash
    matchLabels: { env: prod }
# Means: FROM pods with role=frontend OR from any pod in namespace with env=prod
```

---

## Key Rules to Remember

```
NETWORKING:
1. Every pod gets a unique cluster-wide IP. Pod IPs are flat — no NAT between pods.
2. kube-proxy implements Services via iptables DNAT rules on every node.
3. CNI plugins implement the flat network model. K8s just specifies the rules.

DNS:
4. Short service names only work in the SAME namespace.
   Cross-namespace: always use <name>.<namespace>.svc.cluster.local
5. CoreDNS runs at 10.96.0.10 (or similar). ALL pods use it.
6. Headless services return multiple A records (pod IPs), not one ClusterIP.
7. ndots:5 means <5 dots → search domains tried first.

INGRESS:
8. Ingress Resource = config. Ingress Controller = actual proxy. You need BOTH.
9. More specific paths match first. Put / last.
10. TLS terminates AT the Ingress Controller. Backend communication is plain HTTP.

NETWORK POLICY:
11. Default = allow all. NetworkPolicy = selective deny.
12. Policy requires a CNI that supports it (Calico, Cilium, not kindnet/Flannel alone).
13. policyTypes must include both Ingress AND Egress to restrict both directions.
14. {} in podSelector = ALL pods. {} in a rule = allow from anywhere.
15. ALWAYS allow DNS (port 53) in egress policies or nothing resolves.
16. Same list item = AND. Different list items = OR.
```
