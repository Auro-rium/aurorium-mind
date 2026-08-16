#!/usr/bin/env python3
"""Collect bounded, user-owned public context without turning it into SFT targets."""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
from pathlib import Path


def gh_json(path: str) -> object:
    result = subprocess.run(["gh", "api", path], check=True, text=True, capture_output=True)
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default="Auro-rium")
    parser.add_argument("--website-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    records: list[dict[str, str]] = []
    for repo in gh_json(f"users/{args.owner}/repos?per_page=100&type=owner"):
        name = repo["full_name"]
        try:
            readme = gh_json(f"repos/{name}/readme")
            body = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")
        except subprocess.CalledProcessError:
            body = ""
        records.append({"kind": "github_readme", "repo": name, "url": repo["html_url"], "text": body[:100_000]})
    excluded = {"node_modules", ".git", "dist", ".next"}
    for path in args.website_root.rglob("*"):
        if any(part in excluded for part in path.parts):
            continue
        if path.is_file() and path.suffix in {".ts", ".tsx", ".md", ".html"}:
            records.append({"kind": "website_source", "repo": "aurorium-nexus", "url": str(path.relative_to(args.website_root)), "text": path.read_text(encoding="utf-8", errors="replace")[:100_000]})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps({"records": len(records), "out": str(args.out)}))


if __name__ == "__main__":
    main()
