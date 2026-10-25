# SparkPrivacy — Coding agent instructions

Read `START_HERE.md`, `README.md`, `docs/ARCHITECTURE.md`, `docs/SECURITY.md`, `docs/VERIFICATION.md` and `docs/PRODUCT_ROADMAP.md` first. The user wants professional, accessible, animated software that works from Windows/macOS/Linux and can reach DGX Spark through existing SSH. Preserve project continuity in this repository.

## Non-negotiable constraints

- **Do not fabricate protection, accreditation, benchmark, support or test evidence.** This is a developer preview.
- **Security:** Never persist plaintext prompts, detected secret values, model responses, API keys, SSH passwords/private keys. Preserve strict SSH host-key checks and loopback-only API access. No paid cloud/SaaS dependencies.
- **Gateway:** The original pattern scanner is not comprehensive DLP. Keep deny-by-default for unknown multimodal, tools, streaming, redirects and external upstream hosts until reviewed.
- **Quality:** Run pytest, JS parse, packaged-file self-test, platform CI and real-device tests where possible. Record successes and blockers in `docs/VERIFICATION.md`.
- **Design:** Well-spaced navy/mint professional product UI, subtle CSS motion with reduced-motion fallback. No heavy remote fonts, misleading mock telemetry, or unnecessary emoji decoration.
- **Release:** Do not call unsigned prereleases production-ready. Windows/macOS signing requires real distribution credentials. Check actual GitHub release asset names.
- **Ownership:** Md Najmul Hossain. Do not assume an open-source license without authorization.

## Core code map

See `START_HERE.md`. Python package in `sparkprivacy/`, UI in `sparkprivacy/frontend/`, CI in `.github/workflows/ci.yml`, Windows installer in `installer/`, Linux packaging and platform icons in `scripts/`, tests in `tests/`, architecture and continuity in `docs/`.
