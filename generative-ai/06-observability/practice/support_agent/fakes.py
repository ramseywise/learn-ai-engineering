"""Local stand-ins for the two services the chapters talk to.

`fake_langfuse` answers the parts of the Langfuse REST API the SDK calls. `offline_langfuse`
wires it to a real SDK client through an in-memory transport and span exporter, so the real
SDK code runs with nothing leaving the machine. `serve` puts the same fake and a Messages API
fake on localhost, so blocks marked `# illustrative` can run unedited with
ANTHROPIC_BASE_URL and LANGFUSE_BASE_URL pointed at it.

The Messages fake enforces the request rules for the Claude 5 models, so a block that breaks
one fails here with the 400 the API would give.
"""

import contextlib
import json
import logging
import re
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

NOW = "2026-11-01T00:00:00.000Z"
MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-sonnet-5-5", "claude-haiku-5-5"}


class FakeLangfuse:
    def __init__(self):
        self.requests, self.scores, self.datasets, self.items, self.queues = [], [], {}, {}, {}

    def __call__(self, method, path, body):
        self.requests.append((method, path, body))
        if path.endswith("/api/public/projects"):
            return 200, {"data": [{"id": "local", "name": "local", "metadata": {}, "organization": {"id": "o", "name": "o"}}]}
        if "/api/public/v2/prompts" in path:
            return 404, {"message": "Prompt not found"}
        if path.endswith("/api/public/scores") and method == "POST":
            self.scores.extend(body if isinstance(body, list) else [body])
            return 200, {"id": str(uuid.uuid4())}
        if path.endswith("/api/public/v2/datasets") and method == "POST":
            d = {"id": body["name"], "name": body["name"], "description": body.get("description"), "metadata": body.get("metadata"),
                 "projectId": "local", "createdAt": NOW, "updatedAt": NOW}
            self.datasets[body["name"]] = d
            return 200, d
        if "/api/public/v2/datasets/" in path and method == "GET":
            name = path.rsplit("/", 1)[-1]
            return (200, self.datasets[name]) if name in self.datasets else (404, {"message": "no dataset"})
        if path.endswith("/api/public/dataset-items") and method == "POST":
            i = {"id": body.get("id") or str(uuid.uuid4()), "status": "ACTIVE", "input": body.get("input"),
                 "expectedOutput": body.get("expectedOutput"), "metadata": body.get("metadata"),
                 "sourceTraceId": body.get("sourceTraceId"), "sourceObservationId": None, "mediaReferences": [], "datasetId": body["datasetName"],
                 "datasetName": body["datasetName"], "createdAt": NOW, "updatedAt": NOW}
            self.items.setdefault(body["datasetName"], []).append(i)
            return 200, i
        if path.endswith("/api/public/dataset-items") and method == "GET":
            rows = [i for v in self.items.values() for i in v]
            return 200, {"data": rows, "meta": {"page": 1, "limit": 50, "totalItems": len(rows), "totalPages": 1}}
        if path.endswith("/api/public/annotation-queues") and method == "POST":
            q = {"id": str(uuid.uuid4()), "name": body["name"], "description": body.get("description"),
                 "scoreConfigIds": body.get("scoreConfigIds", []), "createdAt": NOW, "updatedAt": NOW}
            self.queues[q["id"]] = q
            return 200, q
        if "/api/public/annotation-queues/" in path and path.endswith("/items") and method == "POST":
            return 200, {"id": str(uuid.uuid4()), "queueId": path.split("/")[-2], "objectId": body["objectId"],
                         "objectType": body["objectType"], "status": "PENDING", "createdAt": NOW, "updatedAt": NOW}
        if path.endswith("/api/public/v2/metrics"):
            return 200, {"data": []}
        return 200, {}


class Capture:
    """What the offline client would have sent."""

    def __init__(self, exporter, api):
        self.exporter, self.api = exporter, api

    def spans(self):
        return self.exporter.get_finished_spans()


def offline_langfuse():
    """A real Langfuse client whose spans stay in memory and whose API calls hit the fake."""
    import httpx
    from langfuse import Langfuse
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    logging.getLogger("langfuse").setLevel(logging.CRITICAL)
    api, exporter = FakeLangfuse(), InMemorySpanExporter()

    def handler(request):
        body = json.loads(request.content) if request.content else None
        status, payload = api(request.method, request.url.path, body)
        return httpx.Response(status, json=payload)

    lf = Langfuse(public_key="pk-lf-local", secret_key="sk-lf-local", base_url="http://langfuse.invalid",
                  span_exporter=exporter, httpx_client=httpx.Client(transport=httpx.MockTransport(handler)))
    return lf, Capture(exporter, api)


def _fill(schema, text):
    """A value of the right type for a JSON schema, so structured output validates."""
    kind = schema.get("type")
    if "enum" in schema:
        return schema["enum"][0]
    if kind == "object":
        return {k: _fill(v, text) for k, v in schema.get("properties", {}).items()}
    if kind == "array":
        return []
    return {"string": "stub", "number": 0.5, "integer": 1, "boolean": False}.get(kind)


def _tool_args(schema, text):
    args = {}
    for name in schema.get("required", []):
        spec = schema["properties"][name]
        match = re.search(r"\bt\d{5}\b", text)
        args[name] = match.group(0) if name == "trace_id" and match else _fill(spec, text)
    return args


def fake_messages(body):
    """The rule checks and a scripted reply. Returns (status, payload)."""
    def bad(message):
        return 400, {"type": "error", "error": {"type": "invalid_request_error", "message": message}}

    if body.get("model") not in MODELS:
        return 404, {"type": "error", "error": {"type": "not_found_error", "message": f"model: {body.get('model')}"}}
    for param in ("temperature", "top_p", "top_k"):
        if param in body:
            return bad(f"{param} is not supported on this model")
    if body.get("thinking", {}).get("type") in ("enabled", "disabled"):
        return bad("thinking: use adaptive or omit")
    if body.get("tool_choice", {}).get("type") in ("any", "tool"):
        return bad("forced tool_choice is not supported on this model")
    if body["messages"][-1]["role"] == "assistant":
        return bad("assistant prefill is not supported on this model")
    if "max_tokens" not in body:
        return bad("max_tokens: required")

    text = json.dumps(body["messages"], ensure_ascii=False)
    usage = {"input_tokens": 120, "output_tokens": 40, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 2400}
    reply = {"id": "msg_fake", "type": "message", "role": "assistant", "model": body["model"], "stop_sequence": None, "usage": usage}
    last = body["messages"][-1]["content"]
    answered_tool = isinstance(last, list) and any(b.get("type") == "tool_result" for b in last)
    tools = body.get("tools") or []
    if tools and not answered_tool:
        tool = tools[0]
        reply["content"] = [{"type": "tool_use", "id": "toolu_fake", "name": tool["name"], "input": _tool_args(tool["input_schema"], text)}]
        reply["stop_reason"] = "tool_use"
        return 200, reply
    schema = body.get("output_config", {}).get("format", {}).get("schema")
    out = json.dumps(_fill(schema, text)) if schema else "Stub reply from the local fake."
    reply["content"] = [{"type": "text", "text": out}]
    reply["stop_reason"] = "end_turn"
    return 200, reply


@contextlib.contextmanager
def serve():
    """Run both fakes on a localhost port for the length of the block."""
    langfuse = FakeLangfuse()

    class Handler(BaseHTTPRequestHandler):
        def _reply(self, status, payload):
            data = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _handle(self, method):
            length = int(self.headers.get("content-length") or 0)
            raw = self.rfile.read(length) if length else b""
            if self.headers.get("Content-Encoding") == "gzip" or "otel" in self.path:
                return self._reply(200, {})  # OTLP span export: accepted and dropped
            body = json.loads(raw) if raw else None
            path = self.path.split("?")[0]
            if path == "/v1/messages":
                self._reply(*fake_messages(body))
            else:
                self._reply(*langfuse(method, path, body))

        def do_GET(self):
            self._handle("GET")

        def do_POST(self):
            self._handle("POST")

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
