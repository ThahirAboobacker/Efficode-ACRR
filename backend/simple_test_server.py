"""
Simple test server for EFFICODE-ACRR
"""
import http.server
import socketserver
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

PORT = 8080
FIXED_RESPONSE = {
    "status": "success",
    "original_code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
    "optimized_code": "def fibonacci(n):\n    \"\"\"Efficient implementation of Fibonacci using dynamic programming\"\"\"\n    if n <= 0:\n        return 0\n    elif n == 1:\n        return 1\n    # Use dynamic programming approach\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
    "original_complexity": "O(2^n)",
    "optimized_complexity": "O(n)",
    "explanation": "Optimizations applied: Replaced recursive Fibonacci with optimized dynamic programming implementation",
    "processing_time": 0.1,
    "timestamp": 1712507632103,
    "improvements": [
        {
            "rule": "replace_recursive_fibonacci",
            "description": "Replace recursive Fibonacci with optimized dynamic programming implementation",
            "category": "algorithm"
        }
    ]
}

class CORSRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-Type, Accept')
        super().end_headers()
    
    def log_message(self, format, *args):
        logging.info("%s - %s" % (self.address_string(), format % args))
    
    def do_OPTIONS(self):
        logging.info("OPTIONS request received")
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        logging.info(f"GET request received: {self.path}")
        if self.path == '/health' or self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            health_response = json.dumps({
                "status": "healthy",
                "optimizer": "available",
                "version": "1.0.0"
            })
            logging.info(f"Returning health response: {health_response}")
            self.wfile.write(health_response.encode())
        else:
            super().do_GET()
    
    def do_POST(self):
        logging.info(f"POST request received: {self.path}")
        if self.path == '/optimize' or self.path == '/api/optimize':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request_json = json.loads(post_data.decode('utf-8'))
                logging.info(f"Request data: {request_json}")
                
                # Send the fixed response regardless of input
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                # Use the input code in the response
                response = FIXED_RESPONSE.copy()
                response["original_code"] = request_json.get("code", response["original_code"])
                logging.info(f"Sending response with length: {len(json.dumps(response))}")
                
                response_json = json.dumps(response)
                logging.info(f"Response first 100 chars: {response_json[:100]}...")
                
                self.wfile.write(response_json.encode())
                logging.info("Response sent successfully")
            except json.JSONDecodeError as e:
                logging.error(f"JSON decode error: {e}")
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = json.dumps({
                    "status": "error",
                    "error": f"Invalid JSON: {str(e)}"
                })
                self.wfile.write(error_response.encode())
            except Exception as e:
                logging.error(f"Error processing request: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                error_response = json.dumps({
                    "status": "error",
                    "error": f"Server error: {str(e)}"
                })
                self.wfile.write(error_response.encode())
        else:
            logging.warning(f"Unknown path: {self.path}")
            self.send_response(404)
            self.end_headers()

def run_server():
    logging.info(f"Starting server on port {PORT}")
    
    # Use ThreadingTCPServer for better concurrency
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("", PORT), CORSRequestHandler) as httpd:
        logging.info(f"Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped by user")
        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            httpd.server_close()
            logging.info("Server closed")

if __name__ == "__main__":
    run_server() 