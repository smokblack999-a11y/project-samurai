# Project Samurai API security

## Required configuration

There are no built-in API or panel credentials. Protected endpoints fail closed
until these environment variables are explicitly configured:

- `API_KEY`: required for every `/data` endpoint and `/admin/info`.
- `PANEL_USERNAME` and `PANEL_PASSWORD`: required for every `/panel` endpoint.
- `API_HOST`: defaults to `127.0.0.1`; only change it when a trusted network
  boundary and TLS reverse proxy are configured.

Generate unique secrets outside source control. Never commit a real `.env` file,
API key, panel password, or Telegram token. If a previous default key was used
outside a local test environment, rotate it.

## Authentication behavior

- Missing API_KEY: protected API routes return HTTP 503 (configuration required).
- Missing or invalid X-API-Key: protected API routes return HTTP 401.
- Missing panel credentials: panel routes return HTTP 503.
- Missing or invalid HTTP Basic credentials: panel routes return HTTP 401.
- Credential comparisons use constant-time comparison.

HTTP Basic authentication is not encryption. Do not expose the panel over plain
HTTP on an untrusted network; use localhost or HTTPS through a trusted reverse proxy.

## Verification

Run:

```sh
python -m pip install -r requirements.txt
python -m unittest -v test_api_security
python -m compileall -q src test_api_security.py
```

These tests verify route authentication behavior. They do not prove production
TLS, tenant isolation, or security of other services in the repository.
