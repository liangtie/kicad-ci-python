from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import uuid
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from convert_altium import convert_kicad_to_ad
import cgi

from convert_glb import export_glb
from get_local_ip import get_local_ip

# Directory to save files
CURRENT_SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
KICAD_IMG_ID = "a37c2763212f"
KICAD_IMG_HOME_PATH = "/home/kicad"
SERVER_URL = f"http://{get_local_ip()}:8000/"  # Change the URL as per your server configuration

class FileUploadHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        if self.path == '/convert_pcb_to_glb':

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
            file_path =CURRENT_SCRIPT_DIR +"/" + filename

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

        elif self.path == '/convert_ad_to_kicad':
            content_type, pdict = cgi.parse_header(self.headers['content-type'])
            if content_type == 'multipart/form-data':
                pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
                form = cgi.parse_multipart(self.rfile, pdict)
                files = form.get('files')

                if not files:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b"No files provided")
                    return

                saved_files = []
                for file_item in files:
                    filename = file_item.filename
                    if not filename:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(b"One or more files have an empty filename")
                        return

                    file_path = os.path.join(CURRENT_SCRIPT_DIR, filename)
                    with open(file_path, 'wb') as output_file:
                        output_file.write(file_item.file.read())

                    saved_files.append(filename)

                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"message": "Files successfully uploaded", "files": saved_files}
                self.wfile.write(bytes(json.dumps(response), 'utf-8'))
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Content-Type must be multipart/form-data")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")




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
