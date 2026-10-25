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
| CI Python tests Windows/macOS/Ubuntu | Pending observable workflow run |
| CI dependency audit | Pending observable workflow run |
| CI Windows x64 installer / portable, Mac Intel / Silicon DMGs, Ubuntu DEB | Pending observable workflow run |
| GitHub published release with all assets and SHA256 | Pending observable workflow run |
| Clean-machine install/update/uninstall | Pending |
| Live Ethernet and VPN DGX Spark SSH+model tunnel | Pending |
| Independent penetration test and DLP detector evaluation | Pending |
| Authenticated enterprise workflow/RBAC | Not implemented |
| Windows certificate signing and Apple notarization | Pending valid signing credentials |

Never claim production security or official privacy certification based on 55 functional tests alone.

## Verified CI and preview release — 2026-10-25

All 15 GitHub Actions jobs passed on run 40165510595, including the Windows encoding test fix, dependency audit, desktop build self-checks and release publication. Download verified `v0.1.0-preview.2` from https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.0-preview.2. Real DGX Spark hardware acceptance, clean-machine installations, Windows signing, Mac notarization, independent pen testing and DLP recall/precision remain open. A controlled local HTTP mock verified request+response email redaction without persistence of raw text.

## Desktop Windows startup hotfix (v0.1.1 source, 2026-10-25)

- Original v0.1.0-preview.2 Windows user screenshot: GUI startup failed in the Uvicorn default formatter because `sys.stdout` was `None` under PyInstaller `--windowed`.
- `desktop_launcher.py` now deliberately opts out of Uvicorn's terminal-dependent default logging via `log_config=None`.
- Added regression cases in `tests/test_packaging.py` to emulate both missing console streams, check real local FastAPI startup, and verify JSON report generation.
- **57 tests passed locally** on Python 3.13/Linux; `python desktop_launcher.py --startup-self-test /tmp/sparkprivacy.json` returned a JSON report showing successful backend and frontend HTTP responses.
- GitHub Actions now runs the startup self-test on built Windows/macOS/Linux GUI binaries; these checks must pass before the **v0.1.1** preview can be published.
- **Still pending:** independent clean-PC confirmation, actual DGX Spark, code signing, pen test. Do not claim hardware acceptance or 100% DLP reliability.

## Verified Windows startup hotfix — v0.1.1-preview.4

- [**Download corrected Windows setup EXE**](https://github.com/hossain0707/SparkPrivacy/releases/download/v0.1.1-preview.4/SparkPrivacy-Setup-Windows-x64.exe) or see [all platforms](https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.1-preview.4).
- Previous **v0.1.0-preview.2** Windows installer failed at launch with `Unable to configure formatter 'default'` / `NoneType.isatty` in PyInstaller consoleless mode; replace it with **v0.1.1-preview.4**.
- [GitHub CI run 40166972946](https://github.com/hossain0707/SparkPrivacy/actions/runs/40166972946) completed **successfully**: 9 platform/Python test jobs, 1 dependency audit, 4 desktop packages with live HTTP startup checks, and 1 release publication job.
- Windows, macOS Intel/Apple Silicon, Ubuntu DEB and portable builds plus `SHA256SUMS.txt` are present in the verified prerelease. The preview is unsigned; real user-machine acceptance, DGX Spark testing and independent security validation remain pending.
