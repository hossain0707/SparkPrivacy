# Security model, threat assumptions and limitations

**Status:** Security-conscious development MVP, **not** independently audited enterprise DLP, privacy certification, HIPAA/GDPR/financial compliance product, or data-leak guarantee.

## Data model

- Raw scanned text is handled in process/request memory and returned only as sanitized preview or a block decision.
- AI gateway may send sanitized or monitor-approved text to a configured **local** model endpoint. That endpoint controls its own logs, storage, auth and training behavior; SparkPrivacy cannot enforce the external process's data practices.
- Local SQLite contains **timestamps, event channel, action, detector categories and counts**, plus non-secret category policy settings. No original prompts, responses or credentials are intentionally stored.
- Optional upstream model authorization token is **volatile process memory only**. The UI temporarily holds it when entered and clears the form after saving.
- OpenSSH uses the operator's existing keys/ssh-agent and `known_hosts`. The application does not read/store the SSH private key bytes.
- PDF reports contain only aggregate controls and event summaries; no original sensitive data values.

## Enforced controls

| Control | Mechanism |
| --- | --- |
| Controller bind | 127.0.0.1 only; per-run random port |
| Local API access | 40-byte random token in header/Bearer; not persisted |
| Browser CSRF/rebinding | Host and Origin restrictions, no CORS; security headers and restrictive CSP |
| Request bounds | 240 KB HTTP JSON body, max 100k characters per scan, max 48 text messages |
| Upstream SSRF | HTTP loopback literal host/localhost, explicit port and exact `/v1/chat/completions` path; no auth in URL, no redirects, `trust_env=False` |
| Untrusted response | Max 2 MB, text-only required, reclassification and field stripping |
| SSH | System OpenSSH with strict host key, batch authentication and bounded fixed read-only commands |
| SSH forwarding | Optional subprocess `ssh -N -L 127.0.0.1:<port>:127.0.0.1:<remote_port>` |
| Audit | Local metadata-only SQLite, bounded listing, retention/purge |
| App distribution | Reproducible CI preview builds, not signed/notarized yet |

## Important limitations

- **No comprehensive detection:** known regex patterns miss novel tokens, unstructured identifying information, attachments, named confidential projects, obfuscation, encrypted fields, and language-specific PII. A valid-looking candidate may be a false positive. Korean resident identifiers are syntax-based, not validated against authoritative registries.
- **No streaming/multimodal/tool support:** these are refused/stripped to avoid unscanned side channels; additional schemas require deep review.
- **No enterprise access control:** only one local operator with access to the desktop session, no organizational roles/approvals or immutable audit trail.
- **Local admin threat:** an administrator or malware on the operator machine may access process memory or the local database. `chmod 0600` is not equivalent to full disk encryption.
- **Prompt injection:** content inspection is not a proof of semantic prompt-injection resistance or secure agent behavior.
- **Reporting:** event counts show only what the configured detectors observed. Compliance or safety must not be inferred from low event counts.
- **SSH trust:** importing aliases from `~/.ssh/config` delegates some behavior (including ProxyJump or ProxyCommand) to the user's installed OpenSSH config; users must trust their own config.
- **Network:** the model endpoint is local or tunneled; its privacy guarantees depend on the independent model server and deployment policy.

## Before enterprise deployment

Obtain independent penetration testing, threat modeling including dependency/supply chain, actual Windows/Mac/Linux installer acceptance and signing, DLP precision/recall on representative permitted datasets, a privacy impact assessment, safe backup/restore plans, secure update channel, incident response playbook, and authorized legal/compliance review. Define customer retention and regulatory boundaries explicitly.

Report vulnerabilities privately to the repository owner; do not post private exploit details or user secrets in public issues.
