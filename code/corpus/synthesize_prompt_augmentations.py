#!/usr/bin/env python3
"""Create a declared synthetic 100k-row augmentation set from reviewed targets.

This is deliberately prompt augmentation, not fabricated autobiographical
content: assistant targets remain verbatim human-authored source text. The
report makes the effective number of independent targets explicit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

LENSES = ("first-principles reasoning", "second-order effects", "inversion", "game-theoretic incentives", "long-term and transhumanist implications")
FRAMES = ("Give the decisive next step.", "State the constraints and the proof boundary.", "Separate observed facts from assumptions.", "Optimize for a runnable outcome, not vague advice.", "Name the risk before proposing the move.")


def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--input", type=Path, required=True); p.add_argument("--out", type=Path, required=True); p.add_argument("--report", type=Path, required=True); p.add_argument("--target-size", type=int, default=100_000); args = p.parse_args()
    bases = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines()]
    if not bases: raise SystemExit("No reviewed base examples")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as handle:
        for i in range(args.target_size):
            base = bases[i % len(bases)]
            original = base["messages"][2]["content"]
            lens, frame = LENSES[(i // len(bases)) % len(LENSES)], FRAMES[(i // (len(bases) * len(LENSES))) % len(FRAMES)]
            prompt = f"Reply in Ishan's observed working style. Apply {lens}. {frame} Do not invent personal history."
            row = {"messages": [{"role":"system","content":"Be concrete, evidence-aware, and honest about uncertainty."}, {"role":"user","content":prompt}, {"role":"assistant","content":original}], "provenance": {"kind":"synthetic_prompt_augmentation_human_target", "base":base["provenance"], "augmentation_id":i}}
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    report = {"total_examples":args.target_size,"human_authored_targets":len(bases),"synthetic_prompt_augmentations":args.target_size-len(bases),"independent_target_upper_bound":len(bases),"synthetic_target_text":0,"status":"synthetic_augmentation_ready","dataset_sha256":hashlib.sha256(args.out.read_bytes()).hexdigest()}
    args.report.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8"); print(json.dumps(report))

if __name__ == "__main__": main()
