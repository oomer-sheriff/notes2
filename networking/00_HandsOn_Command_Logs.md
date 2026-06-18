# Hands-On Command & Output Logs

This document serves as an archive for all the terminal commands and scripts run during our networking curriculum, along with their actual outputs and the engineering insights we drew from them.

---

## 1. Mapping Your Own Machine (`ipconfig /all`)
**Purpose:** Discovers the machine's permanent MAC (Physical) address and temporary IP (Logical) address.

**Output:**
```text
Windows IP Configuration

Ethernet adapter Ethernet:
   Description . . . . . . . . . . . : Realtek PCIe GbE Family Controller
   Physical Address. . . . . . . . . : 7C-8A-E1-C3-0D-38
   DHCP Enabled. . . . . . . . . . . : Yes
   IPv4 Address. . . . . . . . . . . : 192.168.1.6(Preferred) 
   Subnet Mask . . . . . . . . . . . : 255.255.255.0
   Default Gateway . . . . . . . . . : 192.168.1.1
   DNS Servers . . . . . . . . . . . : 218.248.112.65
                                       218.248.90.5
```

**Insight:** Your router (`192.168.1.1`) assigned your machine the IP `192.168.1.6` via DHCP. Your permanent physical MAC address is `7C-8A-E1-C3-0D-38`.

---

## 2. Address Resolution Protocol (`arp -a`)
**Purpose:** Views the local machine's ARP table, which is a cached map of `IP Address -> MAC Address` for devices on the same LAN.

**Output:**
```text
Interface: 192.168.1.6 --- 0xe
  Internet Address      Physical Address      Type
  192.168.1.1           8c-13-e2-57-40-94     dynamic   
  192.168.1.255         ff-ff-ff-ff-ff-ff     static    
```

**Insight:** To send a packet to your router (`192.168.1.1`), your computer must wrap the IP packet in a physical Ethernet frame addressed to the router's physical MAC address (`8c-13-e2-57-40-94`).

---

## 3. ICMP Echo Test (`ping 192.168.1.1`)
**Purpose:** Tests end-to-end network connectivity to a specific IP using the ICMP protocol.

**Output:**
```text
Pinging 192.168.1.1 with 32 bytes of data:
Reply from 192.168.1.1: bytes=32 time=1ms TTL=64
Reply from 192.168.1.1: bytes=32 time<1ms TTL=64
Reply from 192.168.1.1: bytes=32 time<1ms TTL=64
Reply from 192.168.1.1: bytes=32 time<1ms TTL=64

Ping statistics for 192.168.1.1:
    Packets: Sent = 4, Received = 4, Lost = 0 (0% loss)
```

---

## 4. Raw TCP Socket Handshake (Python)
**Purpose:** Demonstrates the blocking, reliable, connection-oriented nature of TCP and the 3-Way Handshake.

**Server Output:**
```text
[*] TCP Server is listening on 127.0.0.1:65432
[+] 3-Way Handshake Complete! Connection established with ('127.0.0.1', 53924)
[*] Received data: Hello TCP Server, are you there?
```

**Client Output:**
```text
[*] Initiating TCP 3-Way Handshake with 127.0.0.1:65432...
[+] Handshake successful! Connected.
[*] Received response: Hello from TCP Server! Your message was safely received.
```

**Insight:** The server was manually bound to port `65432`. However, the OS dynamically assigned the ephemeral port `53924` to the client script to establish the connection!

---

## 5. Raw UDP Datagram Blast (Python)
**Purpose:** Demonstrates the connectionless, "fire and forget" nature of UDP.

**Client Output:**
```text
[*] Notice we DO NOT call connect(). There is no handshake.
[*] We are just blasting the packet into the void and hoping it gets there!
[*] Received response from ('127.0.0.1', 65433): UDP Server got your blast!
```

---

## 6. Internal Routing Table (`route print`)
**Purpose:** Views the logic the computer uses to decide where to send outgoing packets based on Longest Prefix Match (LPM).

**Output:**
```text
IPv4 Route Table
===========================================================================
Active Routes:
Network Destination        Netmask          Gateway       Interface  Metric
          0.0.0.0          0.0.0.0      192.168.1.1      192.168.1.6     25
      192.168.1.0    255.255.255.0         On-link       192.168.1.6    281
```

**Insight:** The `0.0.0.0` rule is the "Catch-All" Default Route. If your computer doesn't know a specific route for an IP, it defaults to sending it out via interface `192.168.1.6` straight to your router (`192.168.1.1`).

---

## 7. Mapping The Internet (`tracert github.com`)
**Purpose:** Maps the physical, hop-by-hop router path a packet takes to reach a destination across the globe.

**Output:**
```text
Tracing route to github.com [20.207.73.82]
over a maximum of 30 hops:

  1    <1 ms    <1 ms    <1 ms  192.168.1.1 
  2     2 ms     3 ms     1 ms  59.182.208.1 
  3     5 ms     5 ms     5 ms  10.219.28.102 
  4     *        *        *     Request timed out.
  ... (Hops 5-12 Timed out due to ICMP drops by enterprise routers)
 13    17 ms    21 ms    16 ms  ae77-0.ier03.maa02.ntwk.msn.net [104.44.6.101] 
 14    18 ms     *        *     be22.rwa01.maa37.ntwk.msn.net [51.10.38.154] 
 15    31 ms    32 ms    32 ms  be1011.owr02.maa37.ntwk.msn.net [51.10.23.219] 
 16    32 ms     *        *     be9.ibr02.pnq21.ntwk.msn.net [51.10.26.232] 
 17    32 ms    34 ms    32 ms  ae122-0.rwa02.pnq21.ntwk.msn.net [104.44.11.254] 
 ...
 22    32 ms    32 ms    33 ms  20.207.73.82 
```

**Insight:** 
- Hop 1: Home router (NAT occurs here).
- Hop 2: Your ISP Gateway.
- Hop 13: The packet hits the Microsoft Azure network (`msn.net`) at a data center in **Chennai** (`maa` airport code).
- Hop 17: The packet travels over Microsoft's internal fiber backbone to **Pune** (`pnq` airport code).
- Hop 22: Arrives safely at the GitHub server!
