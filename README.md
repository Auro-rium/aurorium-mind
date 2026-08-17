# Aurorium Mind

Aurorium Mind is a QLoRA SFT deployment of `Qwen/Qwen3.5-4B`, served through
vLLM, a Rust gateway, FastAPI, and Caddy, with a Next.js/Vercel workspace UI.

## Live links

- Frontend: https://aurorium-mind.vercel.app
- Explainer: https://aurorium-mind.vercel.app/explainer.html
- GitHub: https://github.com/Auro-rium/aurorium-mind
- Intended API host: https://3.134.167.80.sslip.io

## Evidence

See [`artifacts/training-summary.md`](artifacts/training-summary.md) for the
run configuration, aggregate metrics, checksums, and deployment boundary. The
SVG graph is [`artifacts/training-metrics.svg`](artifacts/training-metrics.svg).
The expanded sanitized fine-tuning bundle is in [`artifacts/finetune/`](artifacts/finetune/), including trainer logs, checkpoint state metadata, and manifests. The latest verified runtime snapshot is [`artifacts/live-status.md`](artifacts/live-status.md).

The complete logs, TensorBoard events, evaluation outputs, and checkpoints are
preserved in encrypted AWS S3. Dataset rows, raw conversation exports, adapter
weights, and secrets are intentionally excluded from this repository.

## Hugging Face

The adapter is publicly published at [`auro-rirum/aurorium-mind-qwen35-4b-qlora`](https://huggingface.co/auro-rirum/aurorium-mind-qwen35-4b-qlora).
It contains only the adapter files, training manifest, and README; no dataset
rows, checkpoints, or base-model weights are published. The publisher remains
in [`code/deploy/push_private_adapter.py`](code/deploy/push_private_adapter.py)
and accepts credentials only through `HF_TOKEN` from a secure store.
