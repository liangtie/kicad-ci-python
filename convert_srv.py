from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess
import uuid
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import urlparse, parse_qs

from convert_glb import export_glb

# Directory to save files
SAVE_DIR = "D:/kicad-cli-python"
KICAD_IMG_ID = "a37c2763212f"
KICAD_IMG_HOME_PATH = "/home/kicad"
SERVER_URL = "http://192.168.50.2:8000/"  # Change the URL as per your server configuration

class FileUploadHandler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        # Read JSON content from request
        json_data = self.rfile.read(content_length)
        # Parse JSON data
        try:
            json_obj = json.loads(json_data)
            file_content = json_obj.get('pcb_content', '')

        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON data')
            return

        # Generate a random filename
        filename = str(uuid.uuid4()) + '.' + 'kicad_pcb'
        # Save the file
        file_path =SAVE_DIR +"/" + filename

        try:
            with open(file_path, "w", encoding="gbk") as f:
                f.write(file_content)
        except UnicodeEncodeError:
            # Handle the exception here, for example:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file_content.encode("utf-8", errors="ignore").decode("utf-8"))


        # Export GLB
        glb_file_path = export_glb(file_path)

        # Send response with URL
        if glb_file_path:
            glb_filename = os.path.basename(glb_file_path)
            response_data = {
                'url': SERVER_URL + glb_filename
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')  # Allow POST requests
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')  # Allow Content-Type header
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

    def do_GET(self):
        if self.path.startswith('/download_glb?url='):
            self.download_glb()
        else:
            self._set_headers(404)  # Not Found

    def download_glb(self):
        query_components = parse_qs(urlparse(self.path).query)
        if 'url' in query_components:
            glb_url = query_components['url'][0]
            try:
                response = requests.get(glb_url)
                if response.status_code == 200:
                    self._set_headers(200, 'application/octet-stream')
                    self.wfile.write(response.content)
                else:
                    self._set_headers(404)  # Not Found
                    self.wfile.write(b"File not found")
            except Exception as e:
                self._set_headers(500)  # Internal Server Error
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self._set_headers(400)  # Bad Request
            self.wfile.write(b"URL parameter is missing")          

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        


def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, FileUploadHandler)
    print(f'Starting server on port {port}')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server(8989)
