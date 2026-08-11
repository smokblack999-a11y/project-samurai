from __future__ import annotations

import json
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://api.together.ai/v1"
DEFAULT_MODEL = "openai/gpt-oss-20b"


class TogetherError(RuntimeError):
    """Safe, user-facing Together API failure without exposing credentials."""


@dataclass(frozen=True)
class TogetherConfig:
    api_key: str
    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    timeout: float = 20.0

    @classmethod
    def from_env(cls) -> "TogetherConfig | None":
        key = os.getenv("TOGETHER_API_KEY", "").strip()
        if not key:
            return None
        return cls(
            api_key=key,
            base_url=os.getenv("TOGETHER_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
            model=os.getenv("TOGETHER_MODEL", DEFAULT_MODEL),
            timeout=float(os.getenv("TOGETHER_TIMEOUT", "20")),
        )


def diagnose(prompt: str, *, config: TogetherConfig | None = None) -> str:
    cfg = config or TogetherConfig.from_env()
    if cfg is None:
        raise TogetherError("Together AI is not configured: TOGETHER_API_KEY is missing")
    if not prompt.strip():
        raise TogetherError("diagnostic prompt must not be empty")

    payload = {
        "model": cfg.model,
        "messages": [
            {
                "role": "system",
                "content": "You are an infrastructure diagnostics assistant. Be concise, evidence-based, and propose only safe, reversible next steps.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 700,
    }
    request = Request(
        f"{cfg.base_url}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {cfg.api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=cfg.timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise TogetherError("Together AI authentication/permission failed") from None
        if exc.code == 429:
            raise TogetherError("Together AI rate limit reached") from None
        raise TogetherError(f"Together AI request failed with HTTP {exc.code}") from None
    except (URLError, TimeoutError):
        raise TogetherError("Together AI is unreachable or timed out") from None
    except (ValueError, json.JSONDecodeError):
        raise TogetherError("Together AI returned invalid JSON") from None

    try:
        return str(data["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError):
        raise TogetherError("Together AI returned an unexpected response") from None
