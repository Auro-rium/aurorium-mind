# Aurorium Mind

A private personal-model stack for Ishan/Aurorium. The present training run is
explicitly based on six procedurally generated, synthetic 100k-row shards. It
must not be represented as a 600k-example archive of real conversations.
The source-building tools still preserve a strict route for future
human-authored data: source messages become assistant targets, every record
carries a source hash, and the build fails when the available corpus is below
the requested size.

## Architecture

`Vercel chat UI -> FastAPI -> Rust gateway -> vLLM -> Qwen/Qwen3.5-4B + QLoRA adapter`

FastAPI and the Rust gateway record privacy-safe telemetry (request ID, time,
latency, status, model ID, token counts when supplied). They never record
prompts, completions, cookies, authorization values, or raw corpus text.
QLoRA writes checkpoints plus TensorBoard scalar metrics beneath its output
directory, so training loss/evaluation state survives the instance lifecycle
without storing examples.

## Live serving limits

- vLLM context: 8,192 tokens
- Frontend output budget: up to 4,096 tokens, bounded by remaining context
- GPU: one NVIDIA A10G on AWS `g5.2xlarge` in `us-east-2b`
- Public frontend: https://aurorium-mind.vercel.app
- Public adapter: https://huggingface.co/auro-rirum/aurorium-mind-qwen35-4b-qlora
- Public backend health: https://3.134.167.80.sslip.io/health

The internal vLLM route loads `Qwen/Qwen3.5-4B` plus the `aurorium` adapter.
The base model and vLLM model-list route are not exposed through the public
HTTPS API.

## Corpus build

The source files remain local and are never committed. Run on the secure
training machine:

```bash
python corpus/extract_codex.py --sessions-root ~/.codex/sessions --out data/codex-user-turns.jsonl
python corpus/build_sft.py --input data/codex-user-turns.jsonl --out data/train.jsonl --report data/corpus-report.json --minimum-examples 100000
```

`build_sft.py` reports the real number of usable examples and exits non-zero
when it is below the requested threshold. It does not pad, paraphrase, or
synthetically expand the data. Add a user-owned ChatGPT data export through a
separate importer before lowering that threshold.

If explicitly approved, `synthesize_prompt_augmentations.py` produces a
separately labelled 100k-row set. It must be trained only with
`--allow-synthetic-prompt-augmentation`; its row count must never be described
as 100k independent real conversations.

`generate_pragmatic_synthetic_500k.py` creates six explicitly procedural
synthetic 100k-row shards: pragmatic systems, first principles,
second-order/inversion, systems thinking, game theory, and
speculative/transhumanist strategy.
Its rows are mechanically unique but are not a substitute for diverse,
teacher-generated or human-authored conversations.

## Sensitive material

Put the replacement HF write token in the instance's secret store (for example
AWS Secrets Manager or an operator-created root-only file), not in this repo,
Docker Compose, shell history, telemetry, or a chat message. Revoke the token
previously pasted into this chat.
