# 02 — Kubernetes Architecture (Deep Dive)

> **Goal of this file:** You should be able to close it and draw the full architecture on paper with every component labeled and explained.

---

## 🏙️ The Big Picture — Two Worlds

A Kubernetes cluster is split into exactly two worlds:

```
╔══════════════════════════════════════════════════════════════════╗
║                         CONTROL PLANE                           ║
║         "The Brain" — makes all the decisions                   ║
║  ┌──────────────┐  ┌──────┐  ┌────────────────┐  ┌──────────┐  ║
║  │  API Server  │  │ etcd │  │   Controller   │  │Scheduler │  ║
║  │              │  │      │  │    Manager     │  │          │  ║
║  └──────────────┘  └──────┘  └────────────────┘  └──────────┘  ║
╚══════════════════════════════════════════════════════════════════╝
         ▲  all communication goes through API Server  ▲
         │                                             │
╔════════╪═════════════════════════════════════════════╪══════════╗
║        │           WORKER NODES                      │          ║
║   "The Body" — actually runs your containers         │          ║
║  ┌─────┴──────────────────────────────────────────┐  │          ║
║  │                Node 1                          │  │          ║
║  │  ┌──────────┐  ┌────────────┐  ┌───────────┐  │  │          ║
║  │  │ kubelet  │  │ kube-proxy │  │ container │  │  │          ║
║  │  │          │  │            │  │  runtime  │  │  │          ║
║  │  └──────────┘  └────────────┘  └───────────┘  │  │          ║
║  │  ┌──────────────────────────────────────────┐  │  │          ║
║  │  │  Pod  │  Pod  │  Pod  │  Pod  │  Pod     │  │  │          ║
║  │  └──────────────────────────────────────────┘  │  │          ║
║  └─────────────────────────────────────────────────┘  │          ║
║  ┌─────────────────────────────────────────────────┐  │          ║
║  │                Node 2                          │  │          ║
║  │           ... same structure ...               │◄─┘          ║
║  └─────────────────────────────────────────────────┘            ║
╚══════════════════════════════════════════════════════════════════╝
```

> **Analogy:** The Control Plane is like a **restaurant head office** — it holds the menu, takes orders, manages staff schedules, tracks inventory.  
> The Worker Nodes are the **actual restaurant kitchens** — they do the real cooking (running containers). The head office never actually makes food.

---

## 🧠 Control Plane Components (One by One)

### 1. API Server (`kube-apiserver`)

**What it is:** The single, central gateway for ALL communication in the cluster.

**What it does:**
- Receives every request (from kubectl, from other K8s components, from your apps)
- Validates the request (is this valid YAML? does the user have permission?)
- Reads/writes to etcd (the database)
- Notifies other components of changes

```
                    YOU
                     │
              kubectl apply -f pod.yaml
                     │
                     ▼
            ┌─────────────────┐
            │   API Server    │◄──── All components talk here
            │                 │      kube-scheduler, controller-manager,
            │  - Validates    │      kubelets on nodes
            │  - Authenticates│
            │  - Authorizes   │
            │  - Stores→etcd  │
            └─────────────────┘
```

> **Analogy:** The API Server is the **front desk receptionist at a hospital**.  
> Every request — whether from a patient, a doctor, or a nurse — goes through the receptionist first. They check your ID (authentication), confirm you have the right form (validation), decide if you're allowed to do what you want (authorization), update the patient record (etcd), and then notify the right department to act on it.  
> **Nothing bypasses the front desk.**

**What happens if it dies?**
- You can't `kubectl` anything — the cluster is "deaf"
- Existing pods keep running (nodes operate independently)
- No new pods can be scheduled until API server recovers
- This is why production clusters run 3+ control plane nodes

---

### 2. etcd

**What it is:** A distributed key-value database. The only place cluster state is stored.

**What it stores:**
- Every object you've ever created (pods, deployments, services...)
- Their current spec and status
- Cluster configuration
- Secrets (encrypted at rest, ideally)

```
etcd is like a filing cabinet:

Key                              Value
─────────────────────────────────────────────────────────
/registry/pods/default/nginx-1   {"spec": {...}, "status": {...}}
/registry/pods/default/nginx-2   {"spec": {...}, "status": {...}}
/registry/deployments/default/web {"spec": {...}, "status": {...}}
/registry/secrets/default/api-key {"data": {...}}
```

> **Analogy:** etcd is the cluster's **long-term memory** — its brain's hippocampus.  
> If the API server is the receptionist, etcd is the **central medical records room**.  
> The receptionist never memorizes anything — they always go to the records room to read or write patient information.
>
> **Critical:** If etcd's records room burns down, the hospital has no idea who any of its patients are. This is why **etcd backups are the most critical backup in a K8s cluster.**

**What happens if it dies?**
- Cluster enters read-only mode (API server can't write new state)
- Existing workloads continue running
- No changes can be made until etcd recovers
- If you lose etcd data permanently and have no backup → catastrophic data loss

**Raft Consensus (briefly):**
In production, etcd runs as 3 or 5 nodes. They use the **Raft algorithm** to agree on what's written — like a committee that votes. If 1 of 3 nodes dies, the other 2 can still agree. This is why you always run an **odd number** of etcd nodes (3, 5, 7).

---

### 3. Scheduler (`kube-scheduler`)

**What it is:** The component that decides WHICH worker node a new pod should run on.

**What it does:**
1. Watches the API server for pods that have no node assigned (`spec.nodeName` is empty)
2. For each such pod, runs a scoring algorithm across all available nodes
3. Picks the best node
4. Writes the node assignment back to the API server (which writes to etcd)
5. The kubelet on that node sees the assignment and actually starts the pod

```
Pod created (no node assigned)
         │
         ▼
    ┌─────────────────────────────────┐
    │           Scheduler             │
    │                                 │
    │  Step 1: Filter (hard rules)    │
    │  ┌───────────────────────────┐  │
    │  │ - Enough CPU/RAM?         │  │
    │  │ - Has required labels?    │  │
    │  │ - Node not tainted?       │  │
    │  │ - Pod's affinity rules?   │  │
    │  └───────────────────────────┘  │
    │  Step 2: Score (soft rules)     │
    │  ┌───────────────────────────┐  │
    │  │ - Node with most free RAM │  │
    │  │ - Spread pods evenly      │  │
    │  │ - Close to data source    │  │
    │  └───────────────────────────┘  │
    │  Step 3: Pick highest score     │
    └─────────────────────────────────┘
              │
              ▼
    Updates pod: spec.nodeName = "node-3"
```

> **Analogy:** The Scheduler is a **logistics manager at a staffing agency**.  
> A job order comes in (a new pod needs to run). The manager looks at all available workers (nodes) — who has capacity? Who has the right skills (labels/taints)? Who lives closest to the job site (data affinity)?  
> The manager picks the best fit and assigns the job. The worker then executes it.

**What happens if it dies?**
- Existing pods keep running fine
- **New pods will be stuck in "Pending" state** — no one to assign them to a node
- Pods that crash and need rescheduling will also be stuck

---

### 4. Controller Manager (`kube-controller-manager`)

**What it is:** A single process running many "controllers" — each watching specific objects and taking corrective action.

**The controller pattern:**

```
 ┌─────────────────────────────────────────┐
 │           Controller Loop               │
 │                                         │
 │  1. OBSERVE: What is the current state? │
 │     (ask API server)                    │
 │              │                          │
 │              ▼                          │
 │  2. DIFF: Does it match desired state?  │
 │     (compare spec vs status)            │
 │              │                          │
 │     YES ─────┼──► Sleep, check again   │
 │              │                          │
 │     NO  ─────┼──► Take action          │
 │              ▼                          │
 │  3. ACT: Make the change               │
 │     (create/delete/update via API)      │
 │              │                          │
 │              └──────────────► Go to 1  │
 └─────────────────────────────────────────┘
```

**Built-in controllers include:**

| Controller | Watches | Acts When |
|-----------|---------|-----------|
| **Deployment Controller** | Deployments | Replica count is wrong → creates/deletes ReplicaSets |
| **ReplicaSet Controller** | ReplicaSets | Pod count ≠ desired replicas → creates/deletes Pods |
| **Node Controller** | Nodes | Node goes offline → marks pods as evicted |
| **Job Controller** | Jobs | Needs N completions → creates pods to complete them |
| **Endpoints Controller** | Services + Pods | Pod IP changes → updates Service endpoints |
| **Namespace Controller** | Namespaces | Namespace deleted → cleans up all resources inside |

> **Analogy:** Each controller is a **quality control inspector** at a factory.  
> The Deployment Inspector walks the factory floor every few seconds: "I need to see 3 running Assembly Line Bs. I can only count 2. Something happened to the third. I'll order a new one."  
> It doesn't care WHY there are only 2 — it just reconciles. This is called the **reconciliation loop**.

**What happens if it dies?**
- Existing pods keep running
- Self-healing STOPS — crashed pods won't be restarted
- Deployments won't scale, node failures won't trigger rescheduling
- Eventually, your cluster "drifts" away from desired state

---

## ⚙️ Worker Node Components

### 5. kubelet

**What it is:** The agent that runs on every worker node. It's the "boots on the ground" of K8s.

**What it does:**
- Watches the API server for pods that are assigned to ITS node
- Tells the container runtime (Docker/containerd) to actually start/stop containers
- Monitors container health and reports status back to the API server
- Runs liveness/readiness probes
- Manages pod lifecycle on the node

```
API Server: "Hey kubelet on node-3, you need to run this pod"
                           │
                           ▼
                       kubelet
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
   Pull image        Start container    Set up volumes
   (if needed)       via containerd     and networking
         │                 │
         └─────────────────┘
                  │
                  ▼
         Report status back to API server
         "Pod 'nginx-xyz' is Running on 10.0.0.5"
```

> **Analogy:** kubelet is the **on-site foreman** on a construction site.  
> The head office (control plane) sends blueprints. The foreman takes those blueprints and actually directs the workers (container runtime) to build the structure (container).  
> The foreman also sends daily reports back to the head office: "Foundation complete, walls at 50%, roof not started."

**What happens if it dies?**
- Containers on that node might still run (the container runtime is separate)
- But the node is now "dark" — no health reports, no new pods, no pod restarts
- The Node Controller will eventually mark the node `NotReady` and evict its pods to other nodes

---

### 6. kube-proxy

**What it is:** A network proxy running on every node. It implements the Service networking abstraction.

**What it does:**
- Watches for Service and Endpoint objects in the API server
- Maintains iptables/IPVS rules on each node that route traffic to the right pods
- Makes the "Service virtual IP" concept real at the network level

```
Request arrives at Node for Service IP 10.96.0.1:80
                    │
                    ▼
              kube-proxy rules (iptables)
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
   Pod 10.0.1.5  Pod 10.0.2.3  Pod 10.0.3.7
   (node-1)      (node-2)       (node-3)
   
   Traffic load-balanced across all healthy pods!
```

> **Analogy:** kube-proxy is like the **switchboard operator** at an old telephone company.  
> When you dial a "Service number" (virtual IP), the switchboard knows exactly which physical phone (pod IP) to connect you to, and it can spread calls across multiple phones if several are available.  
> It also updates its routing table whenever phones are added or removed.

---

### 7. Container Runtime

**What it is:** The actual software that runs containers. K8s doesn't run containers itself — it delegates to a runtime.

**Options:**
- **containerd** (default in most modern K8s distros — spun out of Docker)
- **CRI-O** (Red Hat's lightweight runtime)
- **Docker Engine** (via dockershim, removed from K8s 1.24+)

They all implement the **Container Runtime Interface (CRI)** — a standard API that kubelet uses to talk to any runtime.

> **Analogy:** The container runtime is the **oven in the kitchen**.  
> The kubelet (foreman) says "bake this recipe (container image) at 350°F (resource limits)."  
> The oven doesn't care who ordered the dish — it just bakes. You could swap a gas oven for an electric one (Docker for containerd) and the foreman uses the same commands.

---

## 🔗 How ALL Components Talk (Request Flow Walkthrough)

Let's trace exactly what happens when you run `kubectl apply -f deployment.yaml`:

```
Step 1: kubectl reads the YAML file
Step 2: kubectl sends HTTP POST to API Server
        POST /apis/apps/v1/namespaces/default/deployments

Step 3: API Server
        ├── Authenticates you (who are you?)
        ├── Authorizes you (can you create deployments?)
        ├── Validates the manifest (is it valid?)
        └── Writes the Deployment object to etcd

Step 4: Deployment Controller (inside controller-manager)
        ├── Watching API Server: "New Deployment appeared!"
        ├── Calculates: need 3 pods, have 0 → deficit of 3
        └── Creates 1 ReplicaSet → API Server writes to etcd

Step 5: ReplicaSet Controller
        ├── Watching API Server: "New ReplicaSet appeared!"
        ├── Calculates: need 3 pods, have 0
        └── Creates 3 Pod objects → API Server writes to etcd
            (Pods exist as objects but have no node assigned yet)

Step 6: Scheduler
        ├── Watching API Server: "3 pods with no nodeName!"
        ├── Runs filter + score for each pod
        └── Updates each pod: spec.nodeName = "node-X"

Step 7: kubelet on node-X
        ├── Watching API Server: "A pod for me appeared!"
        ├── Tells containerd: "Pull image, start container"
        ├── containerd pulls the image, starts the container
        └── kubelet reports back: "Pod is Running"

Step 8: API Server writes "Running" status to etcd

Step 9: kubectl get pods shows "Running" ✅
```

```
Timeline:
kubectl apply → [API Server] → [etcd] → [Controller Manager]
                                              │
                                         creates pods
                                              │
                                         [Scheduler]
                                              │
                                      assigns to nodes
                                              │
                                          [kubelet]
                                              │
                                     [Container Runtime]
                                              │
                                       Container Running!
```

---

## 💀 "What If X Dies?" — Failure Mode Map

This is a critical table. **Exam questions love this.**

| Component Dies | Immediate Effect | Long-term Effect |
|---------------|-----------------|-----------------|
| **API Server** | kubectl stops working | Cluster is "deaf" — no changes possible |
| **etcd** | API Server can't write | No state changes; if data lost → disaster |
| **Scheduler** | New pods stuck Pending | Existing pods fine; nothing new can start |
| **Controller Manager** | Self-healing stops | Pods won't restart; scaling stops working |
| **kubelet** (on a node) | That node goes dark | Node Controller evicts pods after timeout |
| **kube-proxy** (on a node) | Networking breaks on that node | Existing connections may work; new ones fail |
| **Container Runtime** | Containers can't start/stop | All pods on that node may die |

---

## 🔁 The Desired State Feedback Loop (The Most Important Concept)

```
YOU write:
  "I want 3 replicas of nginx"
           │
           ▼
     Stored in etcd
     (desired state)
           │
    ┌──────┴──────────────────────────────┐
    │         CONTINUOUS LOOP             │
    │                                     │
    │  K8s checks:                        │
    │  actual state == desired state?     │
    │                                     │
    │  YES → do nothing                   │
    │  NO  → take corrective action       │
    │                                     │
    │  Examples of "NO":                  │
    │  - 2 replicas running, need 3 → +1  │
    │  - Pod crashed → restart it         │
    │  - Node died → reschedule pods      │
    │  - You changed replicas to 5 → +2   │
    └─────────────────────────────────────┘
```

> **Analogy:** This is like a **home thermostat**.  
> You set the desired temperature to 22°C (desired state).  
> The thermostat continuously measures the actual temperature (actual state).  
> Too cold → heater turns on. Too hot → AC turns on. Exactly right → nothing happens.  
> **You never tell the thermostat HOW to heat or cool. You just declare what you want.**

---

## 🗺️ Full Architecture At a Glance (Memorize This)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CONTROL PLANE                           │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    API SERVER                           │  │
│   │   The single gateway. Everything talks through here.    │  │
│   └──────────────────────┬──────────────────────────────────┘  │
│                           │                                     │
│   ┌───────────────────────┼───────────────────────────────┐    │
│   │           ┌───────────┼───────────┐                   │    │
│   ▼           ▼           ▼           ▼                   │    │
│ ┌──────┐ ┌─────────────────────────┐ ┌──────────┐        │    │
│ │ etcd │ │   Controller Manager   │ │Scheduler │        │    │
│ │      │ │  ┌───┐ ┌───┐ ┌───┐    │ │          │        │    │
│ │ The  │ │  │Dep│ │RS │ │Node│    │ │ Assigns  │        │    │
│ │ only │ │  │ctl│ │ctl│ │ ctl│    │ │ pods to  │        │    │
│ │store │ │  └───┘ └───┘ └───┘    │ │  nodes   │        │    │
│ └──────┘ └─────────────────────────┘ └──────────┘        │    │
└─────────────────────────────────────────────────────────────────┘
                 ▲ all via API Server ▲
                 │                   │
┌────────────────┼───────────────────┼─────────────────────────────┐
│                │  WORKER NODES     │                              │
│  ┌─────────────┴────────────┐   ┌──┴──────────────────────────┐  │
│  │         Node 1           │   │         Node 2              │  │
│  │                          │   │                             │  │
│  │  ┌───────┐ ┌──────────┐  │   │  ┌───────┐ ┌──────────┐   │  │
│  │  │kubelet│ │kube-proxy│  │   │  │kubelet│ │kube-proxy│   │  │
│  │  └───────┘ └──────────┘  │   │  └───────┘ └──────────┘   │  │
│  │  ┌──────────────────────┐│   │  ┌──────────────────────┐  │  │
│  │  │  Container Runtime   ││   │  │  Container Runtime   │  │  │
│  │  │    (containerd)      ││   │  │    (containerd)      │  │  │
│  │  └──────────────────────┘│   │  └──────────────────────┘  │  │
│  │  ┌────┐ ┌────┐ ┌────┐   │   │  ┌────┐ ┌────┐ ┌────┐     │  │
│  │  │Pod │ │Pod │ │Pod │   │   │  │Pod │ │Pod │ │Pod │     │  │
│  │  └────┘ └────┘ └────┘   │   │  └────┘ └────┘ └────┘     │  │
│  └──────────────────────────┘   └─────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🧪 Test Yourself

1. **What is the ONLY place cluster state is stored?** (Don't say "etcd" without explaining what it stores)
2. **What does the Scheduler do AFTER it picks a node for a pod?** (It doesn't start the pod — what does it do?)
3. **What is the Reconciliation Loop?** Explain it using the thermostat analogy in your own words.
4. **If the Controller Manager crashes, what immediately breaks?** What still works?
5. **Trace the full journey:** What are ALL the steps from `kubectl apply -f` to a pod being `Running`? Name every component involved.
6. **Why do you always run an odd number of etcd nodes?**
7. **What's the difference between kubelet and the container runtime?**

> 🎯 **Challenge:** Close this file and draw the entire architecture on paper. Label every component and draw arrows showing which components talk to which. Check your drawing against the diagrams above.
