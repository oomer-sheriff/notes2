# Level 3: Deep Waters (Routing & The Network Layer)

Congratulations on conquering sockets and ports! Now we step away from your specific machine and look at the infrastructure that ties the world together: **The Network Layer (Layer 3)**.

## 1. The IPv4 Shortage & NAT

As we discussed in Level 1, IPv4 addresses are 32-bit numbers. Mathematically, $2^{32}$ gives us about **4.3 billion** unique IP addresses. 

In the 1980s, that seemed like infinite space. Today, with laptops, phones, smart TVs, and IoT fridges, 4.3 billion is nowhere near enough for the global population. We ran out of IPv4 addresses years ago.

### Deep Dive: The IPv4 Packet Header
Before a packet can be routed, it must be constructed. At Layer 3, your application data and TCP segment are wrapped in an **IP Header** (usually 20 bytes). Key fields include:
1. **Source IP & Destination IP (32 bits each):** Where it's from and where it's going.
2. **TTL (Time to Live):** An integer (e.g., 64) that decrements by 1 at every router hop. If TTL hits 0, the packet is instantly dropped to prevent infinite routing loops!
3. **Protocol (8 bits):** Tells the destination OS what Layer 4 protocol is inside (e.g., `6` for TCP, `17` for UDP).
4. **Header Checksum:** Ensures the IP header wasn't corrupted by electrical noise in transit.
5. **Fragmentation Offsets:** If a packet is too large for a specific router link (exceeds the physical MTU limits), the router fragments the packet into smaller pieces. This field allows the final destination to properly reassemble them.

*How does the internet still work if we are out of addresses?*
**Enter NAT (Network Address Translation).**

### How NAT Works
Instead of giving every single device in your house a unique global IP address, your Internet Service Provider (ISP) only gives you **ONE** public IP address. It assigns this to your Router.

Your Router then creates a completely private, localized network inside your house (your LAN). It hands out private IP addresses (like `192.168.1.6`) to your devices. 
- These private IPs are non-routable on the internet.
- Millions of other houses are using the exact same `192.168.1.6` address inside their own walls.

When your laptop wants to talk to Google:
1. Your laptop (`192.168.1.6`) sends the packet to the Router.
2. The Router removes your private IP, stamps the packet with its **single Public IP**, and sends it to Google.
3. Google replies to the Router's Public IP.
4. The Router looks at its internal translation table to remember who originally asked, swaps the Public IP back to your private `192.168.1.6`, and hands it to your laptop.

### Deep Dive: PAT and the Translation State Table
Technically, NAT translates IP addresses, but **PAT (Port Address Translation)** is what routers actually use to handle multiple devices simultaneously.
When your laptop (`192.168.1.6`) opens a TCP connection on Ephemeral Port `50000`, the packet hits the router.
The router builds a **State Table** in its memory:
- **Internal Device:** `192.168.1.6:50000`
- **External Alias:** `59.182.208.1:60000` (The router's public IP + a newly generated ephemeral port).

The router rewrites the packet header to show the External address as the Source, and sends it to Google. When Google replies to `59.182.208.1:60000`, the router checks its table in `O(1)` time, rewrites the destination back to `192.168.1.6:50000`, and passes it safely to your laptop!

---

## 2. Subnetting & CIDR

Since IPs are limited, we have to group them efficiently. We do this by breaking large networks into smaller sub-networks (Subnets).

An IP address actually contains two pieces of information:
1. **The Network ID:** Which street do you live on?
2. **The Host ID:** Which specific house is yours?

### Subnet Masks
How does a computer know which part of the IP is the Network ID and which is the Host ID? It uses a **Subnet Mask**.
If you recall your `ipconfig` output, your mask was `255.255.255.0`.
- `255` means "This part belongs to the Network".
- `0` means "This part belongs to the Host".

So for IP `192.168.1.6` with mask `255.255.255.0`:
- **Network ID:** `192.168.1` (Everyone in your house shares this).
- **Host ID:** `.6` (Your specific laptop).

### Deep Dive: Binary Subnet Masking and CIDR Notation
Writing out `255.255.255.0` is tedious. Engineers use **CIDR notation**.
Computers don't see `255.255.255.0`; they see binary:
`11111111 . 11111111 . 11111111 . 00000000`
Since there are exactly 24 consecutive `1`s, we just append `/24` to the IP! Example: `192.168.1.6/24`.

When a router receives a packet for `192.168.1.50`, it uses **Bitwise AND operations** against the Subnet Mask to find the Network ID.
IP:   `11000000 . 10101000 . 00000001 . 00110010` (192.168.1.50)
Mask: `11111111 . 11111111 . 11111111 . 00000000` (/24)
--------------------------------------------------
AND:  `11000000 . 10101000 . 00000001 . 00000000` -> This is the Network ID `192.168.1.0`. 
The router now knows exactly which subnet to send the packet to, executed at blazing hardware speed!

---

## 3. Routing Tables (In-Depth)

When you run `requests.get("http://github.com")`, how does the packet actually get there?
Every router (and even your own computer!) holds a **Routing Table**—a list of directions. A typical routing table entry contains:
1. **Network Destination & Netmask:** The target network (e.g., `10.0.0.0/8`).
2. **Gateway (Next Hop):** The IP address of the *next* router in the path.
3. **Interface:** The physical port the packet should be pushed out of.
4. **Metric:** The "cost" of this route (lower is better). If there are two physical paths to the same destination, the router chooses the one with the lowest metric.

### The Algorithm: Longest Prefix Match (LPM)
Since you have a strong DSA background, this is where routing gets really interesting. An enterprise router might have hundreds of thousands of entries. If a packet is destined for `192.168.1.50`, and the routing table has rules for both `192.168.1.0/24` (specific) and `192.0.0.0/8` (broad), which one does it pick? 

Routers use the **Longest Prefix Match** algorithm. They always choose the most specific rule (the one with the longest subnet mask). In hardware, this is often implemented using a highly optimized **Trie** (Prefix Tree) data structure, or in specialized physical memory called TCAM (Ternary Content-Addressable Memory) to perform the lookup in absolute `O(1)` time!

### The "Catch-All": Default Route
If the router's Trie lookup yields absolutely no matches for an IP, it falls back to the **Default Route**. In IPv4, this is written as the network `0.0.0.0` with a mask of `0.0.0.0` (or `0.0.0.0/0`). It basically means "Send everything else here." For your home network, this points straight out to your ISP.

### Static vs. Dynamic Routing
- **Static Routing:** A human engineer manually types the routes into the router. This works for small networks but is impossible to maintain at scale.
- **Dynamic Routing:** Routers talk to each other to automatically build their tables using classic graph algorithms:
  - **Distance-Vector (RIP):** Older protocols that simply ask neighbors "How many hops away is this network?" and pick the path with the fewest hops. Blind to actual bandwidth speeds.
  - **Link-State (OSPF - Open Shortest Path First):** Every router builds a complete topological map of the entire network. Each link is given a "cost" based on its bandwidth (e.g., Fiber is 1, Copper is 10). The router then runs **Dijkstra's Algorithm** locally to calculate the absolute optimal path to every destination!
  - **Path-Vector (BGP):** Used at the global Internet scale to connect different telecom companies together based on economics and policy.

---

## Next Steps: Hands-on

For our hands-on segment, we are going to use two terminal commands: `route print` to view your computer's own internal routing table, and `tracert` (Traceroute) to map the exact hop-by-hop router path a packet takes from your house to a server across the world!

Let me know when you are ready to map the internet.

my notes:
So essentialy, Nat is used to translate the private ip addresses of the devices on a network to a single public ip address for the whole network to share. and that way we can have more devices on a network.

PAT is used to track which packet belongs to which internal device.

CIDR is used to group IP addresses into subnets.

subnets are used to break down large networks into smaller, more manageable networks. typically has two parts, network id and host id.

255= network and 0 = allocatable user address space

Routing tables are used to keep track of shortest path from our router to a given server

We can manuall