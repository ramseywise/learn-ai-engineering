"""A small service that shuts down without dropping requests. Standard library only."""
import json, os, signal, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT = int(os.environ.get("PORT", "8080"))
DRAIN_SECONDS = float(os.environ.get("DRAIN_SECONDS", "1"))   # config comes from the environment
ready = threading.Event()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/healthz":                     # liveness: is this process stuck?
            self.reply(200, {"status": "alive"})
        elif url.path == "/readyz":                    # readiness: should it get traffic now?
            self.reply(200 if ready.is_set() else 503, {"ready": ready.is_set()})
        elif url.path == "/slow":
            time.sleep(int(parse_qs(url.query).get("ms", ["100"])[0]) / 1000)
            self.reply(200, {"done": True})
        else:
            self.reply(404, {"error": "not found"})

    def reply(self, code, body):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        if not ready.is_set():
            self.send_header("Connection", "close")    # tell keep-alive clients to reconnect elsewhere
            self.close_connection = True
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_):
        pass


class Server(ThreadingHTTPServer):
    daemon_threads = False                             # server_close() waits for in-flight handlers
    block_on_close = True


def main():
    server = Server(("0.0.0.0", PORT), Handler)

    def on_term(signum, frame):
        ready.clear()                                  # 1. fail readiness so the balancer moves on
        def drain():
            time.sleep(DRAIN_SECONDS)                  # 2. allow time for the balancer to notice
            server.shutdown()                          # 3. stop accepting new connections
        threading.Thread(target=drain).start()

    signal.signal(signal.SIGTERM, on_term)
    ready.set()
    print(f"serving on {PORT}", flush=True)
    server.serve_forever()
    server.server_close()                              # 4. wait for requests already running
    print("drained, exiting", flush=True)


if __name__ == "__main__":
    main()
