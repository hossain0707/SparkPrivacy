# START HERE — SparkPrivacy development handover

**GitHub:** https://github.com/hossain0707/SparkPrivacy  
**Creator:** Md Najmul Hossain  
**Product:** Local-first text AI data-protection workbench for NVIDIA DGX Spark and other private inference systems.  
**Version:** 0.1.0 developer preview (2026-10-25). **Not production-certified.**

## Continue from another workspace

1. Clone the repository and inspect `README.md`, `START_HERE.md`, `AGENTS.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/VERIFICATION.md` and `docs/PRODUCT_ROADMAP.md` **before changing anything**.
2. Use Python 3.11+; run `python -m pip install -e '.[dev]'`, then `python -m pytest -q`, `node --check sparkprivacy/frontend/app.js`, and `python desktop_launcher.py --self-test`.
3. Launch `python -m sparkprivacy` and inspect the responsive frontend on a normal Windows, Mac or Linux browser. On an actual DGX Spark, test authenticated OpenSSH and tunnel forwarding with an independently verified host fingerprint.
4. Never store raw prompts, original protected text, SSH keys, upstream API keys, unredacted model outputs or credentials in audit logs. Keep all upstream AI endpoints loopback-only unless a separately reviewed security design is adopted.
5. Update diagrams, test evidence, install instructions, screenshots/animations, changelog and release information as functionality changes.

## Implemented architecture

- `sparkprivacy/server.py`: loopback FastAPI controller, Origin/Host/CSRF-style session-token safeguards, request sizing and security headers; local API endpoints and web UI.
- `sparkprivacy/scanner.py`: bounded pattern detection for email, common phone numbers, selected API token formats, payment cards with Luhn, Korean resident-ID patterns and formatted US SSN candidates; overlap-safe masking.
- `sparkprivacy/policy.py`: category-level block/redact/monitor choices. Defaults block keys/card/IDs and redact email/phone.
- `sparkprivacy/gateway.py`: non-streaming text-only compatible chat completions with separate request/response policy decisions, explicitly localhost-only upstream endpoint and disabled redirects; no cloud credentials persisted.
- `sparkprivacy/store.py`: metadata-only local SQLite audit and policy settings, thread-serialized DB access, retention and permission restriction on Unix.
- `sparkprivacy/ssh.py`: system OpenSSH import, strict host key and batch key authentication, restricted read-only diagnostics and 127.0.0.1-only SSH port forwarding.
- `sparkprivacy/reports.py`: PDF aggregate assessment with limitations, no user prompt content.
- `sparkprivacy/frontend/`: responsive vanilla JS/CSS/HTML interface and icon, no external CDN or analytics.
- `desktop_launcher.py`: optional pywebview desktop shell; start readiness checking and packaged-file import self-test.
- `.github/workflows/ci.yml`: 3 OS × 3 Python tests, dependency audit, four desktop builds and automatically versioned unsigned prerelease assets after all pass.
- `scripts/generate_icons.py`, `scripts/package_linux.sh`, `installer/SparkPrivacy.iss`: installer asset/build recipes.

## Working and pending

**Locally verified:** 55 pytest tests passed, JS syntax passed, packaged-file import check passed, and `/health` returned application readiness over loopback. Automated Chromium browsing was attempted but blocked by the test environment's administrative browser navigation policy (`ERR_BLOCKED_BY_ADMINISTRATOR`); do not claim a passed visual end-to-end browser test.

**Pending verification:** GitHub Actions cross-OS test/build success and release asset publication until actually observed, clean-machine installation and launch, Windows code signing, Mac notarization, actual Spark Ethernet/LAN/VPN SSH and model API tests, independent security assessment and DLP false-negative/false-positive evaluation. A future version may add team auth, configurable consent-based enterprise data classifications, streaming protocol protection, multimodal inspection and SIEM audit export—but none is implemented now.

## Security and privacy guardrails

- Detection is heuristic: do not claim exhaustive security or regulatory certification.
- Inspect **every** network-bound field: do not pass unrecognized tool/multimodal content through to a model as-is.
- Prevent SSRF by requiring exact loopback upstream and redirect refusal; remote hosts require independently configured SSH tunnel.
- Never disable strict `known_hosts` checks. No automated remote SSH commands other than predefined read-only diagnostics.
- Keep model API credentials in volatile process memory only, not in SQLite or repo.
- Do not expose loopback dashboard or session token to internet, screenshots, logs or telemetry.
- Require independently validated acceptance evidence before any "production-grade" claim.

## Visual identity

Professional dark navy with jade/mint accents and subtle purple-blue depth. Motion must respect `prefers-reduced-motion`; no needless emojis, fake security metrics or external tracked images. Repository visuals: `docs/sparkprivacy-hero.svg`, `docs/sparkprivacy-workflow.svg`, `docs/sparkprivacy-console.svg`, `docs/sparkprivacy-architecture.svg`. Animated visuals are **illustrative**, not a fabricated application screen recording.

## Engineering priorities

1. Get **all 14 jobs** of the CI pipeline passing; inspect and fix true toolchain failures, not hide errors. Observe tagged preview creation and verify actual asset names/checksums.
2. Manual clean-install acceptance on Windows, macOS Intel/Apple Silicon and Ubuntu, including app start, document export and removal.
3. Real Windows/Mac/Linux Ethernet/LAN/VPN SSH acceptance on an actual DGX Spark with port forwarding to a running local LLM.
4. Threat-model review, independent penetration test, dependency audit, responsible vulnerability disclosure and DLP precision/recall study using licensed benchmark data.
5. Expand inspection coverage with user-consented configurable policies and organization-level identity, while maintaining local-first architecture.
6. Sign/notarize only with legitimately held platform developer credentials; then graduate from prerelease after acceptance evidence.

## Suggested agent continuation prompt

> Continue my existing SparkPrivacy GitHub repository. Read START_HERE.md and AGENTS.md, then ARCHITECTURE, SECURITY, VERIFICATION and RELEASE docs; inspect all code before changes. Preserve all features, metadata-only audit, localhost-only gateway, strict SSH host verification and accurate evidence labels. Run tests and verify platform installers before reporting success. Make UI professional and motion accessible, update source/docs/handover with every change, and push only tested changes to the existing repository without requiring paid hosting.

## Verified Windows startup hotfix — v0.1.1-preview.4

- [**Download corrected Windows setup EXE**](https://github.com/hossain0707/SparkPrivacy/releases/download/v0.1.1-preview.4/SparkPrivacy-Setup-Windows-x64.exe) or see [all platforms](https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.1-preview.4).
- Previous **v0.1.0-preview.2** Windows installer failed at launch with `Unable to configure formatter 'default'` / `NoneType.isatty` in PyInstaller consoleless mode; replace it with **v0.1.1-preview.4**.
- [GitHub CI run 40166972946](https://github.com/hossain0707/SparkPrivacy/actions/runs/40166972946) completed **successfully**: 9 platform/Python test jobs, 1 dependency audit, 4 desktop packages with live HTTP startup checks, and 1 release publication job.
- Windows, macOS Intel/Apple Silicon, Ubuntu DEB and portable builds plus `SHA256SUMS.txt` are present in the verified prerelease. The preview is unsigned; real user-machine acceptance, DGX Spark testing and independent security validation remain pending.
