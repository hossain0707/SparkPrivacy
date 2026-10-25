# SparkPrivacy verification ledger — 2026-10-25

## Locally verified

- **55 pytest cases passed** on the development environment, covering PII/key detection, Luhn validation, masking, block/monitor decisions, local policy persistence, audit metadata, report PDF, authentication, Origin/Host checks, local gateway input/response stripping, SSRF rejection, OpenSSH argument validation and package-source integrity.
- `node --check sparkprivacy/frontend/app.js` passed.
- `python desktop_launcher.py --self-test` passed (`{"ok":true,"missing":[]}`).
- Live HTTP GET `/health` returned version and `status=ready` via loopback.
- Chromium attempted to load local app but returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` in the current sandbox. **No successful automated visual browser click-through is claimed.**

## External acceptance gates

| Check | Status |
| --- | --- |
| CI Python tests Windows/macOS/Ubuntu | **Verified — 9 matrix jobs passed** |
| CI dependency audit | **Verified passed** |
| CI Windows x64 installer / portable, Mac Intel / Silicon DMGs, Ubuntu DEB | **All 4 desktop build jobs passed** |
| GitHub published release with all assets and SHA256 | **Published v0.1.0-preview.2** |
| Clean-machine install/update/uninstall | Pending |
| Live Ethernet and VPN DGX Spark SSH+model tunnel | Pending |
| Independent penetration test and DLP detector evaluation | Pending |
| Authenticated enterprise workflow/RBAC | Not implemented |
| Windows certificate signing and Apple notarization | Pending valid signing credentials |

Never claim production security or official privacy certification based on 55 functional tests alone.

## Cross-platform CI and mock HTTP integration — confirmed 2026-10-25

**Run:** [40165510595](https://github.com/hossain0707/SparkPrivacy/actions/runs/40165510595) — **15/15 jobs passed**. The initial run found a Windows test-file encoding oversight; this was fixed by specifying UTF-8, then the full workflow passed on the following commit.

**Published preview:** [v0.1.0-preview.2](https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.0-preview.2), marked as prerelease with six cross-platform packages and SHA256SUMS.txt.

**Additional smoke test:** SparkPrivacy used real loopback HTTP forwarding to a controlled local OpenAI-compatible mock server. The gateway did not forward a synthetic email identifier; it replaced it with `[REDACTED:EMAIL]`. It independently redacted a second synthetic email from model output and recorded only metadata disposition counts (2 redacted events). This does not test actual NVIDIA hardware or a third-party inference runtime.

CI includes compiled-app self-tests, not clean-machine GUI installations. Physical and independent security acceptance remain pending.
