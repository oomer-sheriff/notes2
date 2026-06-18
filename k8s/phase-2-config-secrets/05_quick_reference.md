# ☸️ Phase 2 — Quick Reference Cheat Sheet

---

## ConfigMaps

```bash
# Create
kubectl create configmap my-cm --from-literal=KEY=VALUE
kubectl create configmap my-cm --from-file=config.properties
kubectl create configmap my-cm --from-file=./config-dir/
kubectl apply -f configmap.yaml

# Inspect
kubectl get configmaps
kubectl get cm                                      # Short
kubectl describe cm my-cm                           # Human readable
kubectl get cm my-cm -o yaml                        # Full YAML
kubectl get cm my-cm -o jsonpath='{.data.KEY}'      # Single key value

# Update
kubectl edit cm my-cm                               # Interactive
kubectl patch cm my-cm --type=merge -p '{"data":{"KEY":"newvalue"}}'

# Delete
kubectl delete cm my-cm
```

---

## Secrets

```bash
# Create
kubectl create secret generic my-secret --from-literal=password=abc123
kubectl create secret generic my-secret --from-file=./credentials.json
kubectl create secret docker-registry regcred \
  --docker-server=ghcr.io \
  --docker-username=user \
  --docker-password=token
kubectl create secret tls tls-secret --cert=server.crt --key=server.key

# Inspect (values masked in describe!)
kubectl get secrets
kubectl get secret my-secret -o yaml                # Raw (values are base64)
kubectl describe secret my-secret                   # Masked — shows size only

# Decode a secret value
kubectl get secret my-secret -o jsonpath='{.data.password}' | \
  ForEach-Object { [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($_)) }

# Delete
kubectl delete secret my-secret
```

---

## Injection in Pod Spec — All Patterns

```yaml
# SINGLE ENV VAR FROM CONFIGMAP
env:
- name: MY_LOG_LEVEL
  valueFrom:
    configMapKeyRef:
      name: app-config
      key: LOG_LEVEL
      optional: false

# SINGLE ENV VAR FROM SECRET
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-creds
      key: password

# ALL CONFIGMAP KEYS AS ENV VARS
envFrom:
- configMapRef:
    name: app-config

# ALL SECRET KEYS AS ENV VARS
envFrom:
- secretRef:
    name: db-creds

# MIXED envFrom (order matters for conflicts — last wins)
envFrom:
- configMapRef:
    name: app-config
- configMapRef:
    name: feature-flags
- secretRef:
    name: db-creds

# DOWNWARD API — pod's own metadata
env:
- name: MY_POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: MY_NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace
- name: MY_NODE
  valueFrom:
    fieldRef:
      fieldPath: spec.nodeName
- name: MY_POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
- name: MY_CPU_REQUEST
  valueFrom:
    resourceFieldRef:
      containerName: my-container
      resource: requests.cpu

# CONFIGMAP AS VOLUME (all keys become files)
volumeMounts:
- name: config-vol
  mountPath: /etc/myapp/config
  readOnly: true
volumes:
- name: config-vol
  configMap:
    name: app-config

# SECRET AS VOLUME (all keys become files in tmpfs)
volumeMounts:
- name: secret-vol
  mountPath: /etc/myapp/secrets
  readOnly: true
volumes:
- name: secret-vol
  secret:
    secretName: db-creds
    defaultMode: 0400     # r-------- permission

# SELECTIVE KEY MOUNT (single key → single file)
volumes:
- name: nginx-conf
  configMap:
    name: nginx-config
    items:
    - key: default.conf
      path: site.conf     # custom filename

# PROJECTED VOLUME (multiple sources → single directory)
volumes:
- name: all-config
  projected:
    sources:
    - configMap:
        name: app-config
    - secret:
        name: db-creds
    - downwardAPI:
        items:
        - path: pod-name
          fieldRef:
            fieldPath: metadata.name
```

---

## Update Behaviour

| Mechanism | Needs Pod Restart? | How to Force Update |
|-----------|-------------------|-------------------|
| `env.valueFrom` (CM or Secret) | YES | `kubectl rollout restart deployment/myapp` |
| `envFrom` (CM or Secret) | YES | `kubectl rollout restart deployment/myapp` |
| Volume mount (CM or Secret) | NO | Auto-updates in ~60-90s |
| `subPath` volume mount | YES | Breaks auto-update! |

---

## Resources

```yaml
resources:
  requests:
    memory: "128Mi"    # Scheduler reservation (what you typically use)
    cpu: "250m"        # 1000m = 1 full core
  limits:
    memory: "256Mi"    # OOMKilled if exceeded
    cpu: "500m"        # Throttled if exceeded (NOT killed)
```

```bash
# Observe actual usage
kubectl top pods
kubectl top pods --containers    # Per-container breakdown
kubectl top nodes
kubectl top pods --sort-by=memory
kubectl top pods --sort-by=cpu
```

---

## QoS Classes

| Class | How to Achieve | Eviction Order |
|-------|---------------|---------------|
| `Guaranteed` | ALL containers: requests == limits (both CPU and memory) | Last |
| `Burstable` | At least one container: requests < limits OR only requests OR only limits | Middle |
| `BestEffort` | NO containers have any resource settings | First |

```bash
# Check a pod's QoS class
kubectl get pod my-pod -o jsonpath='{.status.qosClass}'
```

---

## Secret Types

| Type | kubectl shortcut | Use Case |
|------|-----------------|---------|
| `Opaque` | `secret generic` | Any custom secret |
| `kubernetes.io/dockerconfigjson` | `secret docker-registry` | Image pull auth |
| `kubernetes.io/tls` | `secret tls` | TLS cert + key |

---

## Key Rules to Remember

```
1. base64 ≠ encryption. kubectl get secret -o yaml → decode instantly.

2. Env vars are baked at pod start. CM/Secret change? Restart the pod.
   kubectl rollout restart deployment/myapp

3. Volume mounts auto-update (except subPath). Takes ~60-90s.

4. Secret volumes use tmpfs (RAM). Never written to node disk.

5. requests = scheduler sees. limits = enforcement. 
   CPU over limit = throttled. Memory over limit = OOMKilled.

6. QoS class is auto-assigned. requests == limits = Guaranteed.

7. Always set readOnly: true on secret volume mounts.

8. Always check kubectl get endpoints if service isn't routing traffic.
```
