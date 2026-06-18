# Level 4: The Abyss (Application Layer & Infrastructure)

We've laid the plumbing. We know how to establish a TCP connection across the globe and route an IP packet through 22 different routers. But humans don't type `20.207.73.82` into their browsers. They type `github.com`. 

Welcome to the **Application Layer (Layer 7)**, where the infrastructure finally interfaces with human-readable text.

## 1. DNS: The Internet's Phonebook

DNS (Domain Name System) translates human-readable domain names into machine-readable IP addresses.

### Deep Dive: DNS Caching (TTL) and UDP
DNS predominantly runs over **UDP Port 53**. Why? Because UDP is incredibly fast (no 3-way handshake overhead), and DNS queries are usually small enough to fit inside a single UDP packet!
When your computer needs an IP, it first checks its **Local Cache**. If it misses, it queries your ISP's **Recursive DNS Resolver**.

The Recursive Resolver then does the hard work (Iterative Queries):
1. **Root Name Servers:** It asks the root server, "Who handles `.com`?"
2. **TLD Name Servers:** The root points it to the Top Level Domain (TLD) server. It asks the `.com` server, "Who handles `github.com`?"
3. **Authoritative Name Servers:** The `.com` server points it to GitHub's own DNS server (A Zone File). The resolver asks, "What is the IP for `github.com`?" 
4. The Authoritative Server returns `20.207.73.82` along with a **TTL (Time to Live)** value in seconds (e.g., 3600).
5. The Recursive Resolver and your computer cache this IP for exactly 3600 seconds so they don't have to do this expensive lookup again for an hour!

### Common DNS Records
- **A Record:** Maps a name to an IPv4 address.
- **AAAA Record:** Maps a name to an IPv6 address.
- **CNAME:** Maps a name to another name (an alias). E.g., `www.github.com` might just point to `github.com`.
- **NS Record:** Points to the Authoritative Name Server for a domain.

---

## 2. DHCP: The Dynamic Host Configuration Protocol

When you connected to your Wi-Fi, how did your laptop automatically know its IP (`192.168.1.6`), its Subnet Mask, its Default Gateway, and its DNS servers? It used DHCP!

DHCP uses the **DORA Process** (broadcast over the LAN):
1. **Discover:** Client shouts, "Is there a DHCP server here? I need an IP!"
2. **Offer:** Router replies, "I am here! I can offer you `192.168.1.6`."
3. **Request:** Client says, "Awesome, I formally request to lease `192.168.1.6`."
4. **Acknowledge:** Router says, "Granted! You have this IP leased for 7 days."

---

## 3. HTTP, HTTPS, and the TLS Handshake

Once DNS gives you the IP, your computer performs the **TCP 3-Way Handshake** on Port 80 (HTTP) or Port 443 (HTTPS).

### Deep Dive: Advanced HTTP Headers
HTTP is a stateless, text-based protocol. You literally send plain text over the TCP socket.
```http
GET / HTTP/1.1
Host: github.com
User-Agent: Mozilla/5.0
Connection: keep-alive
Cookie: session_id=12345
```
Because HTTP is strictly stateless, servers use headers to maintain "State" across different requests:
- **`Set-Cookie` / `Cookie`:** The server sends a token, and your browser automatically attaches it to every future request so you stay "logged in".
- **`Connection: keep-alive`:** Normally, early HTTP closed the TCP socket after 1 request. Keep-Alive tells the server to hold the TCP socket open so the browser can download multiple images without constantly waiting on new 3-way handshakes!
- **`Access-Control-Allow-Origin` (CORS):** A crucial security header enforced by web browsers that prevents a malicious website from making background API requests to your bank account's domain.

### Deep Dive: TLS 1.3 and Diffie-Hellman Ephemeral
Because HTTP is plain text, anyone sniffing the network (or any router along the path) can read your passwords. HTTPS wraps the HTTP payload in TLS encryption.

**The TLS Handshake happens *after* the TCP Handshake:**
1. **ClientHello:** Client sends supported cipher suites.
2. **ServerHello & Certificate:** Server picks a cipher and sends its SSL Certificate (cryptographically signed by a Certificate Authority to prove it's the real GitHub).
3. **Key Exchange (Diffie-Hellman Ephemeral):** This is pure mathematical magic. The client and server exchange public numbers over the insecure network. Using modular arithmetic, they both independently calculate the *exact same symmetric encryption key* (AES-256) without ever actually sending the key over the wire!
4. **Perfect Forward Secrecy:** Because they generate a new, random symmetric key for every session (Ephemeral), even if a hacker records years of your encrypted traffic and steals the server's master private key tomorrow, they cannot decrypt your past sessions!

---

## 4. Load Balancing & Reverse Proxies

GitHub doesn't run on one single server. It runs on thousands.
When you hit `20.207.73.82`, you aren't hitting the database. You are hitting a **Reverse Proxy** or **Load Balancer** (like Nginx, HAProxy, or an AWS Application Load Balancer).

- **Layer 4 Load Balancing (TCP/UDP):** The load balancer doesn't look at the HTTP text at all. It just blindly forwards raw TCP packets to backend servers based on IP/Port. It is incredibly fast but "dumb".
- **Layer 7 Load Balancing (HTTP Reverse Proxies):** The load balancer actually terminates the TCP connection, decrypts the TLS, and reads the raw HTTP headers. It can make smart routing decisions (e.g., "If the URL is `/images`, send it to Backend-A; if `/api`, send it to Backend-B"). Nginx and HAProxy excel here.

---

## Next Steps: Hands-on

For Level 4 hands-on, we are going to:
1. Act as a manual DNS resolver using `nslookup`.
2. Connect to a web server manually via Telnet/Curl to see the raw HTTP headers in plaintext!

Let me know when you've reviewed the notes!
