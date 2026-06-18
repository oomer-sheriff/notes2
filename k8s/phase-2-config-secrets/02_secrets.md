# 02 — Secrets: Handling Sensitive Data

> **Critical mindset shift:** K8s Secrets are NOT encrypted by default. The name is misleading. Understanding what they actually are — and their real security properties — is essential before you put anything sensitive in them.

---

## 🔐 What Is a Secret?

A Secret is a Kubernetes object designed to store sensitive information like passwords, API tokens, and TLS certificates.

Structurally, it's almost identical to a ConfigMap — but with one key difference:

```yaml
# ConfigMap — values stored as plain text
apiVersion: v1
kind: ConfigMap
data:
  LOG_LEVEL: "info"               ← plain text

# Secret — values stored as base64
apiVersion: v1
kind: Secret
data:
  PASSWORD: "c3VwZXJzZWNyZXQxMjM="  ← base64("supersecret123")
```

**base64 is encoding, NOT encryption.** Anyone can decode it in one command:
```bash
echo "c3VwZXJzZWNyZXQxMjM=" | base64 --decode
# Output: supersecret123
```

> **Analogy:** base64 is like writing a secret message by flipping every letter in the alphabet (A→Z, B→Y...). It looks scrambled, but anyone who knows the trick can read it instantly. It's obfuscation, not security.

---

## 🚨 The Honest Security Reality of K8s Secrets

Before you use K8s Secrets, you need to understand what they actually protect against — and what they don't.

```
What K8s Secrets DO:
  ✅ Keep secret values out of your YAML/source code
  ✅ Restrict who can LIST/GET secrets via RBAC
  ✅ Don't show values in `kubectl describe` (masked)
  ✅ Available as tmpfs (in-memory) mounts — never written to node disk
  ✅ Can be encrypted at rest in etcd (if configured with a KMS provider)

What K8s Secrets DON'T do (by default):
  ❌ Encrypt the data in etcd (stored as base64 plain text by default!)
  ❌ Prevent cluster-admins from reading all secrets
  ❌ Audit who accessed which secret
  ❌ Automatically rotate secrets
  ❌ Prevent secrets from appearing in pod logs if the app prints them
```

**The threat model:**

```
Who can see your secrets?

Anyone with:
  kubectl get secret my-secret -o yaml        → can see base64 → decode instantly
  kubectl exec -it pod -- env                 → can see ALL env vars
  Access to the etcd backup file              → has ALL secrets in plaintext (if no KMS!)
  Node-level access                           → may access secrets via /proc

Who is blocked:
  Devs without RBAC "get" on Secrets         → can't list or read secrets (RBAC helps!)
  External attackers without cluster access  → can't reach etcd
```

> **Analogy:** K8s Secrets are like a **locked glass cabinet**.  
> The lock (RBAC) stops most people from opening it.  
> But anyone who CAN open it can see everything clearly through the glass (base64 = transparent).  
> A bank vault (encrypted at rest + KMS) is what you actually want for real secrets in production.

---

## 🏷️ Secret Types

K8s has multiple secret types for different use cases. The `type` field tells K8s how to validate and use it.

| Type | Use Case | Key Names |
|------|---------|-----------|
| `Opaque` | Generic secrets (passwords, API keys) | Any keys you want |
| `kubernetes.io/dockerconfigjson` | Private registry pull credentials | `.dockerconfigjson` |
| `kubernetes.io/tls` | TLS certificate + key | `tls.crt`, `tls.key` |
| `kubernetes.io/service-account-token` | SA token (auto-created) | `token`, `ca.crt`, `namespace` |
| `kubernetes.io/basic-auth` | Username/password | `username`, `password` |
| `kubernetes.io/ssh-auth` | SSH private key | `ssh-privatekey` |

---

## 🏗️ Creating Secrets — All Methods

### Opaque Secret (Generic)

**Method 1: From literals (recommended for quick tests)**
```bash
kubectl create secret generic db-secret \
  --from-literal=username=admin \
  --from-literal=password=supersecret123 \
  --from-literal=api-key=sk-abc123xyz
```

**Method 2: From a file (good for certs, keys)**
```bash
kubectl create secret generic tls-cert \
  --from-file=tls.crt=./server.crt \
  --from-file=tls.key=./server.key
```

**Method 3: YAML with `stringData` (human-readable values, K8s encodes for you)**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
  namespace: production
type: Opaque
stringData:                   # ← Write plain text here
  username: "admin"
  password: "supersecret123"  # K8s base64-encodes this automatically when stored
  connection-string: "postgresql://admin:supersecret123@postgres:5432/mydb"
```

**Method 4: YAML with `data` (pre-encoded base64)**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
data:                              # ← Must be base64-encoded manually
  username: YWRtaW4=               # base64("admin")
  password: c3VwZXJzZWNyZXQxMjM=  # base64("supersecret123")
```

> 💡 **Use `stringData` in your YAML files, not `data`.** It's more readable and K8s handles the encoding. The downside: the encoded form is what gets stored (and shown when you `get -o yaml`).

---

### Docker Registry Secret

```bash
kubectl create secret docker-registry registry-creds \
  --docker-server=ghcr.io \
  --docker-username=myusername \
  --docker-password=ghp_mytoken \
  --docker-email=me@example.com
```

Then use it in a pod so Kubernetes can pull private images:

```yaml
spec:
  imagePullSecrets:
  - name: registry-creds    # K8s uses this when pulling images for this pod
  containers:
  - name: my-app
    image: ghcr.io/myorg/my-private-app:latest
```

---

### TLS Secret

```bash
# Generate a self-signed cert (for testing)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key -out server.crt \
  -subj "/CN=myapp.example.com"

# Create the TLS secret
kubectl create secret tls my-tls-secret \
  --cert=server.crt \
  --key=server.key
```

TLS secrets are used by Ingress resources for HTTPS termination (Phase 3).

---

## 💉 Injecting Secrets — Same Mechanisms as ConfigMaps

The injection methods are identical to ConfigMaps. Same YAML structure, just replace `configMapKeyRef` with `secretKeyRef`.

### As Environment Variables

```yaml
spec:
  containers:
  - name: my-app
    image: my-app:latest
    env:
    - name: DB_PASSWORD           # Env var name in container
      valueFrom:
        secretKeyRef:
          name: db-secret         # Secret name
          key: password           # Key within the secret
          optional: false         # (default) Pod fails if secret/key not found

    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: db-secret
          key: api-key
```

### All Keys at Once (`envFrom`)

```yaml
    envFrom:
    - secretRef:
        name: db-secret           # ALL keys become env vars
```

### As a Volume (Files)

```yaml
spec:
  containers:
  - name: my-app
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secrets     # Directory of secret files
      readOnly: true              # Always set readOnly: true for secrets!

  volumes:
  - name: secret-volume
    secret:
      secretName: db-secret
      defaultMode: 0400           # File permissions: owner read-only
```

Inside the container:
```bash
ls /etc/secrets/
# password    api-key    username    connection-string

cat /etc/secrets/password
# supersecret123

# File permissions are 0400 (readable only by owner):
ls -la /etc/secrets/
# -r-------- ... password
```

> 💡 **Volume-mounted secrets** are more secure than env vars because:
> - Env vars can be accidentally logged by the app (`env` command, debug prints)
> - Volumes support **automatic rotation** — if the Secret is updated, the mounted files update after ~60-90s (same as ConfigMap volumes)
> - Env vars don't update without a pod restart

---

## 🔒 The `stringData` vs `data` Duality

```bash
# You create with stringData:
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
stringData:
  password: "mysecret"
EOF

# When you read it back, it comes as data (encoded):
kubectl get secret my-secret -o yaml
# data:
#   password: bXlzZWNyZXQ=    ← base64 of "mysecret"

# Decode it:
echo "bXlzZWNyZXQ=" | base64 --decode
# mysecret
```

This is the "glass cabinet" in action. Anyone with `kubectl get secret` access can decode it trivially.

---

## 🔍 Inspecting Secrets

```bash
# List secrets
kubectl get secrets
kubectl get secret db-secret

# describe DOES NOT show values (masked!)
kubectl describe secret db-secret
# Output:
# Name:         db-secret
# Type:         Opaque
# Data
# ====
# api-key:   12 bytes     ← Only shows SIZE, not value
# password:  15 bytes
# username:  5 bytes

# Get the actual value (bypasses masking — be careful in terminals that log!)
kubectl get secret db-secret -o yaml
kubectl get secret db-secret -o jsonpath='{.data.password}' | base64 --decode
```

---

## 🏭 Production Secret Management — Beyond K8s Secrets

For true production workloads, K8s Secrets alone are often not sufficient. Here's the hierarchy of approaches:

```
Level 1: K8s Secrets (base64, RBAC only)
  ✅ Simple, built-in
  ❌ Not encrypted at rest by default
  ❌ In your Git history if you're not careful
  Use for: Learning, low-sensitivity non-prod environments

Level 2: K8s Secrets + Encryption at Rest
  ✅ etcd secrets are encrypted using a KMS provider
  ✅ Admins can't read raw etcd and see secrets
  ❌ Still in cluster, still accessible via kubectl to cluster-admins
  Use for: Medium-security production workloads

Level 3: External Secret Managers (Industry Standard)
  ┌──────────────────────────────────────────────┐
  │  HashiCorp Vault / AWS Secrets Manager       │
  │  / GCP Secret Manager / Azure Key Vault      │
  │                                              │
  │  + External Secrets Operator (ESO)           │
  │    Watches K8s Secrets, syncs from Vault     │
  └──────────────────────────────────────────────┘
  ✅ Centralized secret management
  ✅ Audit trail for every secret access
  ✅ Automatic rotation
  ✅ Secrets never stored in etcd unencrypted
  Use for: Any production workload with real sensitive data

Level 4: Sealed Secrets (GitOps-compatible)
  ┌──────────────────────────────────────────────┐
  │  Bitnami Sealed Secrets                      │
  │  Encrypt secrets with a cluster-specific key │
  │  Safe to commit to Git!                      │
  └──────────────────────────────────────────────┘
  ✅ Version control your secrets safely
  ✅ Only the cluster can decrypt them
  Use for: GitOps workflows where secrets go in Git repos
```

> 🎯 **For now:** Learn K8s Secrets deeply (they're required knowledge for CKA/CKAD). In Phase 8 (GitOps), we'll look at Sealed Secrets as part of the production pipeline.

---

## ⚠️ Security Best Practices for Secrets

### DO:
```yaml
# ✅ Mount as volumes, not env vars
volumeMounts:
- name: secret-vol
  mountPath: /etc/secrets
  readOnly: true          # ALWAYS readOnly!

# ✅ Use defaultMode to restrict file permissions
volumes:
- name: secret-vol
  secret:
    secretName: db-creds
    defaultMode: 0400     # Only owner can read

# ✅ Set immutable: true if the secret won't change (performance + accidental change prevention)
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
immutable: true           # Prevents any updates; must delete+recreate to change
data:
  api-key: abc123==
```

### DON'T:
```yaml
# ❌ Never store secrets in your container image
ENV DATABASE_PASSWORD=supersecret123   # In Dockerfile — visible in image layers!

# ❌ Never print secrets in logs
print(f"Connecting to DB with password: {os.environ['DB_PASSWORD']}")

# ❌ Never commit Secret YAML with actual values to Git
# (use stringData placeholders or Sealed Secrets instead)

# ❌ Don't use the same secret in dev and prod
# Create separate secrets per environment
```

---

## 🧪 Test Yourself

1. **Run `echo "c3VwZXJzZWNyZXQ=" | base64 --decode` in your terminal. What does this prove about K8s Secrets?**, secrets are not encrypted by default, just encoded

2. **What is the difference between `stringData` and `data` in a Secret manifest?** Which one should you use in YAML files? Use stringData

3. **You store a database password as an environment variable from a Secret. A developer accidentally adds `print(os.environ)` for debugging. What's the security implication?** What's the better approach?  it will be logged in the console, use volumes instead

4. **You run `kubectl describe secret db-creds`. The output shows `password: 15 bytes` but not the actual value. Does this mean the data is encrypted?** Explain. No, it is just base64 encoded so not encrypted

5. **What three things make a Secrets volume mount more secure than an env var injection?** It can be remounted without restarting the pod , 

6. **Your CI/CD pipeline stores image pull secrets. What Secret type do you use?** What field in the pod spec references it?dockerconfigjson in the imagePullSecrets field in the pod spec

7. **In which scenario would you choose Sealed Secrets over plain K8s Secrets?** sensitive data?, where secrets go into git repos, safe to store there since secrets are encrypted with a cluster-specific key

8. **A team says "we don't need to worry about Secret security because we've set RBAC so only admins can access them." Is this sufficient?** What are they missing? they are wrong, etcd encryption at rest or external secret manager required

so essentially secrets are also config maps, that are encoded by default, and maybe encrypted via kms providers using dek (local) and kek (masterkey), and that is "encryption at rest", which is done by kubernetes control plane which stores the encrypted key inside etcd


config maps also store inside etcd, but arent this encrypted, since they only store non sensitive data

the thing with secrets, is that even if etcd is encrypted, the secret objects are still base64 encoded



