# Installing SparkPrivacy on Windows, macOS and Linux

## Release download procedure

Open https://github.com/hossain0707/SparkPrivacy/releases, select a verified **prerelease** with six assets plus `SHA256SUMS.txt`, and download the package for your OS. The CI recipe is in `.github/workflows/ci.yml`. If no release is published yet, build/test from source.

| OS | File | Action |
| --- | --- | --- |
| Windows x64 | `SparkPrivacy-Setup-Windows-x64.exe` | Run per-user installer; start from Start Menu; uninstall from Apps |
| Windows x64 portable | `SparkPrivacy-Portable-Windows-x64.zip` | Extract **entire** directory and run `SparkPrivacy.exe` |
| Mac Apple Silicon | `SparkPrivacy-macOS-Apple-Silicon-unsigned.dmg` | Open DMG, drag app into `/Applications` |
| Mac Intel | `SparkPrivacy-macOS-Intel-unsigned.dmg` | Open DMG, drag app into `/Applications` |
| Ubuntu 24.04 x64 | `SparkPrivacy-Linux-Ubuntu-x64.deb` | Install with `sudo apt install ./SparkPrivacy-Linux-Ubuntu-x64.deb` |
| Linux x64 portable | `SparkPrivacy-Portable-Linux-x64.tar.gz` | Extract all files and run binary, with GTK/WebKitGTK libraries available |

The macOS DMGs are **unsigned and unnotarized**, and the Windows EXE is **unsigned**. You may see security warnings. Do not disable platform protections as a routine installation procedure. Use approved source builds or obtain properly signed software if your organization requires verified publishers.

## First launch

1. Launch SparkPrivacy on the operator computer; no account or cloud signup is required.
2. Open **Data Inspector** and use *Load safe sample*. Run the inspection and verify the simulated email/phone are redacted under default policy.
3. Open **Policy Studio**, inspect the six category actions and customize them as needed.
4. For a model, configure an existing loopback OpenAI-compatible API; if it runs on DGX Spark, use DGX Connections and a verified SSH tunnel first.
5. In Reports, export a metadata-only PDF. In Settings, set audit retention.

## Verify release checksums

macOS/Linux: `shasum -a 256 <filename>` (or `sha256sum <filename>` on Linux), then compare with the matching filename in `SHA256SUMS.txt` on the same release.

Windows PowerShell: `Get-FileHash .\SparkPrivacy-Setup-Windows-x64.exe -Algorithm SHA256`, then compare with the release's manifest.

## Troubleshooting

- **No window appears:** confirm it launches from a system terminal; the packaged webview may depend on operating system GUI runtimes. Open the source version if native shell fails.
- **SSH failed:** check `ssh <alias>` in your terminal, network route, verified host fingerprint, user identity and private-key agent.
- **Gateway 502:** the configured loopback model server may not exist or may use another API schema; it is never started automatically.
- **Gateway 403:** default policy blocked detected sensitive content before forwarding. Inspect the reason and do not disable policy without review.
- **Report:** a PDF summarizes detector and policy metadata, not the original content.

## Developers

Clone source, `python -m pip install -e '.[dev]'`, run tests and use `python -m sparkprivacy`. Optional native shell: `python -m pip install -e '.[desktop]'`; `python desktop_launcher.py`. Builds are defined in `.github/workflows/ci.yml`.

## Direct verified download (2026-10-25)

The first published preview is [`v0.1.0-preview.2`](https://github.com/hossain0707/SparkPrivacy/releases/tag/v0.1.0-preview.2), containing the exact Windows, macOS and Linux filenames listed above, plus a matching SHA-256 manifest. The release pipeline passed 15 jobs. The binaries remain unsigned, with clean-machine acceptance pending. For later releases, choose the newest GitHub-verified preview whose assets and checksums have been inspected.
