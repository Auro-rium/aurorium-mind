#!/usr/bin/env python3
"""Make traceable persona SFT rows without synthetic targets or padding."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


def valid(text: str) -> bool:
    return 80 <= len(text) <= 6000 and "[REDACTED_SECRET]" not in text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--minimum-examples", type=int, default=100_000)
    args = parser.parse_args()
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    rows: list[dict] = []
    for line in args.input.read_text(encoding="utf-8").splitlines():
        item = json.loads(line)
        target = item["text"].strip()
        digest = hashlib.sha256(target.encode()).hexdigest()
        if digest in seen or not valid(target):
            continue
        seen.add(digest)
        counts[item["source"]] += 1
        # The target is verbatim human-authored text; the framing is explicit
        # so reviewers know this is context-derived, not a real user prompt.
        rows.append({
            "messages": [
                {"role": "system", "content": "Respond in Ishan's direct, evidence-first working style. Do not claim personal experiences you cannot ground."},
                {"role": "user", "content": "Continue the discussion with a concise, concrete response in the demonstrated writing style."},
                {"role": "assistant", "content": target},
            ],
            "provenance": {"kind": "human_authored_context_derived", "source": item["source"], "source_sha256": item["source_sha256"], "line": item["line"]},
        })
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = {"usable_examples": len(rows), "minimum_examples": args.minimum_examples, "by_source": dict(counts), "synthetic_targets": 0, "status": "ready" if len(rows) >= args.minimum_examples else "insufficient"}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    if len(rows) < args.minimum_examples:
        raise SystemExit("Insufficient real examples: import more user-owned source material; do not pad.")


if __name__ == "__main__":
    main()
