#!/usr/bin/env python3
"""Extract only human-authored Codex turns with deterministic redaction.

Raw session files are read in place. The output is private training material;
it contains a source hash, never the original absolute path or session ID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

SECRET_PATTERNS = (
    re.compile(r"\b(?:hf|ghp|github_pat|sk|AKIA)[A-Za-z0-9_-]{16,}\b", re.I),
    re.compile(r"\b(?:aws_secret_access_key|api[_-]?key|token|password)\s*[:=]\s*\S+", re.I),
    re.compile(r"-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----.*?-----END(?: [A-Z]+)? PRIVATE KEY-----", re.S),
)


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED_SECRET]", text)
    return text.strip()


def text_content(content: object) -> str:
    if not isinstance(content, list):
        return ""
    return "\n".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict) and block.get("type") in {"input_text", "output_text", "text"}
    )


def iter_user_turns(session: Path):
    raw = session.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    for line_number, line in enumerate(raw.splitlines(), start=1):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") != "response_item":
            continue
        payload = event.get("payload", {})
        if payload.get("type") != "message" or payload.get("role") != "user":
            continue
        body = redact(text_content(payload.get("content")))
        if body:
            yield {"source": "codex", "source_sha256": source_hash, "line": line_number, "text": body}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sessions-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with args.out.open("w", encoding="utf-8") as out:
        for path in sorted(args.sessions_root.rglob("*.jsonl")):
            for row in iter_user_turns(path):
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                count += 1
    print(json.dumps({"written": count, "out": str(args.out)}))


if __name__ == "__main__":
    main()
