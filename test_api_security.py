import base64
import unittest
from unittest.mock import patch

from src.api import app


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_data_routes_fail_closed_without_api_key_configuration(self):
        with patch("src.api.Config.API_KEY", ""):
            requests = [
                self.client.get("/data"),
                self.client.post("/data", json={"name": "blocked"}),
                self.client.get("/data/1"),
                self.client.put("/data/1", json={"name": "blocked"}),
                self.client.delete("/data/1"),
            ]
        self.assertTrue(all(response.status_code == 503 for response in requests))

    def test_data_routes_reject_missing_or_wrong_key(self):
        with patch("src.api.Config.API_KEY", "expected-test-key"):
            requests = [
                self.client.get("/data"),
                self.client.get("/data", headers={"X-API-Key": "wrong"}),
                self.client.post("/data", json={"name": "blocked"}),
                self.client.get("/data/1"),
                self.client.put("/data/1", json={"name": "blocked"}),
                self.client.delete("/data/1"),
            ]
        self.assertTrue(all(response.status_code == 401 for response in requests))

    def test_valid_api_key_allows_data_read(self):
        with patch("src.api.Config.API_KEY", "expected-test-key"), \
             patch("src.api.ensure_storage_file"), \
             patch("src.api.load_storage", return_value={"items": []}):
            response = self.client.get(
                "/data", headers={"X-API-Key": "expected-test-key"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"items": []})

    def test_panel_fails_closed_without_credentials(self):
        with patch("src.api.Config.PANEL_USERNAME", ""), \
             patch("src.api.Config.PANEL_PASSWORD", ""):
            response = self.client.get("/panel")
        self.assertEqual(response.status_code, 503)

    def test_panel_rejects_invalid_basic_auth(self):
        credentials = base64.b64encode(b"admin:wrong").decode("ascii")
        with patch("src.api.Config.PANEL_USERNAME", "admin"), \
             patch("src.api.Config.PANEL_PASSWORD", "correct-password"):
            response = self.client.get(
                "/panel", headers={"Authorization": f"Basic {credentials}"}
            )
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)

    def test_panel_accepts_configured_basic_auth(self):
        credentials = base64.b64encode(b"admin:correct-password").decode("ascii")
        with patch("src.api.Config.PANEL_USERNAME", "admin"), \
             patch("src.api.Config.PANEL_PASSWORD", "correct-password"), \
             patch("src.api.ensure_storage_file"), \
             patch("src.api.load_storage", return_value={"items": []}):
            response = self.client.get(
                "/panel", headers={"Authorization": f"Basic {credentials}"}
            )
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
