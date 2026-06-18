import socket

HOST = '127.0.0.1'
PORT = 65432

# 1. Create a socket object (IPv4, TCP)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print(f"[*] Initiating TCP 3-Way Handshake with {HOST}:{PORT}...")

# 2. Connect to the server 
# Under the hood, this triggers the SYN -> SYN-ACK -> ACK packet sequence!
client_socket.connect((HOST, PORT))
print("[+] Handshake successful! Connected.")

# 3. Send data reliably
message = "Hello TCP Server, are you there?"
client_socket.sendall(message.encode())

# 4. Receive response
data = client_socket.recv(1024)
print(f"[*] Received response: {data.decode()}")

# 5. Close connection
client_socket.close()
