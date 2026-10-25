"""Cross-platform desktop launcher for SparkPrivacy.

The Windows PyInstaller --windowed build has no console streams. Uvicorn's
standard logging config assumes sys.stdout.isatty() exists, so the native
launcher deliberately disables that config and verifies the actual HTTP
server on all distribution builds rather than just importing package files.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


def self_test() -> dict:
    from sparkprivacy.paths import frontend_dir
    from sparkprivacy.scanner import scan_text

    files = ("index.html", "styles.css", "app.js", "mark.svg")
    missing = [name for name in files if not (frontend_dir() / name).is_file()]
    return {"ok": not missing and len(scan_text("person@example.org")) == 1, "missing": missing}


def make_uvicorn_config(app, port: int):
    """Avoid uvicorn's terminal-only formatter in consoleless GUI builds."""
    import uvicorn

    return uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        access_log=False,
        log_level="warning",
        log_config=None,
    )


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _start_server(app, port: int):
    import uvicorn

    server = uvicorn.Server(make_uvicorn_config(app, port))
    errors: list[str] = []

    def serve() -> None:
        try:
            server.run()
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")

    thread = threading.Thread(target=serve, name="sparkprivacy-local-server", daemon=True)
    thread.start()
    return server, thread, errors


def _wait_for_ready(port: int, thread: threading.Thread, errors: list[str], timeout: float = 12.0) -> None:
    url = f"http://127.0.0.1:{port}/health"
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if errors:
            raise RuntimeError("Local server failed to start: " + errors[0])
        if not thread.is_alive():
            raise RuntimeError("Local server stopped before responding")
        try:
            with urllib.request.urlopen(url, timeout=0.4) as response:
                data = json.load(response)
                if response.status == 200 and data.get("status") == "ready":
                    return
        except (OSError, ValueError, TimeoutError):
            time.sleep(0.12)
    raise RuntimeError("Local SparkPrivacy server did not become ready")


def _stop_server(app, server, thread: threading.Thread) -> None:
    try:
        app.state.tunnels.close()
    finally:
        server.should_exit = True
        thread.join(timeout=5)


def startup_self_test() -> dict:
    """Exercise an actual bundled HTTP server, even when stdout/stderr are None."""
    from sparkprivacy.server import create_app

    with tempfile.TemporaryDirectory(prefix="sparkprivacy-launch-check-") as temp:
        port = _free_port()
        app = create_app(data_dir=Path(temp))
        server, thread, errors = _start_server(app, port)
        try:
            _wait_for_ready(port, thread, errors)
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3) as page:
                markup = page.read()
                if page.status != 200 or b"SparkPrivacy" not in markup:
                    raise RuntimeError("Desktop homepage check failed")
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/static/app.js", timeout=3) as asset:
                if asset.status != 200 or not asset.read():
                    raise RuntimeError("Bundled frontend asset check failed")
            return {"ok": True, "backend_ready": True, "frontend_ready": True, "consoleless_safe": True}
        finally:
            _stop_server(app, server, thread)


def _save_result(path: Path, details: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(details, sort_keys=True), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true", help="Check bundled package assets")
    parser.add_argument(
        "--startup-self-test", type=Path, metavar="REPORT.json",
        help="Start HTTP backend without opening a window and write verification to a JSON report",
    )
    args = parser.parse_args()

    if args.self_test:
        details = self_test()
        if sys.stdout is not None:
            print(json.dumps(details))
        raise SystemExit(0 if details["ok"] else 2)

    if args.startup_self_test is not None:
        try:
            details = startup_self_test()
        except Exception as exc:
            details = {"ok": False, "error": f"{type(exc).__name__}: {exc}"}
        _save_result(args.startup_self_test, details)
        raise SystemExit(0 if details["ok"] else 2)

    from sparkprivacy.server import create_app

    port = _free_port()
    app = create_app()
    server, thread, errors = _start_server(app, port)
    try:
        _wait_for_ready(port, thread, errors)
        url = f"http://127.0.0.1:{port}/"
        try:
            import webview
        except ImportError:
            webbrowser.open(url)
            if sys.stdout is not None:
                print(f"SparkPrivacy: {url}")
            thread.join()
        else:
            webview.create_window(
                "SparkPrivacy — Private AI Security", url,
                width=1360, height=870, min_size=(980, 670),
            )
            webview.start()
    finally:
        _stop_server(app, server, thread)


if __name__ == "__main__":
    main()
