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

## Verified preview publication — 2026-10-25

GitHub Actions [run 40165510595](https://github.com/hossain0707/SparkPrivacy/actions/runs/40165510595) passed **all 15 jobs** (9 matrix tests, 1 dependency audit, 4 packages, 1 release publisher) and created [`v0.1.0-preview.2`](https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.0-preview.2).

Release assets verified through GitHub metadata: `SparkPrivacy-Setup-Windows-x64.exe`, `SparkPrivacy-Portable-Windows-x64.zip`, `SparkPrivacy-macOS-Intel-unsigned.dmg`, `SparkPrivacy-macOS-Apple-Silicon-unsigned.dmg`, `SparkPrivacy-Linux-Ubuntu-x64.deb`, `SparkPrivacy-Portable-Linux-x64.tar.gz`, `SHA256SUMS.txt`.

**Stable release gates still open:** real device testing, clean-machine acceptance, cross-organization policy/security testing, signing/notarization, privacy classifier quality metrics, independent security review. These assets remain unsigned developer previews.
