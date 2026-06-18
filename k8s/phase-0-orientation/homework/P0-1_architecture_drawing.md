# Homework P0-1 — Draw the Architecture from Memory

> **Time:** 30–45 minutes  
> **Materials:** Paper and pen (yes, physical paper — muscle memory matters)  
> **No peeking at notes while drawing!**

---

## 📋 Instructions

### Step 1 — Close Your Notes (5 min)

Close `02_architecture.md`. Do not look at it.  
Give yourself 5 minutes to mentally recall everything you know.

---

### Step 2 — Draw (20 min)

On paper (or a whiteboard), draw the full Kubernetes architecture.

**Your drawing must include all of the following:**

**Control Plane (box at the top):**
- [ ] API Server — with a note on what it does
- [ ] etcd — with a note on what it stores
- [ ] Controller Manager — with at least 2 example controllers listed
- [ ] Scheduler — with a note on what it decides

**Worker Nodes (at least 2 boxes):**
- [ ] kubelet — with a note on what it does
- [ ] kube-proxy — with a note on what it manages
- [ ] Container Runtime — named (containerd)
- [ ] At least 3 pods drawn inside each node

**Connections:**
- [ ] Arrows showing that kubectl → API Server
- [ ] Arrows showing that kubelet → API Server (not direct to control plane components!)
- [ ] A note that ALL components communicate THROUGH the API Server

---

### Step 3 — Annotate Failure Modes (10 min)

Next to each component, write what happens if it dies.  
Use these prompts:

```
API Server dies →
etcd dies →
Scheduler dies →
Controller Manager dies →
kubelet dies (on a worker node) →
```

---

### Step 4 — The Request Flow (10 min)

On a separate section of the paper, draw the flow of:

```
"What happens when I run: kubectl apply -f deployment.yaml"
```

Draw each step with arrows. Every component that is involved should appear in the chain.

**Hint:** There are 8 distinct steps across 6 components.

---

### Step 5 — Check Your Work

Now open `02_architecture.md` and compare. For every component you missed or got wrong:

1. Re-read that section
2. Cover it up again
3. Explain it aloud (talk to yourself — it's how you learn!)
4. Redraw just that component

---

## ✅ Done When:

- [ ] Physical drawing exists on paper
- [ ] All 7 components are labeled with their role
- [ ] Failure modes are written for each component
- [ ] The kubectl → Running Pod request flow is drawn step by step
- [ ] You can explain each component out loud without reading your drawing

---

## 📝 Reflection Questions

Write 2-3 sentences answering each:

**1. Before Kubernetes, what was the hardest part of managing many containers?**

```
Your answer here:
```

**2. The API Server is described as "the gateway." Why does everything have to go through it rather than components talking directly to each other?**

```
Your answer here:
```

**3. In your own words, what is the "reconciliation loop" and why is it powerful?**

```
Your answer here:
```

---

> 🎯 **Goal test:** Can you explain each component to a colleague in under 30 seconds, without notes? That's the bar.
