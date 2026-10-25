"""Conservative, transparent pattern scanner. NOT a guarantee of complete DLP."""
from __future__ import annotations

from dataclasses import dataclass, asdict
import re

MAX_SCAN_CHARS = 100_000

@dataclass(frozen=True)
class Finding:
    category: str
    start: int
    end: int
    confidence: str
    severity: str

    def public(self) -> dict:
        return asdict(self)

# Avoid capturing entire credential in any log, database or exception.
PATTERNS = (
    ("api_key", r"(?<![a-zA-Z0-9])(?:sk-(?:proj-)?[a-zA-Z0-9_\-]{18,}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16})(?![A-Za-z0-9_])", "high", "critical"),
    ("email", r"(?<![\w.+-])[A-Za-z0-9._%+\-]{1,64}@[A-Za-z0-9.-]{1,200}\.[A-Za-z]{2,24}(?![\w.-])", "high", "medium"),
    ("korean_rrn", r"(?<!\d)\d{6}[\- ]?[1-8]\d{6}(?!\d)", "medium", "high"),
    ("us_ssn", r"(?<!\d)(?!000|666|9\d\d)\d{3}[- ](?!00)\d{2}[- ](?!0000)\d{4}(?!\d)", "medium", "high"),
    ("phone", r"(?<!\w)(?:\+?82[- ]?0?1[0-9][\- ]?\d{3,4}[\- ]?\d{4}|0?1[0-9][\- ]?\d{3,4}[\- ]?\d{4}|\+?1[- .]?(?:\(?\d{3}\)?)[- .]?\d{3}[- .]?\d{4})(?!\d)", "medium", "medium"),
    ("card_candidate", r"(?<![A-Za-z0-9])(?:\d[ -]?){12,18}\d(?![A-Za-z0-9])", "high", "high"),
)
COMPILED = tuple((category, re.compile(pattern, re.IGNORECASE), confidence, severity) for category, pattern, confidence, severity in PATTERNS)


def luhn_valid(raw: str) -> bool:
    digits = [int(c) for c in raw if c.isdigit()]
    if not 13 <= len(digits) <= 19 or len(set(digits)) == 1:
        return False
    total = 0
    for index, d in enumerate(reversed(digits)):
        if index % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def scan_text(text: str) -> list[Finding]:
    if not isinstance(text, str) or len(text) > MAX_SCAN_CHARS:
        raise ValueError("Text must be a string of at most 100,000 characters")
    candidates: list[Finding] = []
    for category, pattern, confidence, severity in COMPILED:
        for match in pattern.finditer(text):
            if category == "card_candidate" and not luhn_valid(match.group()):
                continue
            kind = "payment_card" if category == "card_candidate" else category
            candidates.append(Finding(kind, match.start(), match.end(), confidence, severity))
    # Prefer longer matches when detectors overlap; avoid partial redaction leaks.
    priority = {"api_key": 0, "payment_card": 1, "korean_rrn": 2, "us_ssn": 3, "phone": 4, "email": 5}
    candidates.sort(key=lambda f: (-(f.end - f.start), priority.get(f.category, 10), f.start))
    selected: list[Finding] = []
    for f in candidates:
        if not any(not (f.end <= s.start or f.start >= s.end) for s in selected):
            selected.append(f)
    return sorted(selected, key=lambda f: f.start)


def redact_text(text: str, findings: list[Finding]) -> str:
    result = []
    position = 0
    for finding in findings:
        result.extend((text[position:finding.start], f"[REDACTED:{finding.category.upper()}]"))
        position = finding.end
    result.append(text[position:])
    return "".join(result)


def summary(findings: list[Finding]) -> dict[str, int]:
    out: dict[str, int] = {}
    for f in findings:
        out[f.category] = out.get(f.category, 0) + 1
    return out
