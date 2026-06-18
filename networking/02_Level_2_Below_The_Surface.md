# Level 2: Below the Surface (Protocols & Models)

We've proven your machine can physically map to and reach the router. But *how* does data actually travel from your web browser to a server across the world in an organized way? We need standards.

## 1. Network Models: OSI vs. TCP/IP

To handle the immense complexity of networking, engineers divide the problem into **Layers**. Each layer has a very specific job and only talks to the layer directly above or below it.

### The OSI Model (7 Layers)
This is the theoretical model taught in every CS class. It's great for troubleshooting ("Is this a Layer 2 or Layer 3 issue?"):
1. **Physical:** Cables, radio waves, electrical signals. (Hubs live here).
2. **Data Link:** MAC addresses, switching, Ethernet frames. (Switches live here).
3. **Network:** IP addresses, routing packets across networks. (Routers live here).
4. **Transport:** Managing end-to-end connections (TCP/UDP) and Ports. 
5. **Session:** Maintaining ongoing sessions between apps.
6. **Presentation:** Data formatting, encryption (like TLS/SSL), compression.
7. **Application:** The actual app protocol (HTTP, FTP, SMTP, DNS).

### The TCP/IP Model (4 Layers)
This is the *practical* model that the modern Internet actually runs on. It condenses the OSI model into 4 broader layers:
1. **Network Access (Link Layer):** Combines OSI Layers 1 & 2.
2. **Internet:** OSI Layer 3 (IP).
3. **Transport:** OSI Layer 4 (TCP/UDP).
4. **Application:** Combines OSI Layers 5, 6, & 7 (HTTP, DNS, etc.).

> **Engineering Insight:** When you write code (like a Python script using `requests.get()`), you are working at the **Application Layer**. Your operating system's kernel handles the **Transport** and **Network** layers automatically!

---

## 2. The Transport Layer: TCP vs. UDP

Once data reaches the correct IP address (Network Layer), how does the computer know which application gets the data? Is it for Chrome? Or a background Spotify stream? The Transport Layer solves this using **Ports**.

There are two main protocols used here, and choosing between them is a classic System Design interview question.

### TCP (Transmission Control Protocol)
- **Concept:** Connection-oriented and Reliable.
- **How it works:** It guarantees that every packet arrives, and arrives *in the correct order*. If a packet is lost, TCP automatically requests a retransmission. 
- **Overhead:** High. It requires a formal setup phase before sending any data.
- **Use Cases:** Web Browsing (HTTP), Email, File Transfers. (You don't want a webpage to load with missing chunks of text).

### Deep Dive: TCP Segment Headers and Congestion Control
To guarantee reliability without the application's help, TCP wraps your Application data in a **TCP Segment**. The header contains crucial fields:
1. **Sequence Number (SEQ):** Since data is broken into chunks, the Sequence Number tells the receiver the exact byte-offset of this chunk. If a packet arrives out of order, the receiver uses SEQ to reassemble the file perfectly.
2. **Acknowledgment Number (ACK):** The receiver sends an ACK back to the sender confirming it received the bytes. If the sender doesn't receive an ACK within a timeout period, it assumes the packet was lost on the wire and resends it.
3. **Flags:** 1-bit boolean flags that dictate the packet's purpose. `SYN` (Synchronize) for setup, `ACK` (Acknowledge) for receipts, `FIN` (Finish) to gracefully close the connection, `RST` (Reset) to forcefully kill it, and `PSH` (Push) to bypass buffers.

**Flow Control & Congestion Control:**
TCP doesn't just blindly blast data. It uses a **Sliding Window** to dictate how many bytes the sender can push before it MUST pause and wait for an ACK. To prevent overwhelming the global internet backbone, TCP uses algorithms like **Slow Start** (sending data slowly and exponentially doubling the speed until a packet drops) and **AIMD** (Additive Increase, Multiplicative Decrease) to continuously, mathematically probe the network for the absolute fastest transmission speed without causing congestion.

### UDP (User Datagram Protocol)
- **Concept:** Connectionless and Unreliable ("Fire and Forget").
- **How it works:** It blasts packets at the destination as fast as possible. It does not check if they arrived, and it does not reorder them.
- **Overhead:** Very low. Extremely fast.
- **Use Cases:** Live Video Streaming, Online Gaming, VoIP. (If a frame drops in a Zoom call, you don't want the network to pause the call to fetch the old frame—you just want the *newest* frame).

---

## 3. Ports and Sockets

We mentioned ports above, but let's define them formally since they are critical for system design and engineering:

### Ports
A Port is a 16-bit number (ranging from `0` to `65535`) that identifies a specific process or application running on a computer. 
- **Well-Known Ports (0 - 1023):** Reserved for standard, standardized protocols (e.g., Port `80` for HTTP, Port `443` for HTTPS, Port `22` for SSH, Port `53` for DNS).
- **Ephemeral Ports (49152 - 65535):** When you open Chrome and visit a website, your Operating System dynamically assigns Chrome a random, temporary port from this high range. The remote server needs to know this port so it knows exactly where to send the webpage data back to on your machine!

### Sockets
A Socket is a software abstraction—it's the programming interface for the network provided by the Operating System. 
You can think of an **IP Address** as a building's street address, and a **Port** as an apartment number inside that building. 

A **Socket** is simply the combination of the two (`IP:Port`). It is the actual "door" your Python code opened to the network in our hands-on exercise (e.g., the server bound to the socket `127.0.0.1:65432`).

### Deep Dive: Sockets as File Descriptors (FDs)
Under the hood in Linux and Unix, **"Everything is a file"**. A Socket is represented in the operating system's kernel as a **File Descriptor (FD)**. When your Python app calls `socket.socket()`, the OS allocates a unique integer (e.g., FD `5`). 
When you receive data from the network, the OS's Network Stack handles all the complexity. It parses the electrical signals, strips off the Ethernet Frame, strips off the IP Header, strips off the TCP Header, and then writes the raw Application payload into the memory buffer for File Descriptor `5`. Your Python script then reads that buffer *exactly like reading a normal text file from your hard drive!*

*(Note regarding your notes at the bottom: WebSockets are actually built on top of TCP, not UDP! They "upgrade" an HTTP connection into a raw, persistent, two-way TCP pipe. We will cover WebSockets fully in Level 5!)*

---

## 4. The TCP 3-Way Handshake

Because TCP guarantees delivery, it must establish a reliable "connection" before sending any actual payload data. It does this via the 3-Way Handshake:

1. **SYN (Synchronize):** Client says, "Hey Server, I'd like to talk. Let's sync up our packet sequence numbers."
2. **SYN-ACK (Synchronize-Acknowledge):** Server says, "I received your request (ACK), and I also want to sync up my sequence numbers with you (SYN)."
3. **ACK (Acknowledge):** Client says, "Got your sync. We are good to go!"

*Only after this 3-step dance can the client send an HTTP GET request.*

> **Engineering Insight:** The 3-way handshake takes a full Round-Trip Time (RTT). If a server is 100ms away, the handshake alone wastes 100ms before you even ask for data! This latency is why modern protocols like QUIC/HTTP3 (which run over UDP) were invented.

---

## Next Steps: Hands-on

For our hands-on segment, we are going to use **Python** to build a raw TCP Socket Server and Client. We will open up a specific port, establish a 3-way handshake, and send a message. 

Let me know when you've read through this, and we'll start writing our Python socket script!


my notes:

so essentially, OSI model is for abstraction and separation of this data going across computers into manageable layers, each layer does one unit of processing, verification etc

TCP is 3 way handshake, reliable, overhead is high, used for web browsing email file transfer etc

UDP is fast but unreliable, low overhead, just shoots data into the socket we are listening at. 

My doubts are how exactly is UDP implemented in actual servers, ive heard of websockets, but it seems we have missed that information, was looking forward to implement websockets in hand
