from http.server import SimpleHTTPRequestHandler
import socketserver


FILE_SRV_PORT = 7676

class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

with socketserver.TCPServer(("", FILE_SRV_PORT), CORSRequestHandler) as httpd:
    print(f'Serving at port {FILE_SRV_PORT}')
    httpd.serve_forever()
