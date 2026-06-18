import socket

# 1. Create a socket object
# AF_INET = IPv4 address family
# SOCK_STREAM = TCP (Connection-oriented, Reliable)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 2. Bind the socket to a specific IP and Port
HOST = '127.0.0.1' # Localhost (only visible to your machine)
PORT = 65432       # Arbitrary non-privileged port (above 1023)
server_socket.bind((HOST, PORT))

# 3. Listen for incoming connections
# The parameter '1' specifies the backlog of unaccepted connections
server_socket.listen(1)
print(f"[*] TCP Server is listening on {HOST}:{PORT}")

# 4. Accept a connection
# THIS BLOCKS! The program pauses here until a client completes the 3-Way Handshake
conn, addr = server_socket.accept()
print(f"[+] 3-Way Handshake Complete! Connection established with {addr}")

# 5. Read data and send a response
with conn:
    while True:
        data = conn.recv(1024) # Receive up to 1024 bytes
        if not data:
            break
        print(f"[*] Received data: {data.decode()}")
        conn.sendall(b"Hello from TCP Server! Your message was safely received.")
