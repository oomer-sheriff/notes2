# Homework P2-1 — ConfigMaps: All Three Injection Methods

> **Time:** 2 hours  
> **Goal:** Create ConfigMaps three ways and inject them three ways — env var, envFrom, and volume mount. Prove the hot-reload behaviour difference.

---

## 🚀 Setup

```powershell
kubectl create namespace lab-cm
kubectl config set-context --current --namespace=lab-cm
```

---

## Part 1 — Create ConfigMaps (Three Ways) (20 min)

### Task 1.1 — From Literals

```powershell
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=debug \
  --from-literal=MAX_CONNECTIONS=10 \
  --from-literal=APP_ENV=development \
  -n lab-cm

# Inspect it
kubectl get configmap app-config -o yaml -n lab-cm
```

**Fill in:**  
What format is the data stored in — plain text, base64, or something else?

---

### Task 1.2 — From a File

Save this as `lab-files/app.properties`:
```properties
server.port=8080
spring.datasource.url=jdbc:postgresql://postgres:5432/mydb
logging.level.root=INFO
feature.dark-mode=true
feature.new-checkout=false
```

```powershell
kubectl create configmap file-config \
  --from-file=d:\learning\k8s\phase-2-config-secrets\homework\lab-files\app.properties \
  -n lab-cm

kubectl describe configmap file-config -n lab-cm
```

**What is the key name that was created?**  
(Hint: it's the filename itself)

---

### Task 1.3 — From YAML (Best Practice)

Save as `lab-files/full-configmap.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
  namespace: lab-cm
  labels:
    app: nginx
    phase: lab
data:
  # Simple values — injected as env vars
  UPSTREAM_HOST: "backend-svc"
  UPSTREAM_PORT: "8080"
  WORKER_PROCESSES: "auto"

  # File content — injected as files via volume mount
  default.conf: |
    server {
        listen 80;
        server_name _;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        
        location /health {
            return 200 'OK\n';
            add_header Content-Type text/plain;
        }
        
        location /api {
            proxy_pass http://backend-svc:8080;
            proxy_set_header Host $host;
        }
    }

  gzip.conf: |
    gzip on;
    gzip_types text/plain application/json;
    gzip_min_length 1000;
```

```powershell
kubectl apply -f lab-files/full-configmap.yaml

# Verify all keys exist
kubectl get configmap nginx-config -n lab-cm -o jsonpath='{.data}' | python -m json.tool
# OR just:
kubectl describe configmap nginx-config -n lab-cm
```

---

## Part 2 — Inject ConfigMap as Environment Variables (30 min)

### Task 2.1 — Specific Keys (`env.valueFrom`)

Save as `lab-files/pod-env.yaml`:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: env-demo
  namespace: lab-cm
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'env | sort; echo "---sleeping---"; sleep 3600']
    env:
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: LOG_LEVEL
    - name: MAX_CONN
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: MAX_CONNECTIONS
    - name: ENVIRONMENT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: APP_ENV
    resources:
      requests:
        memory: "32Mi"
        cpu: "50m"
      limits:
        memory: "64Mi"
        cpu: "100m"
```

```powershell
kubectl apply -f lab-files/pod-env.yaml

# Wait for Running, then check logs
kubectl logs env-demo -n lab-cm | grep -E "LOG_LEVEL|MAX_CONN|ENVIRONMENT"

# Verify inside the container
kubectl exec env-demo -n lab-cm -- env | grep -E "LOG_LEVEL|MAX_CONN|ENVIRONMENT"
```

**Fill in:**

| Env Var Name in Container | ConfigMap Key | Value |
|--------------------------|--------------|-------|
| `LOG_LEVEL` | `LOG_LEVEL` | |
| `MAX_CONN` | `MAX_CONNECTIONS` | |
| `ENVIRONMENT` | `APP_ENV` | |

---

### Task 2.2 — All Keys at Once (`envFrom`)

```powershell
kubectl run envfrom-demo \
  --image=busybox:1.35 \
  --restart=Never \
  --env-from=configmap/app-config \
  -n lab-cm \
  -- sh -c 'env | sort; sleep 3600'

# Wait for Running
kubectl logs envfrom-demo -n lab-cm
```

**Observation:** All three keys (`LOG_LEVEL`, `MAX_CONNECTIONS`, `APP_ENV`) should appear as env vars. Notice the key names are EXACTLY as they appear in the ConfigMap.

---

### Task 2.3 — The Hot-Reload Test (env vars DON'T update)

```powershell
# Check current LOG_LEVEL in the running pod
kubectl exec env-demo -n lab-cm -- env | grep LOG_LEVEL
# Output: LOG_LEVEL=debug

# Update the ConfigMap
kubectl patch configmap app-config -n lab-cm \
  --type=merge -p '{"data":{"LOG_LEVEL":"info"}}'

# Verify ConfigMap changed
kubectl get configmap app-config -n lab-cm -o jsonpath='{.data.LOG_LEVEL}'

# Wait 30 seconds then check the running pod again
kubectl exec env-demo -n lab-cm -- env | grep LOG_LEVEL
# Output: LOG_LEVEL=debug   ← STILL DEBUG! No hot-reload for env vars!
```

**Key takeaway:** Write in your notes: *"Env vars are baked in at pod startup. ConfigMap changes do NOT propagate to env vars in running pods."*

---

## Part 3 — Inject as Volume (Hot-Reload Demo) (40 min)

### Task 3.1 — Volume Mount

Save as `lab-files/nginx-volume.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-configvol
  namespace: lab-cm
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-configvol
  template:
    metadata:
      labels:
        app: nginx-configvol
    spec:
      containers:
      - name: nginx
        image: nginx:1.25
        volumeMounts:
        - name: nginx-conf
          mountPath: /etc/nginx/conf.d    # ← REPLACES this directory's contents!
          readOnly: true
        resources:
          requests:
            memory: "64Mi"
            cpu: "100m"
          limits:
            memory: "128Mi"
            cpu: "200m"

      volumes:
      - name: nginx-conf
        configMap:
          name: nginx-config             # Our ConfigMap from Task 1.3
```

```powershell
kubectl apply -f lab-files/nginx-volume.yaml

# Get the pod name
POD=$(kubectl get pods -n lab-cm -l app=nginx-configvol -o jsonpath='{.items[0].metadata.name}')

# Verify the files exist inside the container
kubectl exec $POD -n lab-cm -- ls /etc/nginx/conf.d/
# Expected: default.conf  gzip.conf  UPSTREAM_HOST  UPSTREAM_PORT  WORKER_PROCESSES

kubectl exec $POD -n lab-cm -- cat /etc/nginx/conf.d/default.conf
# Should show the nginx config from your ConfigMap!
```

**Note:** ALL keys become files — even `UPSTREAM_HOST` becomes a file named `UPSTREAM_HOST` with the value `backend-svc` as its content. This is why `items:` selective mounting is useful.

---

### Task 3.2 — The Hot-Reload Test (volumes DO update!)

```powershell
# Check the current default.conf content
POD=$(kubectl get pods -n lab-cm -l app=nginx-configvol -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -n lab-cm -- cat /etc/nginx/conf.d/default.conf | grep "return 200"
# Should show: return 200 'OK\n';

# Update the ConfigMap — change the health endpoint response
kubectl patch configmap nginx-config -n lab-cm --type=merge -p '
{"data":{"default.conf":"server {\n    listen 80;\n    location / {\n        root /usr/share/nginx/html;\n    }\n    location /health {\n        return 200 '"'"'UPDATED!\n'"'"';\n        add_header Content-Type text/plain;\n    }\n}\n"}}'

# Wait 60-90 seconds (kubelet sync interval), then check:
kubectl exec $POD -n lab-cm -- cat /etc/nginx/conf.d/default.conf | grep "return 200"
# Should now show: return 200 'UPDATED!';

# Note: nginx itself won't reload automatically (that's the app's job to watch files)
# But the FILE on disk IS updated by K8s.
```

---

## Part 4 — Challenge: Downward API (20 min)

### Task 4.1 — Inject Pod Metadata as Environment Variables

```yaml
# Save as lab-files/downward-api.yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward-demo
  namespace: lab-cm
  labels:
    app: downward-demo
    team: backend
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'echo "I am $MY_POD_NAME on $MY_NODE_NAME in $MY_NAMESPACE"; env | grep MY_; sleep 3600']
    env:
    - name: MY_POD_NAME
      valueFrom:
        fieldRef:
          fieldPath: metadata.name
    - name: MY_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: MY_POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
    - name: MY_NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
    - name: MY_TEAM_LABEL
      valueFrom:
        fieldRef:
          fieldPath: metadata.labels['team']
    resources:
      requests:
        memory: "32Mi"
        cpu: "50m"
      limits:
        memory: "64Mi"
        cpu: "100m"
```

```powershell
kubectl apply -f lab-files/downward-api.yaml
kubectl logs downward-demo -n lab-cm
# Expected: I am downward-demo on k8s-multinode-worker in lab-cm
```

**What is the pod IP?**  
Compare it to `kubectl get pod downward-demo -o wide -n lab-cm`. Match?

---

## 🧹 Cleanup

```powershell
kubectl delete namespace lab-cm
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] Three ConfigMaps created (literals, file, YAML)
- [ ] Env var injection table completed
- [ ] HOT-RELOAD TEST: Proved env vars DON'T update in running pods
- [ ] Volume mount working — files visible inside container
- [ ] HOT-RELOAD TEST: Proved volume-mounted files DO update (after ~60-90s)
- [ ] Downward API: Pod name, node, namespace visible as env vars

## 📝 Reflection

**When would you choose a volume mount over env vars for ConfigMap injection?**
```

```

**The hot-reload test — what are the operational implications?**
```

```
