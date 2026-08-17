# Aurorium Mind evidence

This directory contains publishable training and deployment evidence only. The
training rows, checkpoints, credentials, and raw conversation exports are not
part of this repository. The authoritative full artifacts remain in the
encrypted AWS S3 artifact bucket.

Evidence includes aggregate metrics, checksums, deployment configuration
metadata, and a lightweight SVG graph. The TensorBoard event file is included
when available; it contains scalar telemetry rather than training rows. Start
with [`live-status.md`](live-status.md) for the latest verified AWS, vLLM,
FastAPI, Rust, Caddy, Vercel, GPU, and Hugging Face publication status.

The adapter is publicly available at:
https://huggingface.co/auro-rirum/aurorium-mind-qwen35-4b-qlora
