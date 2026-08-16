#!/usr/bin/env python3
"""Publish only the final LoRA adapter to a Hugging Face model repo.

Authentication is accepted exclusively via HF_TOKEN in the process environment.
Do not pass tokens as arguments or put them in this file.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path

from huggingface_hub import HfApi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--adapter-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--repo-name", default="aurorium-mind-qwen35-4b-qlora")
    parser.add_argument("--staging-dir", default="/opt/aurorium-mind/hf-adapter-export", type=Path)
    parser.add_argument("--public", action="store_true", help="Create a public adapter repo; private is the default")
    args = parser.parse_args()

    if not os.environ.get("HF_TOKEN"):
        raise RuntimeError("HF_TOKEN must be injected from a secure credential store")
    required = ("adapter_model.safetensors", "adapter_config.json")
    missing = [name for name in required if not (args.adapter_dir / name).is_file()]
    if missing:
        raise RuntimeError(f"adapter export is incomplete: {', '.join(missing)}")

    if args.staging_dir.exists():
        shutil.rmtree(args.staging_dir)
    args.staging_dir.mkdir(parents=True)
    for name in required:
        shutil.copy2(args.adapter_dir / name, args.staging_dir / name)
    shutil.copy2(args.manifest, args.staging_dir / "training_manifest.json")
    (args.staging_dir / "README.md").write_text(
        """---
base_model: Qwen/Qwen3.5-4B
library_name: peft
tags:
- qlora
- lora
- synthetic-sft
---

# Aurorium Mind Qwen 3.5 4B QLoRA adapter

Private LoRA adapter for `Qwen/Qwen3.5-4B`. The training corpus is procedural
synthetic SFT data; it does not claim to contain private conversation exports.
Load it as adapter `aurorium` with a compatible Qwen 3.5 base model.
""",
        encoding="utf-8",
    )

    api = HfApi(token=os.environ["HF_TOKEN"])
    private = not args.public
    repo = api.create_repo(repo_id=args.repo_name, repo_type="model", private=private, exist_ok=True)
    api.upload_folder(
        repo_id=args.repo_name,
        repo_type="model",
        folder_path=str(args.staging_dir),
        commit_message="Publish verified Aurorium Mind QLoRA adapter",
    )
    repo_url = str(repo)
    Path(args.staging_dir / "publication.json").write_text(
        json.dumps({"repo_url": repo_url, "private": private}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"repo_url": repo_url, "private": private}))


if __name__ == "__main__":
    main()
