"""Local, authenticated browser API and optional OpenAI-compatible DLP gateway."""
from __future__ import annotations

import json
import re
import secrets
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from pydantic import BaseModel, Field

from . import __version__
from .gateway import forward, sanitize_request, sanitize_response, validate_endpoint
from .paths import app_data_dir, frontend_dir
from .policy import CATEGORIES, decide, validate_actions
from .reports import make_pdf
from .scanner import MAX_SCAN_CHARS
from .ssh import TunnelManager, diagnostics, profiles
from .store import Store

MAX_BODY_BYTES = 240_000

class ScanBody(BaseModel):
    text: str = Field(min_length=0, max_length=MAX_SCAN_CHARS)

class PolicyBody(BaseModel):
    actions: dict[str, str]

class ConfigBody(BaseModel):
    endpoint: str
    model: str = Field(min_length=1, max_length=150)
    upstream_token: str | None = Field(default=None, max_length=500)

class InspectBody(BaseModel):
    alias: str

class TunnelBody(BaseModel):
    alias: str
    remote_port: int = Field(ge=1, le=65535)
    local_port: int = Field(default=0, ge=0, le=65535)

class PurgeBody(BaseModel):
    days: int = Field(ge=0, le=3650)


def create_app(data_dir: Path | None = None, *, testing: bool = False) -> FastAPI:
    state_dir = Path(data_dir) if data_dir else app_data_dir()
    store = Store(state_dir / "audit.sqlite3")
    tunnels = TunnelManager()
    token = secrets.token_urlsafe(40)
    config: dict[str, Any] = {"endpoint": "http://127.0.0.1:8000/v1/chat/completions", "model": "", "upstream_token": None}
    app = FastAPI(title="SparkPrivacy", version=__version__, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.store = store
    app.state.token = token
    app.state.tunnels = tunnels
    app.state.gateway_config = config

    @app.middleware("http")
    async def restrict_local(request: Request, call_next):
        host = request.headers.get("host", "")
        host_name = host.split(":", 1)[0].lower() if not host.startswith("[") else "rejected-ipv6-host"
        if host_name not in ({"127.0.0.1", "localhost", "testserver"} if testing else {"127.0.0.1", "localhost"}):
            return JSONResponse({"detail": "Local host only"}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin not in {f"http://{host}", f"http://127.0.0.1:{request.url.port}", f"http://localhost:{request.url.port}"}:
            return JSONResponse({"detail": "Cross-origin requests denied"}, status_code=403)
        if request.url.path.startswith(("/api/", "/v1/")):
            header = request.headers.get("x-sparkprivacy-token", "")
            bearer = request.headers.get("authorization", "")
            valid = secrets.compare_digest(header, token) or secrets.compare_digest(bearer, "Bearer " + token)
            if not valid:
                return JSONResponse({"detail": "Missing or invalid session credential"}, status_code=401)
        if request.method in {"POST", "PUT", "PATCH"} and request.url.path.startswith(("/api/", "/v1/")):
            length = request.headers.get("content-length")
            if length and (not length.isdecimal() or int(length) > MAX_BODY_BYTES):
                return JSONResponse({"detail": "Request too large"}, status_code=413)
            # Also enforce the limit on chunked uploads, before Pydantic JSON parsing.
            body = await request.body()
            if len(body) > MAX_BODY_BYTES:
                return JSONResponse({"detail": "Request too large"}, status_code=413)
        response = await call_next(request)
        response.headers.update({"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
                                 "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
                                 "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'"})
        return response

    @app.get("/health")
    def health():
        return {"application": "SparkPrivacy", "version": __version__, "status": "ready", "local_only": True}

    @app.get("/", response_class=HTMLResponse)
    def homepage():
        content = (frontend_dir() / "index.html").read_text(encoding="utf-8")
        # The value is random URL-safe server-side data, not an untrusted browser parameter.
        return HTMLResponse(content.replace("__SP_SESSION_TOKEN__", token))

    @app.get("/static/{file_name}")
    def frontend_asset(file_name: str):
        if file_name not in {"app.js", "styles.css", "mark.svg"}:
            raise HTTPException(404, "Asset not found")
        return FileResponse(frontend_dir() / file_name)

    @app.get("/api/status")
    def status():
        return {"version": __version__, "stats": store.statistics(), "policies": store.get_actions(),
                "endpoint": config["endpoint"], "model": config["model"], "tunnels": tunnels.status(),
                "local_only": True, "upstream_key_configured": bool(config["upstream_token"])}

    @app.post("/api/inspect")
    def inspect(body: ScanBody):
        d = decide(body.text, store.get_actions())
        store.event("inspector", d.disposition, d.categories, d.finding_count)
        return d.public()

    @app.get("/api/policies")
    def read_policies():
        return {"actions": store.get_actions(), "categories": list(CATEGORIES), "available": ["block", "redact", "monitor"]}

    @app.put("/api/policies")
    def put_policies(body: PolicyBody):
        try:
            store.set_actions(validate_actions(body.actions))
        except ValueError as e:
            raise HTTPException(422, str(e)) from None
        return {"actions": store.get_actions()}

    @app.get("/api/audit")
    def audit(limit: int = 100):
        return {"events": store.events(limit), "stats": store.statistics()}

    @app.post("/api/audit/purge")
    def purge(body: PurgeBody):
        return {"deleted": store.purge(body.days), "stats": store.statistics()}

    @app.get("/api/report.pdf")
    def pdf():
        output = make_pdf(store.statistics(), store.events(100), store.get_actions())
        return Response(output, media_type="application/pdf", headers={"Content-Disposition": 'attachment; filename="SparkPrivacy-Assessment.pdf"'})

    @app.post("/api/gateway/config")
    def configure(body: ConfigBody):
        try:
            endpoint = validate_endpoint(body.endpoint)
        except ValueError as e:
            raise HTTPException(422, str(e)) from None
        config.update({"endpoint": endpoint, "model": body.model, "upstream_token": body.upstream_token or None})
        return {"endpoint": endpoint, "model": config["model"], "upstream_key_configured": bool(config["upstream_token"])}

    async def proxy_payload(payload: dict):
        actions = store.get_actions()
        try:
            clean, disposition = sanitize_request(payload, actions)
        except ValueError as e:
            raise HTTPException(422, str(e)) from None
        store.event("gateway_request", disposition["disposition"], disposition["categories"], disposition["finding_count"])
        if clean is None:
            raise HTTPException(403, "Request blocked by data-protection policy")
        try:
            answer = await forward(clean, config["endpoint"], config["upstream_token"])
            secured, result = sanitize_response(answer, actions)
        except (ValueError, RuntimeError, OSError, ConnectionError) as e:
            store.event("gateway_response", "error", {}, 0)
            # Error descriptions contain no raw upstream data or prompt contents.
            raise HTTPException(502, str(e)) from None
        store.event("gateway_response", result["disposition"], result["categories"], result["finding_count"])
        return secured

    @app.post("/v1/chat/completions")
    async def chat_endpoint(request: Request):
        try:
            data = await request.json()
        except ValueError:
            raise HTTPException(400, "Invalid JSON") from None
        return await proxy_payload(data)

    @app.post("/api/gateway/test")
    async def gateway_test(request: Request):
        try:
            body = await request.json()
            prompt = body["prompt"]
            if not isinstance(prompt, str) or len(prompt) > 10_000:
                raise ValueError("Prompt too large")
        except (ValueError, KeyError, TypeError):
            raise HTTPException(422, "Provide a text prompt of at most 10,000 characters") from None
        if not config["model"]:
            raise HTTPException(409, "Configure your local model and endpoint first")
        return await proxy_payload({"model": config["model"], "messages": [{"role": "user", "content": prompt}], "stream": False})

    @app.get("/api/connections")
    def connections():
        return {"aliases": profiles(), "tunnels": tunnels.status()}

    @app.post("/api/connections/inspect")
    def inspect_ssh(body: InspectBody):
        try:
            return diagnostics(body.alias)
        except (ValueError, RuntimeError) as e:
            raise HTTPException(422, str(e)) from None

    @app.post("/api/connections/tunnel")
    def start_tunnel(body: TunnelBody):
        try:
            return tunnels.start(body.alias, body.remote_port, body.local_port)
        except (ValueError, RuntimeError, OSError) as e:
            raise HTTPException(422, str(e)) from None

    @app.delete("/api/connections/tunnel/{port}")
    def stop_tunnel(port: int):
        return {"stopped": tunnels.stop(port)}

    return app
