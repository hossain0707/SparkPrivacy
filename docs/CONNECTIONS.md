# Connecting SparkPrivacy to DGX Spark

SparkPrivacy runs as a desktop app on **Windows, macOS or Linux** and can optionally inspect DGX Spark / Linux hosts through the same **system OpenSSH** used by VS Code Remote SSH.

## Method A — Ethernet or local network

1. Connect the host using Ethernet directly (with suitable IP configuration) or a router/switch; Wi-Fi/LAN also works if SSH is reachable.
2. Set up OpenSSH on the operator computer and verify the DGX Spark account supports key-based access.
3. Verify the machine's SSH host fingerprint **out of band**, then store it in the system `known_hosts`. Do not disable strict checking.
4. Add a host alias under `~/.ssh/config` (Windows also supports `%USERPROFILE%\.ssh\config`), and test `ssh my-dgx-spark` from your system terminal.
5. Open SparkPrivacy → DGX Connections → enter/select `my-dgx-spark` → Run read-only diagnostics.

Example (illustrative addresses only):

```sshconfig
Host my-dgx-spark
    HostName 192.168.1.25
    User your-user
    Port 22
    IdentityFile ~/.ssh/id_ed25519
```

## Method B — Remote internet via secure VPN

Place both computers on a VPN such as Tailscale/WireGuard or an equivalent company-approved private connection. Import/use the verified SSH host alias; do not expose the app controller or unmanaged SSH to the public internet.

## Model gateway forwarding

When a model server already runs on the Spark at 127.0.0.1:8000, use **Start private tunnel** with remote port `8000`. SparkPrivacy manages a subprocess with strict host-key checking and binds its local listener to 127.0.0.1. Enter `http://127.0.0.1:<selected-local-port>/v1/chat/completions` in the AI Gateway configuration, and provide the exact model ID. This step does **not** install a model or start inference for you.

**Failures:** Missing keys, unverified fingerprints, SSH permission errors, blocked port forwarding, stopped hosts, missing LLM service and broken VPN connectivity cannot be solved merely by clicking Connect. Check the system terminal and the network administrator's policies. An unbootable DGX Spark may require physical access.
