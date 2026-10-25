from __future__ import annotations

import os
from pathlib import Path


def app_data_dir() -> Path:
    """Private user data location. Never place secrets in the Git working tree."""
    override = os.environ.get("SPARKPRIVACY_DATA_DIR")
    folder = Path(override).expanduser() if override else Path.home() / ".sparkprivacy"
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    if os.name != "nt":
        folder.chmod(0o700)
    return folder


def frontend_dir() -> Path:
    return Path(__file__).resolve().parent / "frontend"
