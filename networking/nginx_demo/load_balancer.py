import socket
import threading

# The pool of backend worker servers
BACKENDS = [('127.0.0.1', 8001), ('127.0.0.1', 8002)]
current_backend = 0

def handle_client(client_socket):
    global current_backend
    
    # ALGORITHM: Round-Robin Load Balancing
    # This ensures traffic is split 50/50 exactly!
    backend_addr = BACKENDS[current_backend]
    current_backend = (current_backend + 1) % len(BACKENDS)
    
    print(f"[*] Load Balancer actively routing request to -> Port {backend_addr[1]}")
    
    try:
        # 1. Receive the raw HTTP GET request from the client (curl)
        request = client_socket.recv(4096)
        
        # 2. Open a new socket connection to the chosen backend server
        backend_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backend_socket.connect(backend_addr)
        
        # 3. Forward the exact raw HTTP request
        backend_socket.sendall(request)
        
        # 4. Receive the HTTP response from the backend and forward it
        while True:
            response = backend_socket.recv(4096)
            if not response:
                break
            # 5. Send it back to the original client
            client_socket.sendall(response)
        
        backend_socket.close()
    except Exception as e:
        print(f"[-] Error routing traffic: {e}")
    finally:
        client_socket.close()

def main():
    # Set up the Reverse Proxy to listen on Port 8080
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    proxy_socket.bind(('127.0.0.1', 8080))
    proxy_socket.listen(5)
    
    print("[*] Python Reverse Proxy (Nginx Clone) listening on port 8080...")
    print("[*] Forwarding traffic to backends on ports 8001 and 8002 via Round-Robin.")
    
    while True:
        client, addr = proxy_socket.accept()
        # Handle each connection concurrently in a new thread
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()

if __name__ == "__main__":
    main()
