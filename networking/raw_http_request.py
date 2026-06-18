import socket

# 1. Open a raw TCP Socket (What we learned in Level 2)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Connect to example.com on Port 80 (HTTP)
print("[*] Connecting to example.com on Port 80 (TCP)...")
s.connect(('example.com', 80))

# 3. Create the raw HTTP GET Request as a plain text string (What we learned in Level 4)
# Notice the \r\n (Carriage Return + Line Feed) required by the HTTP standard!
http_request = (
    "GET / HTTP/1.1\r\n"
    "Host: example.com\r\n"
    "User-Agent: Raw-Python-Socket\r\n"
    "Connection: close\r\n\r\n"
)

# 4. Send the text over the TCP socket
print("[*] Sending raw HTTP text:\n---")
print(http_request.strip())
print("---\n")
s.sendall(http_request.encode('utf-8'))

# 5. Receive the server's HTTP text response
response = s.recv(4096)
print("[*] Received Response from Server:\n---")
print(response.decode('utf-8'))
print("---")

s.close()
