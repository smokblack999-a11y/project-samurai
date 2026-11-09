"""SSRF-resistant outbound HTTP for HAMYLION jobs."""
from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from .config import settings


class OutboundPolicyError(ValueError):
    pass


def _allowed(host: str) -> bool:
    allowed = settings.OUTBOUND_ALLOWED_HOSTS
    return host in allowed or any(host.endswith("." + suffix) for suffix in allowed)


def validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"https", "http"} or not parsed.hostname:
        raise OutboundPolicyError("only http/https URLs are allowed")

    host = parsed.hostname.lower().rstrip(".")
    if not _allowed(host):
        raise OutboundPolicyError("destination host is not allowlisted")

    try:
        infos = socket.getaddrinfo(host, parsed.port or (443 if parsed.scheme == "https" else 80), type=socket.SOCK_STREAM)
    except OSError as exc:
        raise OutboundPolicyError("destination DNS resolution failed") from exc

    for info in infos:
        address = ipaddress.ip_address(info[4][0])
        if not address.is_global:
            raise OutboundPolicyError("destination resolves to a non-public IP")

    return parsed.geturl()


async def fetch_json(url: str) -> dict:
    safe_url = validate_url(url)
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(settings.OUTBOUND_TIMEOUT_SECONDS),
        follow_redirects=False,
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    ) as client:
        response = await client.get(safe_url, headers={"accept": "application/json"})
        response.raise_for_status()
        if len(response.content) > settings.OUTBOUND_MAX_RESPONSE_BYTES:
            raise OutboundPolicyError("response exceeds maximum size")
        content_type = response.headers.get("content-type", "").lower()
        if "json" not in content_type:
            raise OutboundPolicyError("destination did not return JSON")
        value = response.json()
        if not isinstance(value, dict):
            raise OutboundPolicyError("JSON response must be an object")
        return value
