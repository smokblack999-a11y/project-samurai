from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlparse

from .agent import Agent


class APIHandler(BaseHTTPRequestHandler):
    agent: Agent | None = None

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path in ("/", "/api/status"):
            state = self.agent.store.read() if self.agent else {}
            self._json(200, {"service": "x10think", "status": "online", "state": state})
            return
        if path == "/api/health":
            self._json(200, self.agent.scan_once() if self.agent else {"error": "agent unavailable"})
            return
        if path == "/api/logs":
            self._json(200, {"logs": []})
            return
        self._json(404, {"error": "not_found"})

    def log_message(self, *_args) -> None:
        return


def serve(agent: Agent, host: str, port: int) -> None:
    APIHandler.agent = agent
    server = ThreadingHTTPServer((host, port), APIHandler)
    print(f"X10THINK API listening on http://{host}:{port}")
    server.serve_forever()
