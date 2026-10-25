"""OpenSSH-backed SSH tunnels. Does not implement custom cryptography."""
from __future__ import annotations

import re
import shutil
import socket
import subprocess
import threading
import time
from pathlib import Path

HOST = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,100}$")


def validate_alias(value: str) -> str:
    if not isinstance(value, str) or not HOST.fullmatch(value):
        raise ValueError("Use a saved SSH hostname/alias containing letters, digits, dots, hyphens or underscores")
    return value


def profiles(config: Path | None = None) -> list[str]:
    config = config or Path.home() / ".ssh" / "config"
    if not config.is_file() or config.stat().st_size > 200_000:
        return []
    candidates = []
    # SSH config can include complex Match/Include rules: this list is a UX aid, not an SSH parser.
    for line in config.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if line.lower().startswith("host "):
            for part in line.split()[1:]:
                if HOST.fullmatch(part):
                    candidates.append(part)
    return sorted(set(candidates))[:120]


def ssh_binary() -> str:
    binary = shutil.which("ssh")
    if not binary:
        raise RuntimeError("System OpenSSH client is not available")
    return binary


def diagnostics(alias: str, timeout: float = 12.0) -> dict:
    alias = validate_alias(alias)
    command = "uname -s; uname -m; free -b | head -n 2; command -v nvidia-smi >/dev/null && nvidia-smi --query-gpu=name --format=csv,noheader || true"
    cmd = [ssh_binary(), "-o", "StrictHostKeyChecking=yes", "-o", "BatchMode=yes", "-o", "ConnectTimeout=6", "--", alias, command]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "message": "SSH diagnostics timed out"}
    # Avoid leaking stderr (may include usernames/network details). Output from uname/free is bounded.
    return {"ok": result.returncode == 0, "result": result.stdout[:1800] if result.returncode == 0 else "", "message": "Connected" if result.returncode == 0 else "SSH connection failed. Verify key, host fingerprint and network access."}


class TunnelManager:
    def __init__(self):
        self._lock = threading.RLock()
        self._processes: dict[int, subprocess.Popen] = {}

    def start(self, alias: str, remote_port: int, local_port: int = 0) -> dict:
        alias = validate_alias(alias)
        if not 1 <= remote_port <= 65535:
            raise ValueError("Remote port must be 1–65535")
        if local_port and not 1024 <= local_port <= 65535:
            raise ValueError("Local port must be 1024–65535")
        if not local_port:
            with socket.socket() as s:
                s.bind(("127.0.0.1", 0))
                local_port = s.getsockname()[1]
        with self._lock:
            existing = self._processes.get(local_port)
            if existing and existing.poll() is None:
                raise ValueError("This local port is already managed")
            command = [ssh_binary(), "-N", "-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes",
                       "-o", "ExitOnForwardFailure=yes", "-o", "ConnectTimeout=7",
                       "-L", f"127.0.0.1:{local_port}:127.0.0.1:{remote_port}", "--", alias]
            process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.25)
            if process.poll() is not None:
                return {"ok": False, "message": "Tunnel ended early. Verify SSH access and host key."}
            self._processes[local_port] = process
        return {"ok": True, "local_port": local_port, "remote_port": remote_port, "alias": alias,
                "message": "SSH process started; confirm the model endpoint is reachable before sending data."}

    def status(self) -> list[dict]:
        with self._lock:
            return [{"local_port": port, "active": process.poll() is None} for port, process in self._processes.items()]

    def stop(self, port: int) -> bool:
        with self._lock:
            process = self._processes.pop(port, None)
        if not process:
            return False
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        return True

    def close(self):
        for row in self.status():
            self.stop(row["local_port"])
