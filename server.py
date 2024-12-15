import socket
import signal
import sys
import json

# Constants
CONNECT_REQUESTS = 5
BUFFER_SIZE = 1024

def start_server(port):
    """Start the HTTP server."""
    
    # Create the server socket
    server_socket = create_server_socket(port)
    
    # Setup signal handler for graceful shutdown
    setup_shutdown_handler(server_socket)
    
    # Start accepting client connections
    accept_connections(server_socket)

def create_server_socket(port):
    """Create and bind the server socket."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', port))
    server_socket.listen(CONNECT_REQUESTS)
    print(f"...::: Server listening on port {port} :::...\n")
    print(" -> Press Ctrl+C to shut down the server.\n")
    return server_socket

def setup_shutdown_handler(server_socket):
    """Set up the shutdown handler for SIGINT (Ctrl+C)."""
    def shutdown_server(signal, frame):
        """Gracefully shuts down the server."""
        print("\nShutting down the server...")
        server_socket.close()
        sys.exit(0)
    
    # Handle SIGINT (Ctrl+C) to gracefully shutdown the server
    signal.signal(signal.SIGINT, shutdown_server)

def accept_connections(server_socket):
    """Accept and handle incoming client connections."""
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection established from {client_address}")
        
        handle_request(client_socket)

def handle_request(client_socket):
    """Handle the HTTP request from the client."""
    try:
        request = receive_request(client_socket)
        if request:
            first_line = get_first_line(request)
            print(f"First line of request: {first_line}")
            
            if first_line.startswith('GET'):
                response = handle_get_request()
            else:
                response = handle_error("405 Method Not Allowed", "Only GET method is allowed.")
            
            send_response(client_socket, response)
    except Exception as e:
        print(f"Error processing request: {e}")
    finally:
        client_socket.close()

def receive_request(client_socket):
    """Receive the HTTP request from the client."""
    request = client_socket.recv(BUFFER_SIZE).decode('utf-8')
    print(f"Request:\n{request}")
    return request

def get_first_line(request):
    """Extract and return the first line of the request."""
    return request.splitlines()[0] if request else ""

def handle_get_request():
    """Generate the response for a GET request."""
    response_body = json.dumps({"message": "Hello, World!"})
    response = 'HTTP/1.1 200 OK\r\n'
    response += 'Content-Type: application/json\r\n'
    response += f'Content-Length: {len(response_body)}\r\n'
    response += '\r\n'
    response += response_body
    return response

def handle_error(status_code, message):
    """Generate an error response."""
    error_response = {
        "error": status_code,
        "message": message
    }
    response_body = json.dumps(error_response)
    response = f'HTTP/1.1 {status_code}\r\n'
    response += 'Content-Type: application/json\r\n'
    response += f'Content-Length: {len(response_body)}\r\n'
    response += '\r\n'
    response += response_body
    return response

def send_response(client_socket, response):
    """Send the HTTP response to the client."""
    client_socket.sendall(response.encode('utf-8'))

if __name__ == "__main__":
    # Start the server on port 8080
    start_server(8080)
