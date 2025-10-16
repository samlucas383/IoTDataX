from http.server import BaseHTTPRequestHandler, HTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'Hello, World!')


def run(host='0.0.0.0', port=8000):
    server = HTTPServer((host, port), Handler)
    print(f'Serving HTTP on {host}:{port} ...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nShutting down')
        server.server_close()


if __name__ == '__main__':
    run()
