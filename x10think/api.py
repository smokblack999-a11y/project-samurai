from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlparse

from .agent import Agent
from .together import TogetherError


DASHBOARD = Path(__file__).resolve().parent.parent / "dashboard" / "index.html"
MAX_PROMPT_CHARS = 4000


class APIHandler(BaseHTTPRequestHandler):
    agent: Agent | None = None

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0 or length > 16_384:
            raise ValueError("invalid request body size")
        raw = self.rfile.read(length)
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("request body must be a JSON object")
        return payload

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            if DASHBOARD.exists():
                body = DASHBOARD.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        if path == "/api/status":
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

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/diagnose":
            self._json(404, {"error": "not_found"})
            return
        try:
            payload = self._read_json()
            prompt = payload.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                self._json(400, {"error": "prompt_required"})
                return
            if len(prompt) > MAX_PROMPT_CHARS:
                self._json(413, {"error": "prompt_too_large", "max_chars": MAX_PROMPT_CHARS})
                return
            if self.agent is None:
                self._json(503, {"error": "agent_unavailable"})
                return
            result = self.agent.diagnose(prompt)
            self._json(200, {"ok": True, "diagnosis": result})
        except TogetherError as exc:
            self._json(502, {"error": str(exc)})
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_json"})
        except Exception:
            self._json(500, {"error": "diagnostic_failed"})

    def log_message(self, *_args) -> None:
        return


def serve(agent: Agent, host: str, port: int) -> None:
    APIHandler.agent = agent
    server = ThreadingHTTPServer((host, port), APIHandler)
    print(f"X10THINK API listening on http://{host}:{port}")
    server.serve_forever()
