"""Local-only, non-streaming OpenAI-compatible protection gateway."""
from __future__ import annotations

from copy import deepcopy
import ipaddress
from urllib.parse import urlsplit

import httpx
from .policy import decide

MAX_MESSAGES = 48
MAX_UPSTREAM_BYTES = 2_000_000


def validate_endpoint(value: str) -> str:
    if not isinstance(value, str) or len(value) > 200:
        raise ValueError("Endpoint must be an HTTP loopback chat-completions URL")
    parts = urlsplit(value)
    if parts.scheme != "http" or parts.username or parts.password or parts.query or parts.fragment:
        raise ValueError("Only HTTP loopback endpoints are allowed. Connect remote hosts through an SSH tunnel.")
    if parts.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise ValueError("Upstream must be localhost, 127.0.0.1 or ::1; remote servers require an SSH tunnel")
    try:
        port = parts.port
    except ValueError:
        raise ValueError("Invalid port") from None
    if port is None or not 1 <= port <= 65535 or parts.path != "/v1/chat/completions":
        raise ValueError("Endpoint must include a port and end with /v1/chat/completions")
    return value


def sanitize_request(payload: dict, actions: dict) -> tuple[dict | None, dict]:
    if not isinstance(payload, dict) or not isinstance(payload.get("messages"), list) or not 1 <= len(payload["messages"]) <= MAX_MESSAGES:
        raise ValueError("Send 1–48 chat messages")
    if payload.get("stream") is True:
        raise ValueError("Streaming responses are not supported; disable stream to prevent leakage")
    if not isinstance(payload.get("model"), str) or not 1 <= len(payload["model"]) <= 150:
        raise ValueError("Provide a model identifier")
    clone = deepcopy(payload)
    counts: dict[str, int] = {}
    disposition = "allowed"
    for msg in clone["messages"]:
        if not isinstance(msg, dict) or msg.get("role") not in {"system", "user", "assistant", "tool", "developer"} or not isinstance(msg.get("content"), str):
            raise ValueError("Only text chat messages are supported. Multimodal/tools require additional DLP coverage.")
        result = decide(msg["content"], actions)
        for category, n in result.categories.items():
            counts[category] = counts.get(category, 0) + n
        if result.disposition == "blocked":
            return None, {"disposition": "blocked", "categories": counts, "finding_count": sum(counts.values())}
        # Retain only recognized text fields; unknown multimodal/tool keys must not bypass scanning.
        msg["content"] = result.sanitized
        for field in list(msg):
            if field not in {"role", "content"}:
                del msg[field]
        if result.disposition == "redacted":
            disposition = "redacted"
        elif result.disposition == "observed" and disposition == "allowed":
            disposition = "observed"
    # Strict schema: do not forward unknown payload keys (could include unseen images or private data).
    allowed = {"messages", "model", "temperature", "max_tokens", "top_p", "frequency_penalty", "presence_penalty", "stream"}
    clone = {key: value for key, value in clone.items() if key in allowed}
    clone["stream"] = False
    return clone, {"disposition": disposition, "categories": counts, "finding_count": sum(counts.values())}


def sanitize_response(response: dict, actions: dict) -> tuple[dict, dict]:
    if not isinstance(response, dict) or not isinstance(response.get("choices"), list):
        raise ValueError("Upstream response does not contain compatible choices")
    clone = deepcopy(response)
    totals: dict[str, int] = {}
    status = "allowed"
    for choice in clone["choices"]:
        message = choice.get("message") if isinstance(choice, dict) else None
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ValueError("Non-text upstream responses are not supported")
        result = decide(message["content"], actions)
        for category, n in result.categories.items():
            totals[category] = totals.get(category, 0) + n
        if result.disposition == "blocked":
            message["content"] = "[BLOCKED BY SPARKPRIVACY POLICY]"
            status = "blocked"
        else:
            message["content"] = result.sanitized
            if result.disposition == "redacted" and status != "blocked":
                status = "redacted"
            elif result.disposition == "observed" and status == "allowed":
                status = "observed"
    # Drop unknown top-level upstream fields and choices metadata? Most APIs use standard response.
    clean = {k: clone[k] for k in ("id", "object", "created", "model", "choices") if k in clone}
    if isinstance(clone.get("usage"), dict):
        clean["usage"] = {k: v for k, v in clone["usage"].items()
                          if k in {"prompt_tokens", "completion_tokens", "total_tokens"} and isinstance(v, int) and v >= 0}
    for choice in clean["choices"]:
        for field in list(choice):
            if field not in {"index", "finish_reason", "message"}:
                del choice[field]
        choice["message"] = {k: v for k, v in choice["message"].items() if k in {"role", "content"}}
        choice["finish_reason"] = choice.get("finish_reason") if choice.get("finish_reason") in {"stop", "length", "content_filter", None} else "stop"
    return clean, {"disposition": status, "categories": totals, "finding_count": sum(totals.values())}


async def forward(payload: dict, endpoint: str, upstream_key: str | None = None) -> dict:
    endpoint = validate_endpoint(endpoint)
    headers = {"Content-Type": "application/json"}
    if upstream_key:
        headers["Authorization"] = "Bearer " + upstream_key
    try:
        async with httpx.AsyncClient(timeout=35.0, follow_redirects=False, trust_env=False) as client:
            async with client.stream("POST", endpoint, json=payload, headers=headers) as response:
                if 300 <= response.status_code < 400:
                    raise ValueError("Upstream redirects are disabled")
                if response.status_code != 200:
                    raise RuntimeError(f"Local model server returned HTTP {response.status_code}")
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > MAX_UPSTREAM_BYTES:
                    raise ValueError("Model response is too large")
                raw = bytearray()
                async for chunk in response.aiter_bytes():
                    raw.extend(chunk)
                    if len(raw) > MAX_UPSTREAM_BYTES:
                        raise ValueError("Model response exceeds maximum accepted size")
    except httpx.HTTPError as exc:
        raise RuntimeError("Local model endpoint connection failed") from None
    try:
        import json
        return json.loads(raw)
    except (ValueError, UnicodeDecodeError):
        raise ValueError("Model endpoint returned invalid JSON") from None
