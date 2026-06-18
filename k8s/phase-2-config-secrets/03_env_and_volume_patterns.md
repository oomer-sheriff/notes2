# 03 — Environment & Volume Injection Patterns

> **This file is a consolidation guide.** You've now seen ConfigMaps and Secrets separately. This file maps out ALL the ways configuration gets into a running container, when each pattern makes sense, and the advanced tricks you'll need for real workloads.

---

## 🗺️ The Configuration Injection Map

Every piece of configuration that reaches a running container comes through one of these paths:

```
                    CONFIGURATION SOURCES
                           │
          ┌────────────────┼────────────────────┐
          │                │                    │
     ConfigMap          Secret            Direct (pod spec)
          │                │                    │
          └────────────────┤                    │
                           │                    │
                    INJECTION METHODS           │
                           │                    │
          ┌────────────────┼─────────────┐      │
          │                │             │      │
    env (specific   envFrom (all)   Volume      │
    keys)                │          Mount       │
          │              │             │        │
          └──────────────┴─────────────┴────────┘
                                │
                        INSIDE THE CONTAINER
                    env vars  /  files on disk
```

---

## 📌 Pattern 1: Direct `env` in Pod Spec

For config that doesn't belong in a ConfigMap or Secret — or for values derived from the pod itself.

### Literal Value

```yaml
containers:
- name: app
  env:
  - name: APP_MODE
    value: "production"
  - name: REPLICA_ID
    value: "1"
```

### Downward API — Inject Pod's Own Metadata

The **Downward API** lets you inject information about the pod itself as environment variables. The pod doesn't need to call the API server — K8s injects the info at startup.

```yaml
containers:
- name: app
  env:
  - name: MY_POD_NAME           # Pod name
    valueFrom:
      fieldRef:
        fieldPath: metadata.name

  - name: MY_NAMESPACE          # Namespace
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace

  - name: MY_POD_IP             # Pod IP
    valueFrom:
      fieldRef:
        fieldPath: status.podIP

  - name: MY_NODE_NAME          # Node the pod is running on
    valueFrom:
      fieldRef:
        fieldPath: spec.nodeName

  - name: MY_CPU_REQUEST        # From resource requests
    valueFrom:
      resourceFieldRef:
        containerName: app
        resource: requests.cpu

  - name: MY_MEM_LIMIT
    valueFrom:
      resourceFieldRef:
        containerName: app
        resource: limits.memory
```

**Why Downward API is useful:**
- Logging/tracing: tag every log line with the pod name and node
- Distributed coordination: each pod knows its own identity
- Metrics: instrument with pod-level labels

Inside the container:
```bash
echo $MY_POD_NAME      # web-app-abc123-xyz789
echo $MY_NODE_NAME     # k8s-multinode-worker
echo $MY_NAMESPACE     # production
```

---

## 📌 Pattern 2: `envFrom` — Whole ConfigMap/Secret as Env Vars

Best when you have many config values and want them all in one go.

```yaml
containers:
- name: app
  envFrom:
  - configMapRef:
      name: app-config
  - configMapRef:
      name: feature-flags        # Multiple CMs! Stack them.
  - secretRef:
      name: db-credentials
  - configMapRef:
      name: optional-extras
      optional: true             # Don't fail if this CM doesn't exist
```

**The env var merge order matters!** If two sources define the same key, the LAST one wins:

```
app-config:      LOG_LEVEL=info
feature-flags:   LOG_LEVEL=debug   ← This wins (defined later in envFrom list)
```

---

## 📌 Pattern 3: Volume Mount — Config as Files

The most powerful and flexible mechanism. Use it for:
- App configs that are read from files (nginx, Prometheus, Spring Boot, etc.)
- SSH keys, TLS certificates
- Config that needs automatic hot-reload

### Full ConfigMap as a Directory

```yaml
spec:
  containers:
  - name: nginx
    volumeMounts:
    - name: nginx-conf
      mountPath: /etc/nginx/conf.d      # Each CM key = one file here

  volumes:
  - name: nginx-conf
    configMap:
      name: nginx-config
```

Result:
```bash
ls /etc/nginx/conf.d/
# default.conf    upstream.conf    gzip.conf
# (one file per key in the ConfigMap)
```

### Selective Key Mount (Most Useful!)

```yaml
volumes:
- name: nginx-conf
  configMap:
    name: nginx-config
    items:
    - key: default.conf           # Use only THIS key
      path: site.conf             # Name it THIS in the volume
      mode: 0644                  # Optional: specific file permission
```

### Mix ConfigMap and Secret in the Same Volume Path

You can't merge multiple sources into one volume directory directly, but you can use `subPath` to mount individual files into existing directories:

```yaml
containers:
- name: app
  volumeMounts:
  - name: config-vol
    mountPath: /app/config/app.yaml    # Mount a single file
    subPath: app.yaml                  # Specifically this key from the CM
  - name: secrets-vol
    mountPath: /app/config/secrets.yaml
    subPath: secrets.yaml

volumes:
- name: config-vol
  configMap:
    name: app-config
- name: secrets-vol
  secret:
    secretName: app-secrets
```

> ⚠️ **`subPath` gotcha:** When using `subPath`, the volume does NOT hot-reload automatically. You lose the auto-update behaviour of regular volume mounts.

---

## 📌 Pattern 4: Projected Volumes — Multiple Sources, One Mount Point

A **projected volume** combines multiple sources (ConfigMaps, Secrets, Downward API) into a **single directory**. This solves the "I need config and secrets in the same directory" problem.

```yaml
spec:
  containers:
  - name: app
    volumeMounts:
    - name: all-config
      mountPath: /etc/app-config

  volumes:
  - name: all-config
    projected:
      sources:
      - configMap:
          name: app-config            # CM keys become files
      - secret:
          name: app-secrets           # Secret keys become files
          items:
          - key: password
            path: db-password         # specific key at specific path
      - downwardAPI:                  # Pod metadata as a file
          items:
          - path: pod-name
            fieldRef:
              fieldPath: metadata.name
```

Result inside container:
```bash
ls /etc/app-config/
# LOG_LEVEL       ← from ConfigMap
# DATABASE_HOST   ← from ConfigMap
# db-password     ← from Secret
# pod-name        ← from Downward API
```

---

## 🔢 Pattern Summary — Which to Use When?

```
Is the value SENSITIVE (password, key, token)?
├── YES → Use Secret
│         ├── Single value needed → secretKeyRef in env
│         ├── Multiple values → secretRef in envFrom
│         └── File-based (cert, key) → Secret volume mount
│
└── NO → Use ConfigMap
          ├── Simple value → configMapKeyRef in env
          ├── Many values → configMapRef in envFrom  
          ├── Config file (nginx.conf, etc.) → ConfigMap volume mount
          └── Self-referential (pod name, IP) → Downward API
```

---

## 🔄 Configuration Update Behaviour — The Full Matrix

| Source | Mechanism | Pod restarts required? | Update delay |
|--------|-----------|----------------------|-------------|
| ConfigMap | `env.valueFrom` | YES | — |
| ConfigMap | `envFrom` | YES | — |
| ConfigMap | Volume mount | NO | ~60-90 seconds |
| Secret | `env.valueFrom` | YES | — |
| Secret | `envFrom` | YES | — |
| Secret | Volume mount | NO | ~60-90 seconds |
| Downward API | `env.valueFrom` | YES | — |
| Downward API | Volume mount | NO | ~60-90 seconds |

**Triggering a rolling restart (when env vars change):**
```bash
kubectl rollout restart deployment/my-app
```

This performs a zero-downtime rolling restart — each pod is replaced one at a time (respecting your `maxUnavailable` / `maxSurge` strategy). New pods pick up the updated ConfigMap/Secret values.

---

## 🧪 Test Yourself

1. **Your app needs to know which Kubernetes node it's running on (for metrics tagging). How do you get this value into the container without calling the API server?**

2. **You need nginx, a Prometheus metrics scraper, and a CA certificate all available in `/etc/config`. You have: `nginx.conf` in a ConfigMap, `ca.crt` in a Secret, and you want the pod name in a file. What volume type solves this in a single mount point?**

3. **Two ConfigMaps both define `LOG_LEVEL`. You reference both via `envFrom`. Which value does the container see?**

4. **You're using `subPath` to mount a single file. The underlying ConfigMap gets updated. Does the file in the container update automatically?** What does — and what does `subPath` break?

5. **Give two scenarios where the Downward API is genuinely useful in production applications.**

6. **You want your app to hot-reload its config without a pod restart when the ConfigMap changes. What injection mechanism do you choose and what constraint does the app need to meet?**
