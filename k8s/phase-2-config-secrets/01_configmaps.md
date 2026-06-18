# 01 — ConfigMaps: Decoupling Configuration from Code

> **The twelve-factor app principle #3:** "Store config in the environment."  
> In Kubernetes, ConfigMaps are the mechanism. Your container image should be an immutable artefact. The environment shapes its behaviour.

---

## 🤔 Why ConfigMaps? The Problem They Solve

Imagine you build a Docker image for your web app. Inside the image, you hardcode:
```python
DATABASE_HOST = "postgres.mycompany.com"
LOG_LEVEL = "debug"
MAX_CONNECTIONS = 10
```

**Problems:**
1. To change the log level from `debug` to `info`, you rebuild the entire image
2. The same image can't be used in both `dev` (debug logs) and `prod` (info logs) without changes
3. Anyone who can pull the image can read your config

**The ConfigMap solution:**

```
Image (immutable) + ConfigMap (environment-specific) = Running Pod
   nginx:1.25     +   {LOG_LEVEL=info, HOST=prod-db}  = production pod
   nginx:1.25     +   {LOG_LEVEL=debug, HOST=dev-db}  = development pod

Same image. Different behaviour. No rebuild.
```

> **Analogy:** Your app container is a **DVD player** — the hardware is fixed.  
> ConfigMaps are the **DVDs** — you swap them out to change what plays.  
> You don't buy a new DVD player every time you want to watch a different film.

---

## 📦 What Is a ConfigMap?

A ConfigMap is a **key-value store for non-sensitive configuration data**.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: default
data:
  # Simple key-value pairs (injected as environment variables)
  LOG_LEVEL: "info"
  DATABASE_PORT: "5432"
  MAX_RETRIES: "3"
  FEATURE_FLAG_DARK_MODE: "true"

  # Multi-line value (injected as a file)
  app.properties: |
    server.port=8080
    spring.datasource.url=jdbc:postgresql://postgres:5432/mydb
    logging.level.root=INFO
    
  nginx.conf: |
    server {
        listen 80;
        location / {
            root /usr/share/nginx/html;
        }
        location /api {
            proxy_pass http://api-service:8080;
        }
    }
```

The `data` field holds everything. Values can be:
- Simple strings → great for environment variables
- Multi-line strings → great for config file contents

---

## 🏗️ Creating ConfigMaps — Four Ways

### Method 1: From Literal Key-Value Pairs

```bash
kubectl create configmap app-config \
  --from-literal=LOG_LEVEL=info \
  --from-literal=DATABASE_PORT=5432 \
  --from-literal=MAX_RETRIES=3
```

### Method 2: From a File (filename becomes the key)

```bash
# File: nginx.conf
# Key in ConfigMap: "nginx.conf"
# Value: the file's contents

kubectl create configmap nginx-config --from-file=nginx.conf
kubectl create configmap nginx-config --from-file=my-key=nginx.conf  # custom key name
```

### Method 3: From a Directory (every file becomes a key)

```bash
# All files in ./config/ become keys
kubectl create configmap all-configs --from-file=./config/
# Creates: app.conf, database.conf, feature-flags.conf as separate keys
```

### Method 4: From a YAML File (most version-control-friendly)

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: production
data:
  LOG_LEVEL: "info"
  DATABASE_HOST: "postgres.production.svc.cluster.local"
  app.properties: |
    server.port=8080
    feature.new-ui=false
```

```bash
kubectl apply -f configmap.yaml
```

> 💡 **Best practice:** Always use YAML files (Method 4) in real projects. They go in Git, they have a history, they're reviewable in PRs. Literal creates are fine for quick experiments.

---

## 💉 Injecting ConfigMaps — Three Ways Into a Pod

This is the critical part. Once your ConfigMap exists, you need to get its values INTO a running container. There are three mechanisms.

---

### Mechanism 1: Env Var from a Specific Key

Pick individual keys from the ConfigMap and inject them as named environment variables.

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:latest
    env:
    - name: LOG_LEVEL           # The env var name inside the container
      valueFrom:
        configMapKeyRef:
          name: app-config      # ConfigMap name
          key: LOG_LEVEL        # Key inside the ConfigMap

    - name: DB_PORT
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: DATABASE_PORT
```

Inside the container:
```bash
echo $LOG_LEVEL        # info
echo $DB_PORT          # 5432
```

**Use when:** Your app reads individual env vars. Simple, clean for small numbers of variables.

---

### Mechanism 2: ALL Keys as Env Vars (`envFrom`)

Inject every key from the ConfigMap as an environment variable in one shot.

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:latest
    envFrom:
    - configMapRef:
        name: app-config    # ALL keys become env vars!

    # You can reference multiple ConfigMaps:
    - configMapRef:
        name: feature-flags
```

Inside the container:
```bash
env | grep LOG_LEVEL      # LOG_LEVEL=info
env | grep DATABASE_PORT  # DATABASE_PORT=5432
env | grep MAX_RETRIES    # MAX_RETRIES=3
```

**Use when:** You have many config values and want to inject them all at once. Great for "12-factor" apps that expect their entire config via environment.

**⚠️ Warning:** If a key in the ConfigMap is not a valid environment variable name (e.g., `my-key` with a hyphen), it will be silently skipped.

---

### Mechanism 3: ConfigMap as a Volume (Files on Disk)

Mount the ConfigMap as a directory. Each key becomes a **file**, and the value becomes the **file's contents**.

```yaml
spec:
  containers:
  - name: nginx
    image: nginx:1.25
    volumeMounts:
    - name: nginx-config-volume      # References the volume below
      mountPath: /etc/nginx/conf.d/  # Directory inside container
      readOnly: true

  volumes:
  - name: nginx-config-volume
    configMap:
      name: nginx-config             # The ConfigMap to mount
```

Result inside the container:
```bash
ls /etc/nginx/conf.d/
# nginx.conf   ← file created from the key "nginx.conf"

cat /etc/nginx/conf.d/nginx.conf
# server {
#     listen 80;
#     ...
# }
```

**Use when:**
- Your app reads config from files (nginx, Prometheus, custom apps using `config.yml`)
- You're replacing config files in well-known locations
- The config is too complex for env vars (multi-line, nested structures)

---

### Mechanism 3b: Mount a Specific Key as a File

Sometimes you don't want ALL keys as files — just one specific key at a specific path.

```yaml
volumes:
- name: nginx-config-volume
  configMap:
    name: nginx-config
    items:
    - key: nginx.conf           # Take only this key
      path: default.conf        # Name it this in the volume
```

Result: Only one file `/etc/nginx/conf.d/default.conf` is created, not one per key.

---

## 🔄 ConfigMap Updates — Hot Reload vs. Cold Reload

This is where many people get caught out.

```
                    UPDATE CONFIGMAP
                          │
              ┌───────────┼───────────┐
              │           │           │
        Env Var         Volume      envFrom
        Injection       Mount       Injection
              │           │           │
        NO UPDATE!   AUTO UPDATE   NO UPDATE!
        (need pod    (~60-90s     (need pod
         restart)     delay)       restart)
```

**Environment variables are baked in at pod start.** Changing the ConfigMap does NOT update env vars in running pods. You must restart the pods.

**Volume mounts do update** — Kubernetes's kubelet periodically syncs the mounted volume from the latest ConfigMap. It takes ~60–90 seconds.

> **Analogy for volume hot-reload:**  
> Think of the volume as a **projector screen** that shows what's in the ConfigMap.  
> When the ConfigMap changes, the projector eventually updates the screen.  
> But env vars are like **photocopies** — they're made once when the pod starts and don't change even when the original changes.

**Best practice for updating env-var based configs:**
```bash
# Trigger a rolling restart of the deployment (zero-downtime)
kubectl rollout restart deployment/my-app
```

---

## 🔍 Inspecting ConfigMaps

```bash
# List all configmaps
kubectl get configmaps
kubectl get cm            # shorthand

# View the data
kubectl describe configmap app-config      # Human readable
kubectl get configmap app-config -o yaml   # Full YAML with all keys
kubectl get configmap app-config -o jsonpath='{.data.LOG_LEVEL}'  # Specific key
```

---

## ⚠️ ConfigMap Limitations and Gotchas

### Gotcha 1: Size Limit

ConfigMaps have a **1MB size limit**. Don't try to store large files (like ML model weights or big JSON datasets) in a ConfigMap.

### Gotcha 2: Pod Must Restart for Env Var Changes

```bash
# You updated a ConfigMap. Pods with env var injection don't see it.
kubectl rollout restart deployment/my-app  # This is the fix
```

### Gotcha 3: Missing ConfigMap = Pending Pod

If your pod references a ConfigMap that doesn't exist, the pod will be stuck in `Pending` or `ContainerCreating`:

```bash
# Symptom: pod stuck in ContainerCreating
kubectl describe pod my-pod
# Events:
# Warning  Failed  ... Error: configmap "app-config" not found
```

Always create ConfigMaps BEFORE the pods that reference them.

### Gotcha 4: Optional vs Required

By default, if the ConfigMap or key doesn't exist, the pod fails to start. You can mark it optional:

```yaml
env:
- name: OPTIONAL_SETTING
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: OPTIONAL_KEY
      optional: true          # Pod starts even if CM or key doesn't exist
```

### Gotcha 5: Keys Must Be Valid in `data`

Keys in `data` can contain letters, numbers, `-`, `_`, and `.`. They cannot contain `=` or spaces.

---

## 📊 Comparison: Three Injection Mechanisms

| | `env.valueFrom` | `envFrom` | Volume Mount |
|-|-----------------|-----------|-------------|
| **Granularity** | One key at a time | All keys at once | All keys as files (or selective) |
| **Env var name** | Custom (`name:`) | Same as CM key | N/A — files, not vars |
| **Updates** | No (need restart) | No (need restart) | Yes (~60-90s delay) |
| **Best for** | A few specific vars | Many env vars | File-based config (nginx, yaml) |
| **YAML verbosity** | High | Low | Medium |

---

## 🧪 Test Yourself

1. **Your app expects `DATABASE_URL` as an environment variable. The ConfigMap has a key called `database-url` (with a hyphen). You try `envFrom`. Does the env var appear in the container?** Why?: hyphens are illegal and not valid, it will be silently skipped

2. **You update a ConfigMap that's mounted as a volume. How long before the running pod sees the change?** What about a ConfigMap injected as env vars? it needs a pod update(60-120 seconds), configmap injection take  a pod restart as they are baked in at pod start

3. **You have 20 config keys. Should you use `env.valueFrom` (20 separate entries) or `envFrom`?** What's the tradeoff? You should use envFrom as it is less verbose and more efficient

4. **Your nginx pod can't start. `kubectl describe pod` shows `configmap "nginx-conf" not found`. What caused this and what's the fix?**config map should be created and ensure that the names match properly

5. **Why should you store ConfigMap YAML files in Git rather than using `kubectl create configmap --from-literal`?**  You should use yaml files in git to keep track of changes and version control

6. **A config file you're mounting via volume has sensitive info — database passwords, API keys. Is ConfigMap appropriate here?** What should you use instead? use secrets

7. **You updated your ConfigMap with a new `LOG_LEVEL`. You can see the change with `kubectl describe configmap`. But the app still logs at the old level. Why? What do you do?**the changes are not propagated to the running pods, use rollout restart to update the pods
