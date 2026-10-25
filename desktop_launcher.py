"""Portable desktop entry point. PyInstaller includes Python and frontend assets."""
from __future__ import annotations

import argparse
import json
import sys
import socket
import threading
import time
import urllib.request
import webbrowser


def self_test() -> dict:
    from sparkprivacy.server import create_app
    from sparkprivacy.paths import frontend_dir
    from sparkprivacy.scanner import scan_text
    files = ["index.html", "styles.css", "app.js", "mark.svg"]
    missing = [name for name in files if not (frontend_dir() / name).is_file()]
    return {"ok": not missing and len(scan_text("person@example.org")) == 1, "missing": missing}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        info = self_test()
        if sys.stdout is not None:
            print(json.dumps(info))
        raise SystemExit(0 if info["ok"] else 2)

    from sparkprivacy.server import create_app
    from sparkprivacy.__main__ import open_port
    import uvicorn
    port = open_port()
    app = create_app()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, access_log=False, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{port}/"
    for _ in range(80):
        try:
            with urllib.request.urlopen(url + "health", timeout=0.3) as r:
                if r.status == 200:
                    break
        except Exception:
            time.sleep(0.15)
    else:
        raise RuntimeError("Local SparkPrivacy service did not start")
    try:
        try:
            import webview
        except ImportError:
            webbrowser.open(url)
            print(f"SparkPrivacy: {url}")
            thread.join()
        else:
            webview.create_window("SparkPrivacy — Private AI Security", url, width=1360, height=870, min_size=(980, 670))
            webview.start()
    finally:
        app.state.tunnels.close()
        server.should_exit = True
        thread.join(timeout=5)


if __name__ == "__main__":
    main()
