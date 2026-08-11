from __future__ import annotations

import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
import unittest

from x10think.api import APIHandler


class FakeStore:
    def read(self):
        return {}


class FakeAgent:
    def __init__(self, ok: bool = True):
        self.store = FakeStore()
        self.ok = ok

    def diagnose(self, prompt: str) -> dict:
        return {
            "provider": "test",
            "ok": self.ok,
            "answer": f"received:{prompt}",
        }


class DiagnoseHttpTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), APIHandler)
        APIHandler.agent = FakeAgent()
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def request(self, payload):
        conn = HTTPConnection("127.0.0.1", self.server.server_port, timeout=2)
        body = json.dumps(payload).encode()
        conn.request("POST", "/api/diagnose", body, {"Content-Type": "application/json"})
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        conn.close()
        return response.status, data

    def test_diagnose_success(self):
        status, data = self.request({"prompt": "check disk pressure"})
        self.assertEqual(status, 200)
        self.assertTrue(data["ok"])
        self.assertEqual(data["diagnosis"]["provider"], "test")

    def test_empty_prompt_is_rejected(self):
        status, data = self.request({"prompt": "   "})
        self.assertEqual(status, 400)
        self.assertEqual(data["error"], "prompt_required")

    def test_oversized_prompt_is_rejected(self):
        status, data = self.request({"prompt": "x" * 4001})
        self.assertEqual(status, 413)
        self.assertEqual(data["error"], "prompt_too_large")

    def test_provider_failure_is_not_reported_as_success(self):
        APIHandler.agent = FakeAgent(ok=False)
        status, data = self.request({"prompt": "diagnose"})
        self.assertEqual(status, 502)
        self.assertEqual(data["error"], "diagnostic_provider_failed")


if __name__ == "__main__":
    unittest.main()
