# Preview release, packaging and stable-product gates

## CI workflow

The GitHub Actions workflow performs a 9-combination unit test matrix (Windows / macOS / Linux with Python 3.11, 3.12 and 3.13), a dependency vulnerability audit, and four PyInstaller build jobs. It validates bundled imports/assets with `desktop_launcher.py --self-test` before packaging. When all jobs pass on `main`, it creates a **prerelease**, not a stable release, with tag `v0.1.0-preview.<run-number>`.

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
