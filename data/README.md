# Aurorium Mind synthetic SFT dataset

This dataset contains the procedural synthetic data used for the Aurorium Mind
QLoRA/SFT run. It is intentionally **not** an export of Ishan/Aurorium's
private ChatGPT, Codex, website, or GitHub conversations.

## Splits

- `train-100k.jsonl.gz`: 100,000 training examples
- `eval-2k-disjoint.jsonl.gz`: 2,000 disjoint evaluation examples
- `train-100k.jsonl` and `eval-2k-disjoint.jsonl`: uncompressed copies for
  direct Hub/Dataset Viewer inspection
- `train-100k-manifest.json`: counts, provenance, and SHA-256 checksums

Each row contains `messages` plus a `provenance` object. Every provenance record
is labelled `procedural_synthetic` and `human_authored: false`. The source
shards cover first principles, game theory, pragmatic systems, second-order
effects/inversion, speculative transhumanism, and systems thinking.

## Philosophy

The corpus is organized around first-principles reasoning, inversion, second-
order effects, systems thinking, game theory, and pragmatic transhumanism. These
are reasoning lenses and design values—not claims that every generated answer is
true or that synthetic rows reproduce a person's private voice.

The split boundaries and checksums are preserved in the manifest. The dataset
contains no credentials, raw private conversation exports, model checkpoints,
or base-model weights.

## Intended use

This is a research/demo SFT corpus for reasoning-style experiments. It should
not be described as a collection of real user conversations or as evidence of
general factual accuracy.
