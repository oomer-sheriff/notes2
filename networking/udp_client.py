import socket

HOST = '127.0.0.1'
PORT = 65434

# 1. Create a socket object (IPv4, UDP)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("[*] Notice we DO NOT call connect(). There is no handshake.")
print("[*] We are just blasting the packet into the void and hoping it gets there!")

message = "Hello UDP Server, catch this datagram!"

# 2. Send data directly to the target address
client_socket.sendto(message.encode(), (HOST, PORT))

# 3. Try to receive a response 
# Since UDP is unreliable, the packet might have been lost!
# It is best practice to set a timeout so we don't hang forever.
client_socket.settimeout(2.0)
try:
    data, server = client_socket.recvfrom(1024)
    print(f"[*] Received response from {server}: {data.decode()}")
except socket.timeout:
    print("[-] Request timed out. Packet was lost or server didn't reply.")

client_socket.close()
