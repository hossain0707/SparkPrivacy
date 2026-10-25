# Architecture — SparkPrivacy v0.1.0

## Local-first trust boundaries

```
Windows/macOS/Linux operator
  ├── browser or optional pywebview desktop window
  ├── FastAPI HTTP server bound to 127.0.0.1 with unpredictable per-run token
  │    ├── bounded in-process detection & category policy enforcement
  │    ├── input text inspection and response text inspection
  │    ├── metadata-only SQLite audit and category policy store
  │    ├── local-only OpenAI-compatible non-streaming chat gateway
  │    ├── PDF assessment generator
  │    └── subprocess OpenSSH -> optional DGX Spark/Linux host
  └── existing AI model service on 127.0.0.1, or SSH-forwarded remote model
```

The browser and local HTTP controller are on **one device**. Actual model inference occurs on an existing local model server or an explicitly configured SSH-forwarded service. No SparkPrivacy Python agent is installed on remote DGX Spark machines. There is no cloud service.

## Request data flow

1. Accept a limited JSON request from an authenticated local client (`X-SparkPrivacy-Token` or `Authorization: Bearer`), with Host/Origin restrictions, bounded payload size and CSP.
2. Validate text-only OpenAI-compatible `messages`, reject `stream=true`, reject non-text inputs and drop unsupported request/message keys.
3. Classify text spans (bounded scanner), apply policy. If a block-class rule matches, stop before contacting the model. Otherwise replace redact-class matches; monitor-class matches intentionally pass unchanged.
4. Forward sanitized request to a validated exact HTTP **loopback** endpoint with network proxies and redirects disabled. No arbitrary private/public IP ranges are permitted. Remote DGX access must use an independently verified localhost SSH tunnel.
5. Validate and reclassify returned assistant message text, redact or replace with a constant block string as required; strip unexpected response fields.
6. Commit only event timestamp/channel/disposition/category counts to the local DB. Return sanitized response. Export aggregated PDF reports on demand.

## Desktop distribution

`desktop_launcher.py` starts the same protected controller on a free loopback port, verifies its readiness, then displays the application through pywebview (or a normal browser if pywebview is unavailable). PyInstaller packages the Python modules and frontend files. GitHub Actions builds Windows per-user setup + portable ZIP, Intel/Apple Silicon DMGs, Ubuntu DEB + portable TAR.GZ. Package self-test confirms bundled Python imports and UI assets.

## Versioning and future extensions

Current version 0.1.0 supports text-only pattern matches and a single local operator. Versioned future components (subject to secure design review): enterprise identity/RBAC, multi-user policy approvals, private installation agent, streaming and multimodal inspection, customizable classification dictionaries, secure update channels, SIEM export, expanded red-team exercises and detector evaluation corpus.

Architecture illustrations are at `docs/sparkprivacy-architecture.svg` and Mermaid in `README.md`. Update them whenever architecture changes.
