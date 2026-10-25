"""Metadata-only audit store. No original prompts, model outputs or credentials saved."""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from .policy import DEFAULT_ACTIONS, validate_actions


class Store:
    def __init__(self, file: Path):
        self.path = Path(file)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(str(self.path), check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        with self.lock:
            self.db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, at TEXT NOT NULL, channel TEXT NOT NULL,
                disposition TEXT NOT NULL, categories_json TEXT NOT NULL, count INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            """)
            self.db.commit()
        if os.name != "nt":
            self.path.chmod(0o600)

    def get_actions(self) -> dict[str, str]:
        with self.lock:
            row = self.db.execute("SELECT value FROM config WHERE key='policy'").fetchone()
        return validate_actions(json.loads(row[0])) if row else dict(DEFAULT_ACTIONS)

    def set_actions(self, actions: dict[str, str]):
        actions = validate_actions(actions)
        with self.lock:
            self.db.execute("INSERT INTO config (key,value) VALUES ('policy',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (json.dumps(actions),))
            self.db.commit()

    def event(self, channel: str, disposition: str, categories: dict[str, int], count: int) -> str:
        if channel not in {"inspector", "gateway_request", "gateway_response"}:
            raise ValueError("Invalid audit channel")
        if disposition not in {"allowed", "blocked", "redacted", "observed", "error"}:
            raise ValueError("Invalid disposition")
        eid = str(uuid.uuid4())
        at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self.lock:
            self.db.execute("INSERT INTO events VALUES (?,?,?,?,?,?)", (eid, at, channel, disposition, json.dumps(categories, sort_keys=True), count))
            self.db.commit()
        return eid

    def events(self, limit: int = 200) -> list[dict]:
        with self.lock:
            rows = self.db.execute("SELECT * FROM events ORDER BY at DESC, rowid DESC LIMIT ?", (max(1, min(limit, 500)),)).fetchall()
        return [{**dict(r), "categories": json.loads(r["categories_json"])} for r in rows]

    def statistics(self) -> dict:
        with self.lock:
            grouped = self.db.execute("SELECT disposition, count(*) as total FROM events GROUP BY disposition").fetchall()
            count = self.db.execute("SELECT count(*) FROM events").fetchone()[0]
        by_status = {r["disposition"]: r["total"] for r in grouped}
        return {"total": count, "blocked": by_status.get("blocked", 0), "redacted": by_status.get("redacted", 0),
                "allowed": by_status.get("allowed", 0), "observed": by_status.get("observed", 0), "errors": by_status.get("error", 0)}

    def purge(self, days: int):
        if not 0 <= days <= 3650:
            raise ValueError("Retention days must be between 0 and 3650")
        with self.lock:
            if days == 0:
                cursor = self.db.execute("DELETE FROM events")
            else:
                cursor = self.db.execute("DELETE FROM events WHERE at < strftime('%Y-%m-%dT%H:%M:%S', 'now', '-' || ? || ' days')", (days,))
            self.db.commit()
        return max(cursor.rowcount, 0)

    def close(self):
        self.db.close()
