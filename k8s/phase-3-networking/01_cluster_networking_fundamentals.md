# 01 — Cluster Networking Fundamentals

> **The single most important rule:** In Kubernetes, every Pod gets its own IP address, and every Pod can reach every other Pod directly — across any node — without NAT. This is called the **flat network model**, and it's the foundation of everything else in this phase.

---

## 🤯 The Flat Network Model

In a traditional network, if Machine A on subnet `192.168.1.x` wants to reach Machine B on subnet `192.168.2.x`, it needs routing, NAT, or a gateway.

Kubernetes says: **forget all of that for pods.**

```
Traditional network (NAT required):
  Pod A (10.244.1.4) on Node 1
    │
    │ → goes through NAT → 192.168.1.10 (Node 1's real IP) → router → Node 2
    │
  Pod B (10.244.2.7) on Node 2

K8s flat network (NO NAT):
  Pod A (10.244.1.4) on Node 1
    │
    │ → directly → 10.244.2.7
    │
  Pod B (10.244.2.7) on Node 2
  
Pod A knows Pod B's real IP. Pod B sees Pod A's real IP. No masquerading.
```

**The four requirements of the K8s network model:**
1. Every pod gets a unique cluster-wide IP
2. Every pod can reach every other pod by IP without NAT
3. Agents on a node (kubelet, kube-proxy) can reach all pods on that node
4. Nodes can reach all pods on all nodes

Kubernetes itself does NOT implement this. It specifies the rules and requires a **CNI plugin** to implement them.

---

## 🔌 CNI — Container Network Interface

**CNI (Container Network Interface)** is a standard spec for how networking plugins communicate with Kubernetes. When a pod is created, Kubernetes calls the CNI plugin to:
1. Create a network namespace for the pod
2. Assign it an IP address from the pod CIDR range
3. Set up routes so the pod can reach other pods and the node

```
Pod creation flow (networking part):
  kubelet: "I'm creating a new pod"
       │
       └─→ Calls CNI plugin
               │
               ├─→ Creates veth pair (virtual ethernet cable)
               │     one end in pod network namespace
               │     other end on the node (host namespace)
               │
               ├─→ Assigns IP from pod CIDR
               │     e.g., 10.244.1.4/24
               │
               └─→ Sets up routes:
                     "Traffic to 10.244.2.x → go to Node 2"
```

### Popular CNI Plugins

| CNI Plugin | Mechanism | NetworkPolicy? | Notable Feature |
|-----------|-----------|---------------|----------------|
| **Flannel** | VXLAN overlay | ❌ No | Simplest, great for learning |
| **Calico** | BGP routing or VXLAN | ✅ Yes | Most feature-rich, widely used |
| **Cilium** | eBPF (bypass iptables) | ✅ Yes | Best performance, observability |
| **Weave** | Encrypted mesh | ✅ Yes | Easy multi-cloud |
| **kindnet** | Routes (in-cluster) | ❌ No | Default in kind clusters |

> 💡 **Your kind cluster uses `kindnet`**, which is intentionally minimal. It supports the flat network model but does NOT support NetworkPolicy. For the NetworkPolicy lab in this phase, we'll install Calico or use Killercoda's pre-configured environment.

---

## 🌐 How Pod-to-Pod Traffic Actually Flows

### Same Node Communication

```
Pod A (10.244.1.4) → Pod B (10.244.1.7)  (both on Node 1)

                    Node 1
         ┌─────────────────────────────┐
         │                             │
         │  ┌──────┐     ┌──────┐     │
         │  │Pod A │     │Pod B │     │
         │  │.1.4  │     │.1.7  │     │
         │  └──┬───┘     └───┬──┘     │
         │     │veth0         │veth1   │
         │     │              │        │
         │  ┌──▼──────────────▼──┐    │
         │  │   Linux Bridge      │   │
         │  │   (cbr0 / cni0)     │   │
         │  └─────────────────────┘   │
         └─────────────────────────────┘

Traffic: Pod A → veth0 → bridge → veth1 → Pod B
         (stays on same node, no node routing needed)
```

### Cross-Node Communication

```
Pod A (10.244.1.4) → Pod C (10.244.2.9)  (different nodes)

      Node 1                              Node 2
┌──────────────────┐               ┌──────────────────┐
│  ┌──────┐        │               │        ┌──────┐  │
│  │Pod A │        │               │        │Pod C │  │
│  │.1.4  │        │               │        │.2.9  │  │
│  └──┬───┘        │               │        └───┬──┘  │
│     │veth         │               │            │veth  │
│     │             │               │            │      │
│  ┌──▼──────┐     │               │     ┌──────▼──┐  │
│  │ bridge  │     │               │     │ bridge  │  │
│  └──┬──────┘     │               │     └──┬──────┘  │
│     │             │               │        │          │
│  ┌──▼──────────┐ │   physical    │ ┌──────▼──────┐  │
│  │  eth0/ens3  ├─┼───network─────┼─┤  eth0/ens3  │  │
│  │(Node1 IP)   │ │               │ │(Node2 IP)   │  │
│  └─────────────┘ │               │ └─────────────┘  │
└──────────────────┘               └──────────────────┘

CNI sets up routes on each node:
  Node 1: "Traffic for 10.244.2.x → send to Node 2's eth0"
  Node 2: "Traffic for 10.244.1.x → send to Node 1's eth0"
```

The CNI plugin handles the "how" — either via VXLAN tunneling (overlay network) or via BGP routing (underlay routing). The end result is the same: Pod A sees Pod C at its direct IP.

---

## 🔧 kube-proxy — Making Services Work

We touched on kube-proxy in Phase 0. Let's go deeper now.

### What kube-proxy Actually Does

kube-proxy runs on every node and watches the API server for Service and Endpoints objects. When they change, it updates **iptables rules** (or IPVS rules) on that node.

```
You create:  Service "backend-svc" with ClusterIP 10.96.45.21
                           │
                    API Server stores it
                           │
              kube-proxy on EVERY NODE watches and updates iptables:
                           │
         Node 1 iptables:              Node 2 iptables:
         -A KUBE-SVC-xyz               -A KUBE-SVC-xyz
           -j KUBE-SEP-abc (33%)         -j KUBE-SEP-abc (33%)
           -j KUBE-SEP-def (33%)         -j KUBE-SEP-def (33%)
           -j KUBE-SEP-ghi (33%)         -j KUBE-SEP-ghi (33%)
         
         KUBE-SEP-abc → DNAT to 10.244.1.4:8080
         KUBE-SEP-def → DNAT to 10.244.2.7:8080
         KUBE-SEP-ghi → DNAT to 10.244.3.2:8080
```

When traffic hits `10.96.45.21:80`, iptables randomly selects one of the pod IPs and rewrites the destination (DNAT). The traffic arrives at the pod looking like it came from the original source.

> **Analogy:** kube-proxy is like a **post office sorter**.  
> You write "Customer Service Department" on an envelope (Service IP).  
> The sorter has a lookup table of which desk handles customer service today (pod IPs).  
> It rewrites the envelope with a specific desk number (pod IP) and sends it there.  
> The desk receives mail addressed to it directly — it never even sees the original "Customer Service" address.

### kube-proxy Modes

| Mode | How | Performance | Default? |
|------|-----|------------|---------|
| `iptables` | Linux iptables rules | Medium | Yes (most clusters) |
| `IPVS` | Linux IPVS (kernel LB) | High | Optional |
| `nftables` | nftables (modern replacement for iptables) | High | K8s 1.29+ |

For the exam, know that iptables mode is the default and how it works conceptually.

---

## 📦 Pod CIDR vs Service CIDR vs Node CIDR

Three separate IP ranges in a K8s cluster:

```
┌─────────────────────────────────────────────────────────────────┐
│                         K8s Cluster                             │
│                                                                 │
│  Node IP range (real network): 192.168.1.0/24                  │
│    Node 1: 192.168.1.10                                        │
│    Node 2: 192.168.1.11                                        │
│    Node 3: 192.168.1.12                                        │
│                                                                 │
│  Pod CIDR (virtual, flat): 10.244.0.0/16                      │
│    Node 1 pods: 10.244.1.0/24                                  │
│    Node 2 pods: 10.244.2.0/24                                  │
│    Node 3 pods: 10.244.3.0/24                                  │
│                                                                 │
│  Service CIDR (virtual): 10.96.0.0/12                          │
│    Services get IPs here: 10.96.45.21, 10.96.12.3, etc.       │
│    These are NOT assigned to any real interface                │
│    They exist ONLY in iptables rules                           │
│                                                                 │
│  No overlap between these three ranges (required!)             │
└─────────────────────────────────────────────────────────────────┘
```

**Check your kind cluster's ranges:**
```bash
# Pod CIDR per node
kubectl get nodes -o jsonpath='{.items[*].spec.podCIDR}'

# Service CIDR (look at API server arguments)
kubectl describe pod kube-apiserver-k8s-multinode-control-plane -n kube-system | grep service-cluster-ip-range
```

---

## 🔍 Debugging Network Issues — The Toolkit

```bash
# Launch netshoot — the Swiss army knife debug container
kubectl run netdebug --image=nicolaka/netshoot -it --rm -- bash

# Inside netshoot, you have: ping, curl, tcpdump, nslookup, dig,
# traceroute, nc (netcat), ss, ip, iftop, and more

# Test pod connectivity
ping 10.244.2.7                      # Direct pod IP

# Test service connectivity
curl http://my-service:80             # Via service name
curl http://10.96.45.21:80            # Via service ClusterIP

# DNS
nslookup my-service
dig my-service.default.svc.cluster.local

# Network interfaces
ip addr
ip route show

# Check connections
ss -tulnp                            # Listening sockets
```

---

## 🧪 Test Yourself

1. **What does "flat network" mean in Kubernetes?** What would networking look like WITHOUT it?

2. **What is a CNI plugin?** Name 3 examples and one difference between them.

3. **Pod A is on Node 1. Pod B is on Node 2. Pod A sends a packet to Pod B's IP. Walk through the path — every hop from Pod A's network namespace to Pod B's.** Be specific.

4. **The Service ClusterIP `10.96.45.21` doesn't exist on any network interface. How does traffic sent to it actually reach a pod?**

5. **What is DNAT and why does kube-proxy use it?**

6. **Your kind cluster uses `kindnet`. You try to apply a NetworkPolicy. Does it work?** Why or why not?

7. **Three pods are behind a Service. kube-proxy uses iptables to distribute traffic. Is this a true load balancer?** What's the distribution mechanism?
