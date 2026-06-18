import os
from http.server import BaseHTTPRequestHandler, HTTPServer

# Grab the server name from the environment variables (set in docker-compose)
SERVER_NAME = os.getenv("SERVER_NAME", "Unknown Backend")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Send HTTP 200 OK Status Code
        self.send_response(200)
        
        # 2. Send HTTP Headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Nginx will inject 'X-Real-IP' into the headers so the backend knows the true client IP
        # Otherwise, the backend would think every request was coming from the Nginx server!
        client_ip = self.headers.get('X-Real-IP', self.client_address[0])
        
        # 3. Send HTTP Payload (HTML)
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
                .box {{ background: white; padding: 40px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; }}
                .ip {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="box">
                <h1>Hello from {SERVER_NAME}!</h1>
                <p>Nginx received your request and routed it to me.</p>
                <p>Your Original IP Address: <span class="ip">{client_ip}</span></p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('0.0.0.0', port), RequestHandler)
    print(f"[*] {SERVER_NAME} listening on port {port}...")
    server.serve_forever()
