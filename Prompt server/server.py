from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import subprocess

HOST = '0.0.0.0'
PORT = 8000

class SimpleServer(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        raw_data = self.rfile.read(content_length)
        data = json.loads(raw_data.decode('utf-8'))

        if self.path == '/generate':
            content = data.get("content", "")
            prompt_input = f"Act like a vulnerability researcher. Generate a prompt to test for {content} vulnerability."

            try:
                result = subprocess.run(
                    ["ollama", "run", "llama2-uncensored"],
                    input=prompt_input.encode(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=30
                )
                generated_prompt = result.stdout.decode().strip()
                self._send_json({"prompt": generated_prompt})
            except Exception as e:
                self._send_json({"error": str(e)})

        elif self.path == '/feedback':
            self._send_json({"message": "Feedback received."})

        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data):
        response = json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response)

if __name__ == '__main__':
    server = HTTPServer((HOST, PORT), SimpleServer)
    print(f"Prompt server running at http://{HOST}:{PORT}")
    server.serve_forever()
