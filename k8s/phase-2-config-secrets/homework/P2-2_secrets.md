# Homework P2-2 — Secrets: Security Lab

> **Time:** 1.5 hours  
> **Goal:** Create secrets, prove base64 is not encryption, compare env vs volume injection security, and see what masking actually does (and doesn't) protect.

---

## 🚀 Setup

```powershell
kubectl create namespace lab-sec
kubectl config set-context --current --namespace=lab-sec
```

---

## Part 1 — Create and Decode Secrets (20 min)

### Task 1.1 — Create a Secret and Expose the Reality

```powershell
# Create a secret with a "sensitive" value
kubectl create secret generic db-creds \
  --from-literal=username=admin \
  --from-literal=password=MySuperSecret123 \
  --from-literal=api-key=sk-prod-abc123xyz \
  -n lab-sec

# Now prove it's not encrypted — get the raw YAML
kubectl get secret db-creds -n lab-sec -o yaml
```

**Write down the base64-encoded password value here:**
```
password: ___________________
```

Now decode it in PowerShell:
```powershell
# Decode the password (replace with your actual base64 value)
[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("YOUR_BASE64_HERE"))

# Or use WSL/bash:
echo "YOUR_BASE64_HERE" | base64 --decode
```

**Result:** You got the plain text password. This is why K8s Secrets are "security by obscurity, not encryption."

---

### Task 1.2 — What `describe` Hides (and What It Doesn't)

```powershell
# describe masks the values — only shows size in bytes
kubectl describe secret db-creds -n lab-sec

# But get -o yaml bypasses masking
kubectl get secret db-creds -n lab-sec -o yaml

# And jsonpath is even faster for extraction:
kubectl get secret db-creds -n lab-sec -o jsonpath='{.data.password}' | \
  ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
```

**Fill in:**

| Question | Answer |
|----------|--------|
| What does `describe` show for the password? | |
| What does `get -o yaml` show? | |
| Is the data in `describe` safe to share in a screenshot? | |
| Is the data in `get -o yaml` safe to share? | |

---

## Part 2 — Secret Injection: Env Var vs Volume (40 min)

### Task 2.1 — Secret as Environment Variable (Less Secure)

```yaml
# Save as lab-files/secret-env-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-env-demo
  namespace: lab-sec
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'sleep 3600']
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: password
    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: db-creds
          key: api-key
    resources:
      requests:
        memory: "32Mi"
        cpu: "50m"
      limits:
        memory: "64Mi"
        cpu: "100m"
```

```powershell
kubectl apply -f lab-files/secret-env-pod.yaml
kubectl exec secret-env-demo -n lab-sec -- env | grep -E "DB_|API_"
```

**The security exposure:** An env variable can be read by ANYONE inside the container, any process, and is visible in `/proc/<pid>/environ` on the host node.

```powershell
# Simulate accidental logging (the #1 secret leak in production)
kubectl exec secret-env-demo -n lab-sec -- sh -c 'echo "DEBUG: env dump = $(env)"'
# See how all secrets are leaked in a single debug line?
```

---

### Task 2.2 — Secret as Volume Mount (More Secure)

```yaml
# Save as lab-files/secret-vol-pod.yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-vol-demo
  namespace: lab-sec
spec:
  containers:
  - name: app
    image: busybox:1.35
    command: ['sh', '-c', 'sleep 3600']
    volumeMounts:
    - name: secrets
      mountPath: /etc/app-secrets
      readOnly: true
    resources:
      requests:
        memory: "32Mi"
        cpu: "50m"
      limits:
        memory: "64Mi"
        cpu: "100m"

  volumes:
  - name: secrets
    secret:
      secretName: db-creds
      defaultMode: 0400         # r-------- only owner can read
```

```powershell
kubectl apply -f lab-files/secret-vol-pod.yaml

# Inspect the mounted files
kubectl exec secret-vol-demo -n lab-sec -- ls -la /etc/app-secrets/
kubectl exec secret-vol-demo -n lab-sec -- cat /etc/app-secrets/password

# Check file permissions
kubectl exec secret-vol-demo -n lab-sec -- stat /etc/app-secrets/password
```

**Fill in:**

| Question | Answer |
|----------|--------|
| What files are in `/etc/app-secrets/`? | |
| What permissions do the files have? | | readonly
| Can the accidental `echo "$(env)"` leak these secrets? | | only owner can read if we set default mode to the secret mount yaml

---

### Task 2.3 — Verify tmpfs (In-Memory Storage)

Secret volumes are mounted as **tmpfs** — they live only in RAM, never written to disk.

```powershell
kubectl exec secret-vol-demo -n lab-sec -- mount | grep "app-secrets"
# Should show: tmpfs on /etc/app-secrets type tmpfs

# Compare to a regular volume (emptyDir):
# Regular volumes might be on disk: /var/lib/kubelet/pods/.../volumes/
# Secret volumes are in tmpfs: in RAM only
```

---

## Part 3 — Docker Registry Secret (15 min)

### Task 3.1 — Create an imagePullSecret

```powershell
# Create a fake registry secret (we won't actually pull from a private registry)
kubectl create secret docker-registry fake-registry-creds \
  --docker-server=ghcr.io \
  --docker-username=myuser \
  --docker-password=ghp_faketoken123 \
  --docker-email=me@example.com \
  -n lab-sec

# Inspect it — notice the type
kubectl get secret fake-registry-creds -n lab-sec -o yaml
```

**What type is this secret?**  
What key does it contain?

```powershell
# Decode the .dockerconfigjson to see what's inside
kubectl get secret fake-registry-creds -n lab-sec \
  -o jsonpath='{.data.\.dockerconfigjson}' | \
  ForEach-Object { [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($_)) }
```

**What does the decoded content look like?** (It's JSON with server, username, and auth)

---

## Part 4 — The `stringData` Round-Trip (10 min)

```powershell
# Apply a secret using stringData (human-readable values)
kubectl apply -f - @"
apiVersion: v1
kind: Secret
metadata:
  name: string-data-demo
  namespace: lab-sec
type: Opaque
stringData:
  plain-password: "my-readable-password"
  config.yaml: |
    database:
      host: postgres
      password: my-readable-password
"@

# Now read it back — it will come back as base64 in 'data', not 'stringData'
kubectl get secret string-data-demo -n lab-sec -o yaml
```

**Observation:** You wrote `stringData` with plain text. K8s stored it as `data` with base64. The `stringData` field disappears in the output — it's write-only.

---

## 🧹 Cleanup

```powershell
kubectl delete namespace lab-sec
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] Base64 decoded a secret value — proved it's not encrypted
- [ ] `describe` vs `get -o yaml` comparison table completed
- [ ] Env var injection: witnessed secrets visible in `env` output
- [ ] Volume mount: secret files created with `0400` permissions and `tmpfs` mount
- [ ] Docker registry secret created and decoded
- [ ] `stringData` round-trip completed

## 📝 Reflection

**What is the most significant security risk with K8s Secrets as env vars?**
```

```

**If a developer wants to store a production database password, what would you recommend in a real company? (Don't say "K8s Secret" alone — think about the full solution.)**
```

```
