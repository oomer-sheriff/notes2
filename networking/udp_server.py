import socket

# 1. Create a socket object
# AF_INET = IPv4
# SOCK_DGRAM = UDP (Connectionless, Unreliable, Fast)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 2. Bind the socket to an IP and Port
HOST = '127.0.0.1'
PORT = 65434
server_socket.bind((HOST, PORT))

print(f"[*] UDP Server is active on {HOST}:{PORT}")
print("[*] Notice there is no 'listen()' or 'accept()'. We just wait for datagrams.")

# 3. Receive data indefinitely
while True:
    # recvfrom returns the data AND the address of whoever blasted it at us
    data, addr = server_socket.recvfrom(1024)
    print(f"[*] Received datagram from {addr}: {data.decode()}")
    
    # Send a reply back to the sender
    server_socket.sendto(b"UDP Server got your blast!", addr)
