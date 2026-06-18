# Level 5: The Ocean Floor (Advanced Engineering)

We have reached the very bottom of the networking iceberg. You now know how data is physicalized, routed, transported, secured, translated, and load-balanced across the world. 

In this final level, we look at the macro-architecture of the modern internet and the modern application layer that you will use daily as a Software Engineer.

---

## 1. BGP: The Protocol That Runs The Internet

We talked about Longest Prefix Match (LPM) and routing tables. But the internet has millions of routes. How does your ISP know how to get to Microsoft's Azure Network? 

They use **BGP (Border Gateway Protocol)**.
- BGP is the routing protocol of the internet.
- Instead of connecting routers, BGP connects entire **Autonomous Systems (AS)** (like your ISP, Google, AWS).
- **Autonomous System Numbers (ASNs):** Every major network (ISP, Google, AWS) is assigned a unique ASN (e.g., Google is AS15169).
- BGP is a **Path-Vector Protocol**. When a BGP router advertises a route to `20.207.0.0/16`, it attaches an **AS-PATH** attribute (e.g., `AS1234 -> AS5678 -> AS15169`). If a router sees its own ASN in the path, it drops the route to prevent loops!
- BGP does not inherently find the "fastest" route. It finds the route dictated by the **Local Preference** attribute, which is manually set by network engineers based on business peering agreements (e.g., "Send traffic through Tata Communications because we pay them less than AT&T").
- If an engineer misconfigures BGP, they can literally "black hole" internet traffic. This famously happened when a small ISP accidentally advertised an AS-PATH claiming they were the best route to YouTube, routing the entire globe's YouTube traffic into a tiny pipe that instantly collapsed.

---

## 2. Firewalls, ACLs, and NAT Security

We've focused on moving packets, but network security is often about *dropping* them.

- **Stateless Firewalls (ACLs):** Simple Access Control Lists that look at the port and IP and say "Drop all packets on Port 22 (SSH)".
- **Stateful Firewalls & Conntrack Tables:** Smarter firewalls that actively track connections. When your laptop sends a TCP SYN packet to GitHub, the firewall creates an entry in its `conntrack` (connection tracking) memory table. When GitHub replies with a SYN-ACK, the firewall dynamically allows it *only* because it matches the exact tuple `(Source IP, Source Port, Dest IP, Dest Port)` in its state table! Once the TCP `FIN` closes the connection, the firewall deletes the entry, locking the door behind you.
- **NAT as a Firewall:** Network Address Translation acts as a strict, implicit firewall. Since your computer (`192.168.1.6`) has no global IP address, a hacker on the internet literally cannot route a packet to you to initiate an attack. They can only reply to connections you specifically initiated first.

---

## 3. Modern Application Communication: REST vs gRPC vs WebSockets

As an engineer, you won't write raw TCP sockets like we did in our python script very often. You will use higher-level abstractions.

### REST (Representational State Transfer)
- Runs over standard HTTP/1.1 or HTTP/2.
- Uses **JSON (JavaScript Object Notation)** payloads. JSON is human-readable, flexible, and supported by every browser out of the box.
- **The Drawback:** JSON is extremely bloated. Sending `{"id": 123}` wastes dozens of bytes on string keys, quotes, and whitespace. Parsing JSON strings into memory objects is also highly CPU intensive for servers handling 100,000 requests per second.

### gRPC (Google Remote Procedure Call)
- Runs strictly over HTTP/2 (allowing true multiplexing: sending multiple requests simultaneously over a single TCP socket).
- Uses **Protocol Buffers (Protobuf)** instead of JSON. Protobuf is a strictly-typed binary format.
- Instead of sending the string `{"id": 123}`, it compiles the data into raw binary bytes. Because the sender and receiver both have the `.proto` schema file, they know exactly which bit corresponds to the `id` field!
- **The Advantage:** It drastically reduces network bandwidth and CPU parsing overhead. It is the gold standard for high-performance microservices talking to other microservices inside modern datacenters.

### WebSockets
- HTTP is strictly Request -> Response. The server cannot send you data unless you ask for it.
- **WebSockets** solve this by doing an initial HTTP Handshake, and then "upgrading" the connection back into a raw, persistent, bidirectional TCP socket!
- Used for chat apps, live sports scores, and multiplayer games.

---

## Conclusion

From `ipconfig` to `BGP`, you have mapped the full geography of Computer Science Networking. 

You can now confidently look at a system architecture diagram—with Load Balancers, Reverse Proxies, DNS Records, Subnets, and Firewalls—and understand exactly how the bits are physically moving from the silicon to the screen.
