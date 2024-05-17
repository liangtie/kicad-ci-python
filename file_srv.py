from http.server import SimpleHTTPRequestHandler
import socketserver

from utils import FILE_SRV_PORT



class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

with socketserver.TCPServer(("", FILE_SRV_PORT), CORSRequestHandler) as httpd:
    print(f'Serving at port {FILE_SRV_PORT}')
    httpd.serve_forever()
