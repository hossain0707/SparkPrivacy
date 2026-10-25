# SparkPrivacy development and production roadmap

## Delivered in v0.1.0 development candidate

Local-only controller, six-category scanner, configurable policies, non-streaming text model gateway, both-direction filtering, private SSH forwarding, read-only diagnostics, SQLite metadata-only audits, retention, PDF reporting, professional responsive frontend, cross-platform packaging recipes, CI tests and full handover.

## P0 — Before claiming a stable release

- Verify cross-platform GitHub pipeline and package release artifacts.
- Test actual macOS, Windows and Linux installation, lifecycle and uninstall, including GUI WebKit/WebView runtime compatibility.
- Conduct a real DGX Spark SSH+VPN+Ethernet test and localhost inference API test with a model the user is authorized to access.
- Perform independent security threat assessment, dependency audit and red-team tests for bypasses including evasion, Unicode obfuscation, nested JSON and prompt injection.
- Obtain real code-signing/notarization credentials and publish signed binaries, update/rollback policy and clear support documentation.

## P1 — Enterprise policy coverage

- Organization auth/RBAC, separate operator and approver roles, configurable organization rules and review workflow.
- Validated privacy classifiers with measured precision/recall and test corpora; language-specific IDs; safe document classification.
- Streaming, tool-calling and multimodal support only after an end-to-end schema audit and per-field scanning.
- Tamper-evident audit export, backup/restore, SIEM/monitoring integration and data-lifecycle controls.

## P2 — Commercial differentiation

- Governed multi-node private-AI infrastructure workflows and scoped policy distribution.
- Per-organization deployment assessments and independent compliance mapping without claiming accreditation.
- Reproducible benchmark and red-team evidence tied to documented deployment configurations.

Do not introduce cloud fees, stored credentials or unsupported security guarantees without explicit user approval.
