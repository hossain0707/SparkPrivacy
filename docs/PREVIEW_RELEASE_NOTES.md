# SparkPrivacy v0.1.1 — Windows desktop startup hotfix (unsigned developer preview)

SparkPrivacy is an independent, local-first private AI data-protection workbench for Windows, macOS and Linux, with optional NVIDIA DGX Spark access through existing OpenSSH credentials.

### Fixed in this build

- Corrected Windows "Unable to configure formatter default" crash caused by PyInstaller `--windowed` removing `sys.stdout`/`sys.stderr` before Uvicorn logging initialization.
- Disabled Uvicorn's console-only default logging configuration in the packaged desktop launcher.
- Added live packaged-application HTTP startup and frontend-asset verification to the Windows, macOS and Linux CI build jobs.
- Added regression tests that reproduce both missing standard streams and exercise the full local service startup.
- Please uninstall or replace the original v0.1.0-preview.2 Windows build.

### Included features

- Local sensitive-data inspector and block/redact/monitor policy studio.
- Loopback-only text chat policy gateway with input and output protection.
- Metadata-only local audit history, retention, evidence-labeled PDF assessments.
- Strict OpenSSH host aliases, read-only diagnostics and local port forwarding.
- Professional accessible desktop-style UI and source documentation.

### Download packages

Select the Windows x64 Setup EXE, macOS Apple Silicon/Intel DMG, Ubuntu x64 DEB or portable ZIP/TAR.GZ. Compare your file with the included `SHA256SUMS.txt`.

### Essential limitations

**Unsigned preview.** Windows may warn about an unknown publisher; macOS packages are unnotarized and may be blocked by system policy. Clean-machine installation, actual DGX Spark hardware acceptance, pattern detector accuracy testing and independent security audits remain pending. This is **not** comprehensive DLP, official compliance certification, or NVIDIA-endorsed software. No raw prompts or model outputs are intentionally stored in SparkPrivacy's audit database. See `docs/SECURITY.md` and `docs/RELEASE.md`.

© 2026 Md Najmul Hossain.
