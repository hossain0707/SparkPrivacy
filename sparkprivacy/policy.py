"""Small, auditable policy engine. Default is block secrets and redact personal data."""
from __future__ import annotations

from dataclasses import dataclass
from .scanner import Finding, scan_text, redact_text, summary

ACTIONS = ("block", "redact", "monitor")
CATEGORIES = ("api_key", "email", "phone", "payment_card", "korean_rrn", "us_ssn")
DEFAULT_ACTIONS = {
    "api_key": "block",
    "email": "redact",
    "phone": "redact",
    "payment_card": "block",
    "korean_rrn": "block",
    "us_ssn": "block",
}

@dataclass(frozen=True)
class Decision:
    disposition: str
    sanitized: str | None
    categories: dict[str, int]
    finding_count: int
    high_risk: bool

    def public(self) -> dict:
        return {"disposition": self.disposition, "sanitized": self.sanitized, "categories": self.categories,
                "finding_count": self.finding_count, "high_risk": self.high_risk}


def validate_actions(actions: dict) -> dict[str, str]:
    if not isinstance(actions, dict) or set(actions) != set(CATEGORIES):
        raise ValueError("Actions must include each supported category exactly once")
    if any(action not in ACTIONS for action in actions.values()):
        raise ValueError("Only block, redact and monitor actions are supported")
    return dict(actions)


def decide(text: str, actions: dict[str, str] | None = None) -> Decision:
    actions = validate_actions(actions or DEFAULT_ACTIONS)
    findings = scan_text(text)
    blocked = any(actions[f.category] == "block" for f in findings)
    high_risk = any(f.severity in {"high", "critical"} for f in findings)
    if blocked:
        # Avoid returning even partial original content on block.
        return Decision("blocked", None, summary(findings), len(findings), high_risk)
    sanitized = redact_text(text, [f for f in findings if actions[f.category] == "redact"])
    status = "redacted" if sanitized != text else ("observed" if findings else "allowed")
    return Decision(status, sanitized, summary(findings), len(findings), high_risk)
