# Level 1: The Tip of the Iceberg (Foundations)

Welcome to the start of your networking journey! We're beginning with the absolute basics, but we'll look at them through an engineering lens. 

## 1. What is a Network?
At its core, a network is simply two or more computers connected together to share resources (data, printers, internet access).
When you write a distributed system or microservices architecture, you are fundamentally relying on a network to pass messages. If the network is slow or fails, your code fails. This is known as the *Fallacies of Distributed Computing* (e.g., assuming the network is reliable, latency is zero, and bandwidth is infinite).

### Types of Networks (Scope)
- **LAN (Local Area Network):** Devices in a single physical location (your home, a single office building). They usually share the same routing equipment and IP subnet. Speeds are typically very high (1Gbps to 10Gbps+).
- **MAN (Metropolitan Area Network):** Spans a city or a large campus.
- **WAN (Wide Area Network):** Spans large geographic areas. This involves renting leased lines or VPNs over the public internet to connect multiple LANs together.
- **The Internet:** The ultimate WAN. A massive "network of networks" interconnected globally.

---

## 2. The Addresses of the Web: MAC vs. IP

Just like you need an address to send a physical letter, computers need addresses to send data packets. There are two types of addresses every networked computer uses simultaneously:

### MAC Address (Media Access Control)
- **What is it?** A physical, permanent address "burned" into your Network Interface Card (NIC) by the manufacturer.
- **Format:** 48 bits, usually represented as 6 pairs of hexadecimal digits (e.g., `00:1A:2B:3C:4D:5E`).
- **Scope:** ONLY used for communication *within the same local network (LAN)*. 
- **Analogy:** Your Social Security Number (or National ID). It uniquely identifies *who* you are, permanently, regardless of where you move.

### IP Address (Internet Protocol)
- **What is it?** A logical, temporary address assigned to your device by the network you connect to. 
- **Format:** (IPv4) 32 bits, represented as 4 numbers between 0-255 (e.g., `192.168.1.5`).
- **Scope:** Used for communication *across different networks (routing)*.
- **Analogy:** Your home mailing address. It identifies *where* you are currently located. If you move from your house to a coffee shop, your MAC address stays the same, but your IP address changes to match the coffee shop's network.

> **Engineering Insight:** Why both? When your computer wants to talk to a Google server, it uses the IP address to route the packet across the world. However, to actually push the electrical signal out of your computer and onto your home router, it uses the router's MAC address at the physical layer.

### Deep Dive: Address Resolution Protocol (ARP)
How does your computer actually know the physical MAC address of your router? It uses ARP. 
1. Your computer blasts a **Broadcast Ethernet Frame** to the special MAC address `FF:FF:FF:FF:FF:FF`. Every single device on the local network physically receives this.
2. The payload says: *"Who has IP 192.168.1.1? Tell 192.168.1.6."*
3. The router receives it, realizes it owns that IP, and replies with a **Unicast Frame** directly back to your MAC address: *"I have 192.168.1.1, and my MAC is 8C:13:E2:57:40:94."*
Your computer caches this in its ARP Table so it doesn't have to broadcast every time.

---

## 3. Physical & Data Link Devices

How do we actually connect these devices together? We use specialized hardware. Understanding the difference between these three is crucial.

### Hub (Layer 1 - Physical)
- **How it works:** A dumb device. When an electrical signal comes in one port, the hub simply copies and blasts it out of *all* other ports.
- **The Problem:** It causes massive traffic collisions and is highly insecure (anyone can sniff everyone else's traffic). You won't find these used in modern networks.

### Switch (Layer 2 - Data Link)
- **How it works:** A smart device. It actively learns the **MAC Addresses** of every computer plugged into it by inspecting the Source MAC of incoming frames.
- **The Advantage:** It isolates collision domains. When Computer A talks to B, the switch sends the signal *only* to B's port. This allows **Full-Duplex** communication (computers can send and receive simultaneously without collisions).

### Deep Dive: CSMA/CD and The Ethernet Frame
In the old days of Hubs, networks were **Half-Duplex** (only one device could talk at a time). If two talked, the voltages collided on the copper wire resulting in corrupt data. Networks used **CSMA/CD** (Carrier-Sense Multiple Access with Collision Detection):
1. **Listen:** Is the wire silent?
2. **Talk:** Send the data.
3. **Detect:** If a collision happens, broadcast a jam signal, wait a random exponential backoff time, and retry.

When data is sent over the wire, it is structured mathematically as an **Ethernet Frame**:
1. **Preamble (8 bytes):** Alternating 1s and 0s to synchronize receiver clocks.
2. **Destination MAC (6 bytes):** Where it's going.
3. **Source MAC (6 bytes):** Where it's from.
4. **EtherType (2 bytes):** What protocol is inside (e.g., IPv4 is 0x0800).
5. **Payload (46-1500 bytes):** The actual IP Packet.
6. **FCS (Frame Check Sequence, 4 bytes):** A CRC-32 mathematical checksum. If electrical interference flipped a bit on the wire, the checksum fails and the frame is instantly dropped.

### Router (Layer 3 - Network)
- **How it works:** Connects *different* networks together (e.g., connects your home LAN to the ISP's WAN). 
- **The Advantage:** It looks at the **IP Addresses** of packets to determine the best path to send them to their final destination across the globe. 

> **Wait, my home box does all of this?** 
> Yes! The box your ISP gave you is actually a 3-in-1 combo device. It contains a **Router** (connecting your home to the internet), a **Switch** (the 4 ethernet ports on the back connecting local devices), and a **Wireless Access Point** (allowing Wi-Fi connections).

---

## Next Steps
Now that we have the theory, let's get our hands dirty in the terminal. Read through this, and when you're ready, let me know! We will map out your local network using some command-line tools.


my notes:

damn pretty cool, so router connects isp wans and my lan together, switch is smart device that knows which device is connected to which port and sends messages properly, and hub is dumb broadcaster


ip address is dynamic, keeps changing according to location and is given to us by the router, mac address is fixed, given by manufacturer.

lan is local area network, wan is wide area network, this is how they are connected

my router at home does all three, it is a 3 in 1 device that contains a router, switch and a wireless access point