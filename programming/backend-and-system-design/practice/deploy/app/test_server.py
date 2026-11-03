import json, os, signal, subprocess, sys, time, unittest, urllib.error, urllib.request
from pathlib import Path

PORT = "18099"
BASE = f"http://127.0.0.1:{PORT}"


def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=5) as reply:
            return reply.status, json.load(reply)
    except urllib.error.HTTPError as err:
        return err.code, json.load(err)


class ServerTest(unittest.TestCase):
    def setUp(self):
        env = dict(os.environ, PORT=PORT, DRAIN_SECONDS="0.1")
        self.proc = subprocess.Popen([sys.executable, str(Path(__file__).with_name("server.py"))],
                                     env=env, stdout=subprocess.PIPE, text=True)
        self.proc.stdout.readline()

    def tearDown(self):
        self.proc.kill()
        self.proc.wait()
        self.proc.stdout.close()

    def test_probes(self):
        self.assertEqual(get("/healthz"), (200, {"status": "alive"}))
        self.assertEqual(get("/readyz"), (200, {"ready": True}))
        self.assertEqual(get("/nope")[0], 404)

    def test_sigterm_finishes_running_request(self):
        import threading
        result = {}
        thread = threading.Thread(target=lambda: result.update(r=get("/slow?ms=600")))
        thread.start()
        time.sleep(0.2)
        self.proc.send_signal(signal.SIGTERM)
        thread.join()
        self.assertEqual(result["r"], (200, {"done": True}))
        self.assertEqual(self.proc.wait(timeout=5), 0)


if __name__ == "__main__":
    unittest.main()
