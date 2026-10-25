from __future__ import annotations

import argparse
import socket
import threading
import webbrowser

import uvicorn
from .server import create_app


def open_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def main():
    p = argparse.ArgumentParser(description="SparkPrivacy — local AI data protection")
    p.add_argument("--no-browser", action="store_true")
    p.add_argument("--port", type=int, default=0)
    args = p.parse_args()
    port = args.port or open_port()
    if not args.no_browser:
        threading.Timer(1.1, lambda: webbrowser.open(f"http://127.0.0.1:{port}/")).start()
    print(f"SparkPrivacy is running locally at http://127.0.0.1:{port}/ (Ctrl+C to stop)")
    uvicorn.run(create_app(), host="127.0.0.1", port=port, access_log=False, log_level="warning")


if __name__ == "__main__":
    main()
