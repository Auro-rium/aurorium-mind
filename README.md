# Aurorium Mind

Aurorium Mind is a QLoRA SFT deployment of `Qwen/Qwen3.5-4B`, served through
vLLM, a Rust gateway, FastAPI, and Caddy, with a Next.js/Vercel workspace UI.

## Live links

- Frontend: https://aurorium-mind.vercel.app
- GitHub: https://github.com/Auro-rium/aurorium-mind
- Intended API host: https://3.134.167.80.sslip.io

## Evidence

See [`artifacts/training-summary.md`](artifacts/training-summary.md) for the
run configuration, aggregate metrics, checksums, and deployment boundary. The
SVG graph is [`artifacts/training-metrics.svg`](artifacts/training-metrics.svg).

The complete logs, TensorBoard events, evaluation outputs, and checkpoints are
preserved in encrypted AWS S3. Dataset rows, raw conversation exports, adapter
weights, and secrets are intentionally excluded from this repository.

## Hugging Face

The adapter publisher is [`code/deploy/push_private_adapter.py`](code/deploy/push_private_adapter.py).
Publishing is deliberately gated on a secure `HF_TOKEN` supplied through the
AWS credential store; no token is accepted from chat or committed to GitHub.
