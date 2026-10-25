# Preview release, packaging and stable-product gates

## CI workflow

The GitHub Actions workflow performs a 9-combination unit test matrix (Windows / macOS / Linux with Python 3.11, 3.12 and 3.13), a dependency vulnerability audit, and four PyInstaller build jobs. It validates bundled imports/assets with `desktop_launcher.py --self-test` before packaging **and** `--startup-self-test` against each bundled GUI executable with actual localhost HTTP readiness, homepage and frontend asset checks. The latter covers Windows PyInstaller `--windowed` where stdout/stderr are absent. When all jobs pass on `main`, it creates a **prerelease**, not a stable release, with tag `v0.1.1-preview.<run-number>`.

Assets include Windows per-user Inno Setup installer and portable ZIP, macOS Intel and Apple Silicon DMGs, Linux Ubuntu DEB and portable TAR.GZ, plus SHA-256 checksums. All are **unsigned**, and their existence cannot be asserted until GitHub confirms publication.

## Stable release gates

- [ ] All test matrix jobs, build jobs, dependency audits and tagged preview downloads green.
- [ ] Clean-machine Windows 10/11 x64 setup/update/uninstall acceptance.
- [ ] macOS Intel and Apple Silicon installed `.app` first-launch acceptance.
- [ ] Ubuntu 24.04 x64 DEB and portable binary first-launch acceptance.
- [ ] Real DGX Spark connectivity on Ethernet/LAN/VPN with separately validated SSH fingerprints.
- [ ] Gateway end-to-end interaction with model server (including upstream error modes and false-positive/negative checks).
- [ ] Independent threat model and penetration test, supply chain review, privacy impact assessment.
- [ ] Valid code signing and macOS notarization; trusted update/rollback paths.
- [ ] Release notes, accurate screenshots, user-facing support/security disclosure.

Do not mark these checks as completed without evidence. A green CI build is not a substitute for physical acceptance, regulatory review or security assessment.

## Verified CI and preview release — 2026-10-25

All 15 GitHub Actions jobs passed on run 40165510595, including the Windows encoding test fix, dependency audit, desktop build self-checks and release publication. Download verified `v0.1.0-preview.2` from https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.0-preview.2. Real DGX Spark hardware acceptance, clean-machine installations, Windows signing, Mac notarization, independent pen testing and DLP recall/precision remain open. A controlled local HTTP mock verified request+response email redaction without persistence of raw text.

## Windows GUI Uvicorn startup regression — 2026-10-25

**Field report:** SparkPrivacy v0.1.0-preview.2 on Windows failed to launch with "Unable to configure formatter 'default'" and `AttributeError: 'NoneType' object has no attribute 'isatty'` from `uvicorn.logging.DefaultFormatter`. In PyInstaller `--windowed`, `sys.stdout` and `sys.stderr` are `None`. The original CI import-only `--self-test` did not exercise HTTP server startup and failed to detect this.

**Correction in v0.1.1 source:** The desktop launcher now creates `uvicorn.Config(..., log_config=None)`, avoiding the console formatter. New `--startup-self-test dist/startup-check.json` starts an HTTP backend in an isolated temporary workspace, loads `/health`, `/` and `/static/app.js`, stops cleanly, and writes a JSON success/failure report without relying on stdout. Package jobs test this flag against the actual GUI executable on **all four platform runners** before publishing. Two regression tests run in normal Python with both streams forced to `None`.

**Evidence:** 57 local pytest cases passed; consoleless test and live local HTTP startup check passed on Linux/Python 3.13. Remote Windows packaging and user clean-machine acceptance must be confirmed from the new GitHub Actions run and an actual Windows PC respectively. The original v0.1.0-preview.2 Windows installer must not be recommended as fixed.
