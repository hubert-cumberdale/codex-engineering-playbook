from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Dict, Tuple

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_IPV4_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# A simplistic “token” heuristic: long base-ish strings (letters/numbers/_-)
_TOKEN_RE = re.compile(r"\b[A-Za-z0-9_-]{20,}\b")


@dataclass(frozen=True)
class RedactionResult:
    redacted_text: str
    counts: Dict[str, int]
    input_sha256: str
    output_sha256: str


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def redact_text(text: str) -> Tuple[str, Dict[str, int]]:
    counts = {"email": 0, "ipv4": 0, "token": 0}

    def sub_email(match: re.Match[str]) -> str:
        counts["email"] += 1
        return "[REDACTED_EMAIL]"

    def sub_ipv4(match: re.Match[str]) -> str:
        counts["ipv4"] += 1
        return "[REDACTED_IPV4]"

    def sub_token(match: re.Match[str]) -> str:
        counts["token"] += 1
        return "[REDACTED_TOKEN]"

    out = _EMAIL_RE.sub(sub_email, text)
    out = _IPV4_RE.sub(sub_ipv4, out)
    out = _TOKEN_RE.sub(sub_token, out)
    return out, counts


def redact_with_evidence(text: str) -> RedactionResult:
    inp_hash = _sha256_bytes(text.encode("utf-8"))
    out_text, counts = redact_text(text)
    out_hash = _sha256_bytes(out_text.encode("utf-8"))
    return RedactionResult(
        redacted_text=out_text,
        counts=counts,
        input_sha256=inp_hash,
        output_sha256=out_hash,
    )