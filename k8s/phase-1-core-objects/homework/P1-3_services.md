# Homework P1-3 — Services & DNS Communication

> **Time:** 2 hours  
> **Goal:** Build a multi-service application and prove that pods can find each other by DNS name, not IP. Experience all Service types and understand what each one actually does.

---

## 🚀 Setup

```powershell
kubectl create namespace lab3
kubectl config set-context --current --namespace=lab3
```

---

## Part 1 — ClusterIP Service + Internal DNS (45 min)

### Task 1.1 — Deploy a Backend Service

```yaml
# Save as: lab-files/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: lab3
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: echo-server
        # http-echo replies with a configurable message — great for testing
        image: hashicorp/http-echo:latest
        args:
        - "-text=Hello from the Backend! Pod: $(MY_POD_NAME)"
        - "-listen=:5678"
        env:
        - name: MY_POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name    # Inject pod name as env var
        ports:
        - containerPort: 5678
        resources:
          requests:
            memory: "32Mi"
            cpu: "50m"
          limits:
            memory: "64Mi"
            cpu: "100m"
---
apiVersion: v1
kind: Service
metadata:
  name: backend-svc
  namespace: lab3
spec:
  type: ClusterIP
  selector:
    app: backend       # Routes to pods with this label
  ports:
  - port: 80           # Service listens on 80
    targetPort: 5678   # Pod's container listens on 5678
```

```powershell
kubectl apply -f lab-files/backend.yaml

# Verify deployment and service
kubectl get deployments,services,endpoints -n lab3
```

**Fill in:**

| Question | Answer |
|----------|--------|
| What is the Service's ClusterIP? | |
| What pod IPs are in the Endpoints? | |
| What port does the Service listen on? | |
| What port does the pod container actually listen on? | |

---

### Task 1.2 — Test DNS from Inside the Cluster

Launch a debug pod to test connectivity from within the cluster network:

```powershell
# Method 1: curl from a temporary pod (recommended)
kubectl run curl-test --image=curlimages/curl:latest \
  --restart=Never -it --rm -n lab3 \
  -- curl http://backend-svc:80

# Expected output: Hello from the Backend! Pod: backend-xxxxxxxx

# Method 2: Get a persistent shell for multiple tests
kubectl run debug-shell --image=nicolaka/netshoot \
  --restart=Never -it --rm -n lab3 -- bash
```

Inside the debug shell, run ALL of these:

```bash
# Test 1: Short name (same namespace = works!)
curl http://backend-svc
curl http://backend-svc:80

# Test 2: Full DNS name
curl http://backend-svc.lab3.svc.cluster.local

# Test 3: Direct pod IP (DON'T do this in production — demo only!)
curl http://<pod-ip>:5678

# Test 4: DNS lookup
nslookup backend-svc
nslookup backend-svc.lab3.svc.cluster.local

# Test 5: See search domains
cat /etc/resolv.conf

# Test 6: Prove load balancing — run this 10 times, note which pod replies
for i in $(seq 1 10); do curl -s http://backend-svc; echo; done
exit
```

**Fill in:**

| DNS Name Used | Did It Work? | Why? |
|--------------|-------------|------|
| `backend-svc` | | |
| `backend-svc.lab3` | | |
| `backend-svc.lab3.svc.cluster.local` | | |
| Direct pod IP | | |

**Did load balancing work?** Did different pods respond to different requests?

---

### Task 1.3 — Cross-Namespace DNS

```powershell
# Create a pod in a DIFFERENT namespace
kubectl create namespace lab3b

kubectl run cross-ns-test --image=curlimages/curl:latest \
  --restart=Never -it --rm -n lab3b \
  -- curl http://backend-svc.lab3.svc.cluster.local

# Expected: Hello from the Backend!
# This proves cross-namespace communication works with full DNS name
```

```powershell
# Now try the short name from a different namespace (should FAIL)
kubectl run cross-ns-test --image=curlimages/curl:latest \
  --restart=Never -it --rm -n lab3b \
  -- curl http://backend-svc

# Expected: curl: (6) Could not resolve host: backend-svc
# Short names only work within the SAME namespace
```

**Cleanup:**
```powershell
kubectl delete namespace lab3b
```

---

## Part 2 — The Selector Link (Very Important!) (20 min)

### Task 2.1 — Break the Service (Selector Mismatch)

```powershell
# Check current endpoints
kubectl get endpoints backend-svc -n lab3
# Should show 2 pod IPs

# Patch the service selector to a WRONG label
kubectl patch service backend-svc -n lab3 \
  -p '{"spec":{"selector":{"app":"backend-BROKEN"}}}'

# Check endpoints — should now be EMPTY!
kubectl get endpoints backend-svc -n lab3

# Try to reach the service
kubectl run curl-test --image=curlimages/curl --restart=Never -it --rm -n lab3 \
  -- curl --max-time 5 http://backend-svc
# Expected: Connection timeout! Service exists but has no endpoints.
```

**This is the #1 cause of "my service isn't working" errors.**

```powershell
# Fix it — restore correct selector
kubectl patch service backend-svc -n lab3 \
  -p '{"spec":{"selector":{"app":"backend"}}}'

kubectl get endpoints backend-svc -n lab3
# Should show IPs again
```

---

## Part 3 — NodePort Service (30 min)

### Task 3.1 — Create a NodePort Service

```yaml
# Save as: lab-files/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: lab3
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
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
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-svc
  namespace: lab3
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080    # We mapped this in kind-config.yaml!
```

```powershell
kubectl apply -f lab-files/frontend.yaml

kubectl get service frontend-svc -n lab3
# Note the NodePort (30080)

# Access from your Windows browser or curl:
curl http://localhost:30080
# Expected: nginx welcome page!
```

**Why does this work?** Look back at your `kind-config.yaml` — you mapped container port 30080 to host port 30080.

---

## Part 4 — Port-Forward for ClusterIP Services (15 min)

### Task 4.1 — Access a ClusterIP Service Locally

ClusterIP is NOT accessible from outside the cluster. But `port-forward` creates a temporary tunnel:

```powershell
# Forward local port 8080 to the ClusterIP service's port 80
kubectl port-forward service/backend-svc 8080:80 -n lab3

# In a SECOND terminal:
curl http://localhost:8080
# Expected: Hello from the Backend!

# Try it multiple times — note load balancing across pods
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080

# Ctrl+C in the first terminal to stop port-forwarding
```

---

## Part 5 — Challenge: Two Services Talking (30 min)

### Task 5.1 — Frontend Calling Backend

Create a custom nginx config that proxies `/api` calls to the backend service:

```yaml
# Save as: lab-files/nginx-proxy-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-proxy-config
  namespace: lab3
data:
  default.conf: |
    server {
        listen 80;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /api/ {
            # Proxy to backend service using its DNS name!
            proxy_pass http://backend-svc.lab3.svc.cluster.local/;
            proxy_set_header Host backend-svc;
        }
    }
```

```powershell
kubectl apply -f lab-files/nginx-proxy-config.yaml

# Update frontend deployment to mount this config
kubectl patch deployment frontend -n lab3 --type='json' -p='[
  {
    "op": "add",
    "path": "/spec/template/spec/volumes",
    "value": [{"name": "nginx-config", "configMap": {"name": "nginx-proxy-config"}}]
  },
  {
    "op": "add",
    "path": "/spec/template/spec/containers/0/volumeMounts",
    "value": [{"name": "nginx-config", "mountPath": "/etc/nginx/conf.d/"}]
  }
]'

# Test: hit /api/ through the frontend (should proxy to backend)
curl http://localhost:30080/api/
# Expected: Hello from the Backend! Pod: backend-xxxxxxxx
```

**This demonstrates service-to-service communication via internal DNS — the foundation of microservices on K8s.**

---

## 🧹 Cleanup

```powershell
kubectl delete namespace lab3
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] ClusterIP service created and backend accessed from inside cluster
- [ ] DNS resolution table completed (all 4 DNS name forms tested)
- [ ] Cross-namespace DNS tested (full name works, short name doesn't)
- [ ] Selector mismatch deliberately caused and then fixed
- [ ] NodePort service accessible from Windows browser
- [ ] Port-forward tunnel working for ClusterIP
- [ ] Challenge: Frontend proxying to backend via DNS name

---

## 📝 Reflection

**Why should you NEVER hardcode pod IPs in your app config?**
```

```

**What is the difference between `port` and `targetPort` in a Service? Use your lab as an example.**
```

```

**What is the first thing you check when a service isn't routing traffic?**
```

```
