# 03 — Ingress: Routing External Traffic Into the Cluster

> **The problem Services alone don't solve:** You have 10 microservices. Each one exposed as a LoadBalancer Service = 10 cloud load balancers = expensive and unmanageable. Ingress solves this with a single entry point that routes to all of them based on URL path or hostname.

---

## 🚪 Ingress vs Service — What's the Difference?

You already know Services. Here's where they fall short for HTTP traffic:

```
Services alone (expensive, unmanageable):
  
  Internet → LB-1 (34.1.2.3) → api.example.com        → api-service
  Internet → LB-2 (34.1.2.4) → shop.example.com       → shop-service
  Internet → LB-3 (34.1.2.5) → admin.example.com      → admin-service
  Internet → LB-4 (34.1.2.6) → api.example.com/v2     → api-v2-service
  
  4 cloud load balancers → $$$, 4 public IPs to manage

Ingress (single entry point):
  
  Internet → 1 LB (34.1.2.3) → NGINX Ingress Controller
                                        │
                              ┌─────────┼──────────────┐
                              ▼         ▼              ▼
                 api.example.com  shop.example.com  /admin
                       │               │               │
                  api-service     shop-service    admin-service
  
  1 cloud load balancer → $, 1 public IP, unlimited routing rules
```

---

## 🏗️ The Two-Layer Architecture

Ingress in K8s has two separate pieces. **Beginners constantly confuse them:**

```
Layer 1: INGRESS RESOURCE (YAML you write)
  ┌─────────────────────────────────────┐
  │  apiVersion: networking.k8s.io/v1   │
  │  kind: Ingress                      │
  │  metadata:                          │
  │    name: my-ingress                 │
  │  spec:                              │
  │    rules:                           │
  │    - host: api.example.com          │
  │      http:                          │
  │        paths:                       │
  │        - path: /                    │
  │          backend:                   │
  │            service:                 │
  │              name: api-svc          │  ← This is just DECLARATIVE CONFIG.
  │              port: 80               │    On its own, it does NOTHING.
  └─────────────────────────────────────┘

Layer 2: INGRESS CONTROLLER (deployed separately!)
  ┌─────────────────────────────────────────────────────────────────┐
  │  A pod (usually NGINX, Traefik, or HAProxy) running in kube-ns  │
  │  - Watches the API server for Ingress resources                 │
  │  - Reads the routing rules                                      │
  │  - Configures itself (e.g., updates nginx.conf)                 │
  │  - Actually proxies the traffic                                 │
  └─────────────────────────────────────────────────────────────────┘
```

> **Analogy:** The Ingress Resource is like a **set of traffic rules** you post on a sign ("Turn left for downtown, right for airport").  
> The Ingress Controller is the **actual traffic officer** reading those signs and directing cars.  
> Signs without an officer = nothing happens. Officer without signs = no routing.

**Popular Ingress Controllers:**

| Controller | Best For | Notes |
|-----------|---------|-------|
| **NGINX Ingress** | General purpose | Most widely used, battle-tested |
| **Traefik** | Microservices, auto-discovery | Great GitOps integration |
| **AWS ALB** | AWS EKS clusters | Native AWS Application Load Balancer |
| **GCE** | GKE clusters | Native GCP load balancing |
| **Istio Gateway** | Service mesh | Used when Istio is already deployed |

---

## 🔧 Installing NGINX Ingress Controller (kind)

```bash
# Install NGINX Ingress Controller (kind-specific version with NodePort)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for it to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=90s

# Verify
kubectl get pods -n ingress-nginx
kubectl get service -n ingress-nginx
```

After installation, the Ingress Controller is exposed as a NodePort on ports `80` and `443`. With kind's port mappings (from your `kind-config.yaml`), these are accessible at `localhost:80` and `localhost:443`.

---

## 📋 Ingress Resource — Fully Annotated

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  namespace: production
  annotations:
    # Ingress class — tells K8s which controller handles this
    kubernetes.io/ingress.class: "nginx"
    
    # NGINX-specific tuning (annotations vary by controller!)
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

spec:
  # (Optional) Specify which IngressClass to use
  ingressClassName: nginx

  # TLS configuration
  tls:
  - hosts:
    - api.example.com
    - shop.example.com
    secretName: my-tls-secret      # TLS cert+key stored here

  rules:
  # Rule 1: Host-based routing
  - host: api.example.com          # Only traffic with this Host header
    http:
      paths:
      - path: /v1                  # Path prefix
        pathType: Prefix           # Prefix, Exact, or ImplementationSpecific
        backend:
          service:
            name: api-v1-svc
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2-svc
            port:
              number: 80

  # Rule 2: Different host
  - host: shop.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: shop-svc
            port:
              number: 80

  # Rule 3: No host specified = catch-all (matches any Host header)
  - http:
      paths:
      - path: /health
        pathType: Exact             # Only exact match
        backend:
          service:
            name: healthcheck-svc
            port:
              number: 80
```

---

## 🗺️ Path Types Explained

```
pathType: Prefix
  path: /api
  Matches: /api, /api/, /api/v1, /api/users/123
  Does NOT match: /apikey, /apiv2  (only on / boundaries)

pathType: Exact
  path: /api
  Matches: /api ONLY
  Does NOT match: /api/, /api/v1

pathType: ImplementationSpecific
  Controller decides the matching logic (avoid in production for portability)
```

---

## 🌐 Routing Patterns in Practice

### Pattern 1: Single Host, Path-Based Routing

```
User → api.example.com/users     → user-service
User → api.example.com/orders    → order-service
User → api.example.com/products  → product-service
```

```yaml
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /users
        pathType: Prefix
        backend:
          service: { name: user-svc, port: { number: 80 } }
      - path: /orders
        pathType: Prefix
        backend:
          service: { name: order-svc, port: { number: 80 } }
      - path: /products
        pathType: Prefix
        backend:
          service: { name: product-svc, port: { number: 80 } }
      - path: /
        pathType: Prefix
        backend:
          service: { name: frontend-svc, port: { number: 80 } }
```

> ⚠️ **Order matters!** More specific paths first. `/users` before `/`. Otherwise `/` catches everything.

### Pattern 2: Multi-Host (Virtual Hosting)

```
User → api.myapp.com      → api-service
User → shop.myapp.com     → shop-service
User → admin.myapp.com    → admin-service
```

```yaml
spec:
  rules:
  - host: api.myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service: { name: api-svc, port: { number: 80 } }
  - host: shop.myapp.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service: { name: shop-svc, port: { number: 80 } }
```

**Testing locally without real DNS:** Use the `Host` HTTP header to simulate:
```bash
# Send request to localhost but with custom Host header
curl -H "Host: api.myapp.com" http://localhost:80/
curl -H "Host: shop.myapp.com" http://localhost:80/
```

Or add to Windows hosts file (`C:\Windows\System32\drivers\etc\hosts`):
```
127.0.0.1  api.myapp.com
127.0.0.1  shop.myapp.com
```

---

## 🔒 TLS Termination

TLS at the Ingress means: HTTPS from the client to the Ingress Controller, plain HTTP from the Controller to the backend service. The Controller handles certificates.

```
Client ──HTTPS──→ [Ingress Controller] ──HTTP──→ backend-svc
                  (handles TLS)
```

### Step 1: Create a TLS Secret

```bash
# Generate a self-signed cert (for testing only!)
# For production: use cert-manager with Let's Encrypt
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key \
  -out tls.crt \
  -subj "/CN=myapp.example.com/O=MyOrg" \
  -addext "subjectAltName=DNS:myapp.example.com,DNS:*.myapp.example.com"

# Create TLS secret
kubectl create secret tls myapp-tls \
  --cert=tls.crt \
  --key=tls.key
```

### Step 2: Reference in Ingress

```yaml
spec:
  tls:
  - hosts:
    - myapp.example.com
    secretName: myapp-tls    # The TLS secret

  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-svc
            port:
              number: 80
```

### cert-manager — Automated Certificate Management

In production, you never manage certs manually. **cert-manager** is the de-facto standard:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml

# Create a ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: you@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

Then in your Ingress, add an annotation:
```yaml
annotations:
  cert-manager.io/cluster-issuer: "letsencrypt-prod"
```

cert-manager automatically provisions a Let's Encrypt cert and stores it in a Secret. Renewal is automatic.

---

## 🔄 How NGINX Ingress Controller Works Internally

```
1. You apply an Ingress resource
            │
2. NGINX Controller watches API server, sees the new Ingress
            │
3. Controller generates nginx.conf based on Ingress rules:
   
   upstream api-svc-production-80 {
     server 10.244.1.4:8080;  # pod IPs from Endpoints
     server 10.244.2.7:8080;
   }
   
   server {
     listen 80;
     server_name api.example.com;
     
     location /v1 {
       proxy_pass http://api-svc-production-80;
     }
   }

4. Controller applies the new nginx.conf (hot reload, no downtime)

5. Traffic arrives at controller pod, nginx routes it
   to one of the backend pod IPs
```

---

## 🧪 Test Yourself

1. **What is the difference between an Ingress Resource and an Ingress Controller?** Why do you need both?

2. **You have 5 microservices, each needing external HTTPS access. Compare the cost/complexity of: (a) 5 LoadBalancer Services vs (b) 1 Ingress with 5 rules.**

3. **`pathType: Prefix` with path `/api`. Does it match `/apikey`?** Why or why not?

4. **A request arrives at `api.example.com/users/123`. You have rules for `/users` and `/`. Which rule wins?**

5. **You configure TLS in the Ingress. Is traffic encrypted between the Ingress Controller and the backend service?** What would you need if you also wanted backend encryption?

6. **You're testing locally with a kind cluster. DNS doesn't resolve `api.myapp.com`. How do you test your Ingress host-based routing without real DNS?**

7. **The Ingress is configured correctly but returns 503. What is the most likely cause?** How do you diagnose it?

8. **What does cert-manager do and why is it important in production?**
