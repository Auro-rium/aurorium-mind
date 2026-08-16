#!/usr/bin/env python3
"""Report grounded concept prevalence without printing private corpus text."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

TERMS = {"transhumanism": r"transhuman", "second_order": r"second.?order", "inversion": r"inversion", "game_theory": r"game.?theor", "first_principles": r"first.?princip"}
parser = argparse.ArgumentParser(); parser.add_argument("--input", type=Path, required=True); parser.add_argument("--out", type=Path, required=True); args = parser.parse_args()
counts = {name: 0 for name in TERMS}
for line in args.input.read_text(encoding="utf-8").splitlines():
    text = json.loads(line).get("text", "")
    for name, pattern in TERMS.items(): counts[name] += bool(re.search(pattern, text, re.I))
args.out.write_text(json.dumps({"records_with_term": counts}, indent=2) + "\n", encoding="utf-8")
print(json.dumps(counts))
