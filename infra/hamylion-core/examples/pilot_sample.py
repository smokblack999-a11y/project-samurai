"""Synthetic, intentionally flawed fixture for the HAMYLION AEGIS smoke test.

All values below are fake. Never replace the dummy token with a real secret.
"""
import requests

DUMMY_API_KEY = "not-a-real-api-key-1234567890"

def fetch_internal_status(url, user_expression):
    # Intentional: TLS verification disabled.
    response = requests.get(url, headers={"X-Demo-Key": DUMMY_API_KEY}, verify=False)
    # Intentional: dynamic code execution.
    return eval(user_expression), response.status_code
