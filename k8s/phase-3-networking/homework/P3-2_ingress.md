# Homework P3-2 — Ingress Controller & Routing Lab

> **Time:** 2.5 hours  
> **Goal:** Install NGINX Ingress Controller, configure path-based and host-based routing, test TLS termination, and understand how the controller translates Ingress resources into nginx config.

---

## 🚀 Setup

```powershell
# Verify your kind cluster has port mappings for port 80
# Check kind-config.yaml — should have containerPort: 30080 or port 80 mapped
kubectl get nodes

# Install NGINX Ingress Controller for kind
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for it to become ready (can take 60-90s)
kubectl wait --namespace ingress-nginx `
  --for=condition=ready pod `
  --selector=app.kubernetes.io/component=controller `
  --timeout=120s

# Verify the controller is running
kubectl get pods -n ingress-nginx
kubectl get services -n ingress-nginx
```

**What port does the ingress-nginx service expose?**  
```powershell
kubectl get svc -n ingress-nginx ingress-nginx-controller
```

---

## Part 1 — Deploy Three Backend Services (20 min)

### Task 1.1 — Deploy the Apps

Save as `lab-files/backends.yaml`:

```yaml
---
# Service A: web frontend
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo
        args: ["-text=I am the WEB APP"]
        ports:
        - containerPort: 5678
        resources:
          requests: { memory: "32Mi", cpu: "50m" }
          limits: { memory: "64Mi", cpu: "100m" }
---
apiVersion: v1
kind: Service
metadata:
  name: web-app-svc
  namespace: default
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 5678
---
# Service B: API
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-app
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-app
  template:
    metadata:
      labels:
        app: api-app
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo
        args: ["-text=I am the API"]
        ports:
        - containerPort: 5678
        resources:
          requests: { memory: "32Mi", cpu: "50m" }
          limits: { memory: "64Mi", cpu: "100m" }
---
apiVersion: v1
kind: Service
metadata:
  name: api-app-svc
  namespace: default
spec:
  selector:
    app: api-app
  ports:
  - port: 80
    targetPort: 5678
---
# Service C: Admin
apiVersion: apps/v1
kind: Deployment
metadata:
  name: admin-app
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: admin-app
  template:
    metadata:
      labels:
        app: admin-app
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo
        args: ["-text=I am the ADMIN PANEL"]
        ports:
        - containerPort: 5678
        resources:
          requests: { memory: "32Mi", cpu: "50m" }
          limits: { memory: "64Mi", cpu: "100m" }
---
apiVersion: v1
kind: Service
metadata:
  name: admin-app-svc
  namespace: default
spec:
  selector:
    app: admin-app
  ports:
  - port: 80
    targetPort: 5678
```

```powershell
kubectl apply -f lab-files/backends.yaml
kubectl get pods
kubectl get services
```

---

## Part 2 — Path-Based Routing (30 min)

### Task 2.1 — Single Host, Multiple Paths

Save as `lab-files/path-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: path-based-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.local     # We'll fake this with /etc/hosts
    http:
      paths:
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-app-svc
            port:
              number: 80
      - path: /admin
        pathType: Prefix
        backend:
          service:
            name: admin-app-svc
            port:
              number: 80
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-svc
            port:
              number: 80
```

```powershell
kubectl apply -f lab-files/path-ingress.yaml
kubectl get ingress
kubectl describe ingress path-based-ingress
```

### Task 2.2 — Test With curl (Using Host Header)

```powershell
# Find the NodePort for the ingress controller
$HTTP_PORT = $(kubectl get svc -n ingress-nginx ingress-nginx-controller `
  -o jsonpath='{.spec.ports[?(@.name=="http")].nodePort}')
Write-Host "Ingress HTTP port: $HTTP_PORT"

# Test each path using Host header:
curl -H "Host: myapp.local" "http://localhost:$HTTP_PORT/"
# Expected: I am the WEB APP

curl -H "Host: myapp.local" "http://localhost:$HTTP_PORT/api"
# Expected: I am the API

curl -H "Host: myapp.local" "http://localhost:$HTTP_PORT/admin"
# Expected: I am the ADMIN PANEL

curl -H "Host: myapp.local" "http://localhost:$HTTP_PORT/api/users"
# Expected: I am the API  (Prefix match — /api/* all goes to API)
```

**Fill in:**

| URL Path | Backend Hit | Why? |
|----------|------------|------|
| `/` | | |
| `/api` | | |
| `/admin` | | |
| `/api/anything` | | |
| `/adminsomething` | | |

---

## Part 3 — Host-Based Routing (30 min)

### Task 3.1 — Multiple Hosts, One Ingress

Save as `lab-files/host-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: host-based-ingress
  namespace: default
spec:
  ingressClassName: nginx
  rules:
  - host: web.myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-svc
            port:
              number: 80
  - host: api.myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-app-svc
            port:
              number: 80
  - host: admin.myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-app-svc
            port:
              number: 80
```

```powershell
kubectl apply -f lab-files/host-ingress.yaml

# Test each virtual host:
curl -H "Host: web.myapp.local" "http://localhost:$HTTP_PORT/"
curl -H "Host: api.myapp.local" "http://localhost:$HTTP_PORT/"
curl -H "Host: admin.myapp.local" "http://localhost:$HTTP_PORT/"

# What happens with an unknown Host?
curl -H "Host: unknown.myapp.local" "http://localhost:$HTTP_PORT/"
# Expected: 404 from NGINX (no matching rule)
```

---

## Part 4 — TLS Termination (30 min)

### Task 4.1 — Generate a Self-Signed Certificate

```powershell
# Run in WSL or Git Bash:
# openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
#   -keyout tls.key -out tls.crt `
#   -subj "/CN=secure.myapp.local" `
#   -addext "subjectAltName=DNS:secure.myapp.local"

# PowerShell alternative using .NET:
$cert = New-SelfSignedCertificate `
  -DnsName "secure.myapp.local" `
  -CertStoreLocation "cert:\CurrentUser\My" `
  -NotAfter (Get-Date).AddYears(1)

$certPath = "lab-files\tls.crt"
$keyPath = "lab-files\tls.key"

# Export cert and key (you'll need to import to K8s)
# Alternatively, use the openssl command in WSL
```

For simplicity, use WSL:
```bash
# In WSL terminal:
cd /mnt/d/learning/k8s/phase-3-networking/homework/lab-files
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=secure.myapp.local" 2>/dev/null
ls -la tls.crt tls.key
```

### Task 4.2 — Create the TLS Secret and Ingress

```powershell
# Create the TLS secret
kubectl create secret tls myapp-tls `
  --cert=lab-files/tls.crt `
  --key=lab-files/tls.key

kubectl get secret myapp-tls
kubectl describe secret myapp-tls
```

Save as `lab-files/tls-ingress.yaml`:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
  namespace: default
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - secure.myapp.local
    secretName: myapp-tls           # Our self-signed cert

  rules:
  - host: secure.myapp.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-app-svc
            port:
              number: 80
```

```powershell
kubectl apply -f lab-files/tls-ingress.yaml

# Find HTTPS port
$HTTPS_PORT = $(kubectl get svc -n ingress-nginx ingress-nginx-controller `
  -o jsonpath='{.spec.ports[?(@.name=="https")].nodePort}')

# Test HTTPS (ignore cert warning with -k since it's self-signed)
curl -k -H "Host: secure.myapp.local" "https://localhost:$HTTPS_PORT/"
# Expected: I am the WEB APP (over HTTPS!)

# Verify the cert details
curl -k -v -H "Host: secure.myapp.local" "https://localhost:$HTTPS_PORT/" 2>&1 | `
  Select-String "subject|issuer|CN"
```

---

## Part 5 — Inspect the NGINX Config Generated (15 min)

### Task 5.1 — See How Ingress Becomes nginx.conf

```powershell
# Get the nginx ingress controller pod name
$NGINX_POD = $(kubectl get pods -n ingress-nginx `
  -l app.kubernetes.io/component=controller `
  -o jsonpath='{.items[0].metadata.name}')

# Read the actual nginx.conf the controller generated!
kubectl exec $NGINX_POD -n ingress-nginx -- cat /etc/nginx/nginx.conf | Select-String -Pattern "server_name|proxy_pass|upstream" -Context 2,0
```

**What do you see?** The Ingress rules you wrote are now live nginx configuration.

---

## 🧹 Cleanup

```powershell
kubectl delete ingress --all
kubectl delete -f lab-files/backends.yaml
kubectl delete secret myapp-tls
```

---

## ✅ Done When:

- [ ] NGINX Ingress Controller installed and running
- [ ] Path-based routing: all 3 paths routing to correct backends
- [ ] Path-based routing table filled in
- [ ] Host-based routing: 3 virtual hosts working
- [ ] TLS: HTTPS working with self-signed cert
- [ ] nginx.conf inspected and routing rules visible

## 📝 Reflection

**What is the `rewrite-target: /` annotation doing in the path-based ingress?**
```

```

**Why do you need the `Host` header when testing from localhost?**
```

```
