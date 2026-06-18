# Homework P1-4 — Namespace Isolation Lab

> **Time:** 1 hour  
> **Goal:** Set up a realistic dev/prod namespace split, prove what namespaces do and don't isolate, and apply resource quotas.

---

## 🚀 Setup

```powershell
# Create both namespaces
kubectl create namespace dev
kubectl create namespace prod
```

---

## Part 1 — Deploy the Same App in Both Namespaces (20 min)

### Task 1.1 — Deploy Identically Named Resources

The power of namespaces: the same name can exist in both!

```powershell
# Deploy "web-app" in dev
kubectl create deployment web-app --image=nginx:1.25 --replicas=2 -n dev
kubectl expose deployment web-app --port=80 --target-port=80 -n dev

# Deploy "web-app" in prod (same name, different namespace)
kubectl create deployment web-app --image=nginx:1.25 --replicas=3 -n prod
kubectl expose deployment web-app --port=80 --target-port=80 -n prod

# They're completely separate!
kubectl get all -n dev
kubectl get all -n prod
```

**Fill in:**

| Namespace | Deployment Replicas | Service ClusterIP |
|-----------|--------------------|--------------------|
| dev | | |
| prod | | |

Are the ClusterIPs different? Yes — they are completely separate virtual IPs.

---

### Task 1.2 — Prove They're Separate (Even With the Same Name)

```powershell
# Test: can dev's web-app be reached using just "web-app"?
kubectl run test --image=curlimages/curl --restart=Never -it --rm -n dev \
  -- curl http://web-app

# Test: does "web-app" in prod namespace mean a different thing?
kubectl run test --image=curlimages/curl --restart=Never -it --rm -n prod \
  -- curl http://web-app

# Both work! But they reach DIFFERENT pods.
```

---

## Part 2 — Namespace Naming Scope (15 min)

### Task 2.1 — Prove Names Must Be Unique Per Namespace

```powershell
# This works:
kubectl create configmap app-config --from-literal=env=dev -n dev
kubectl create configmap app-config --from-literal=env=prod -n prod

# Same name, different namespace — no conflict!
kubectl get configmaps -n dev
kubectl get configmaps -n prod
```

```powershell
# This FAILS — name already exists in the namespace:
kubectl create configmap app-config --from-literal=env=dev2 -n dev
# Error: configmaps "app-config" already exists
```

---

## Part 3 — Resource Quotas (30 min)

### Task 3.1 — Apply a ResourceQuota to dev

```yaml
# Save as: lab-files/dev-quota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    count/pods: "5"
    requests.cpu: "500m"
    requests.memory: "512Mi"
    limits.cpu: "1"
    limits.memory: "1Gi"
```

```powershell
kubectl apply -f lab-files/dev-quota.yaml

# Check current quota usage
kubectl describe resourcequota dev-quota -n dev
```

### Task 3.2 — Hit the Quota

```powershell
# dev has 2 pods currently. Try to scale up to 10 (past the quota of 5)
kubectl scale deployment web-app --replicas=10 -n dev

# Check what happened
kubectl get pods -n dev
kubectl describe deployment web-app -n dev | grep -A5 Conditions
kubectl get events -n dev --sort-by='.lastTimestamp'
```

**What do you see?** The deployment will scale only to 5 — the quota allows 5 pods. The 6th pod will be rejected with a quota error.

```powershell
# Read the quota usage
kubectl describe resourcequota dev-quota -n dev
```

### Task 3.3 — Observe the Quota in Action

```powershell
# Scale back to 2
kubectl scale deployment web-app --replicas=2 -n dev

# Now try adding pods MANUALLY that would exceed the quota
kubectl run extra1 --image=nginx:1.25 -n dev
kubectl run extra2 --image=nginx:1.25 -n dev
kubectl run extra3 --image=nginx:1.25 -n dev
kubectl run extra4 --image=nginx:1.25 -n dev   # 2 + 4 = 6, OVER QUOTA!

# Check what happened
kubectl get pods -n dev
kubectl get events -n dev --sort-by='.lastTimestamp' | tail -5
```

---

## Part 4 — Cross-Namespace Network (No Isolation by Default!)

### Task 4.1 — Prove Default Cross-Namespace Networking

```powershell
# From dev namespace, reach prod's web-app service
kubectl run cross-test --image=curlimages/curl --restart=Never -it --rm -n dev \
  -- curl http://web-app.prod.svc.cluster.local

# This WORKS! Namespaces do NOT provide network isolation by default.
# (Network isolation requires NetworkPolicy — Phase 3!)
```

**Key point to remember:** If you see this work, write it in your notes:  
_"Namespaces are NOT a network security boundary without NetworkPolicy."_

---

## 🧹 Cleanup

```powershell
kubectl delete namespace dev
kubectl delete namespace prod
kubectl config set-context --current --namespace=default
```

---

## ✅ Done When:

- [ ] Same app deployed in both `dev` and `prod` with same name
- [ ] Proven same name in different namespaces doesn't conflict
- [ ] ResourceQuota applied and pod limit enforced
- [ ] Witnessed quota rejection event
- [ ] Proven cross-namespace networking works without NetworkPolicy

---

## 📝 Reflection

**What can namespaces NOT do on their own?**
```

```

**What would you add to namespaces to make them truly isolated?**
```

```

**When would you use ResourceQuotas in a real org?**
```

```
