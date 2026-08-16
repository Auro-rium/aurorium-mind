"""Create an auditable, balanced subset from the six procedural-synthetic shards."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--eval-out", type=Path)
    parser.add_argument("--eval-examples", type=int, default=2_000)
    parser.add_argument("--examples", type=int, default=100_000)
    args = parser.parse_args()
    source_names = {"first_principles.jsonl", "game_theory.jsonl", "pragmatic_systems.jsonl", "second_order_inversion.jsonl", "speculative_transhumanism.jsonl", "systems_thinking.jsonl"}
    shards = sorted(path for path in args.input_dir.glob("*.jsonl") if path.name in source_names)
    if not shards:
        raise SystemExit("no JSONL shards found")
    per, remainder = divmod(args.examples, len(shards))
    quotas = {shard: per + (index < remainder) for index, shard in enumerate(shards)}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    selected: list[dict[str, object]] = []
    with args.out.open("w", encoding="utf-8") as destination:
        for shard in shards:
            count = 0
            with shard.open("r", encoding="utf-8") as source:
                for line in source:
                    if count == quotas[shard]:
                        break
                    destination.write(line)
                    count += 1
            if count != quotas[shard]:
                raise SystemExit(f"{shard.name} had only {count} rows; expected {quotas[shard]}")
            selected.append({"source_shard": shard.stem, "examples": count})
    eval_manifest: dict[str, object] | None = None
    if args.eval_out:
        eval_per, eval_remainder = divmod(args.eval_examples, len(shards))
        eval_quotas = {shard: eval_per + (index < eval_remainder) for index, shard in enumerate(shards)}
        with args.eval_out.open("w", encoding="utf-8") as destination:
            for shard in shards:
                skip = quotas[shard]
                take = eval_quotas[shard]
                with shard.open("r", encoding="utf-8") as source:
                    for _ in range(skip):
                        next(source)
                    for _ in range(take):
                        destination.write(next(source))
        eval_manifest = {"examples": args.eval_examples, "sha256": digest(args.eval_out), "provenance": "rows immediately after the balanced training prefixes; disjoint from train"}
    manifest = {
        "total_examples": args.examples,
        "status": "procedural_synthetic_ready",
        "provenance": "balanced deterministic prefix selection from six procedural-synthetic source shards",
        "human_authored_examples": 0,
        "subset_sha256": digest(args.out),
        "shards": selected,
    }
    if eval_manifest:
        manifest["evaluation"] = eval_manifest
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
