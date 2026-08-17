# Aurorium Mind — verified live status

Snapshot date: 2026-08-17 (Asia/Kolkata)

This is an evidence snapshot, not a continuously updated dashboard. Values below
are measurements or configuration observed from the deployed paths at snapshot
time. The GPU sample was idle; it is not a peak-load benchmark.

## Training and evaluation

| Metric | Verified value |
|---|---|
| Base model | `Qwen/Qwen3.5-4B` |
| Method | QLoRA / SFT |
| Training set | 100,000 synthetic examples |
| Evaluation set | 2,000 disjoint examples |
| Epochs | 1 |
| Batch / gradient accumulation | 64 / 1 |
| Training max sequence | 512 tokens |
| Final train loss | 0.2158 |
| Final eval loss | 0.05661 |
| Final eval token accuracy | 0.9771 |
| Runtime | approximately 13h58m |
| Adapter SHA-256 | `0fba57e246ed38cd6a7ea5b040553079ba9f691e8afb52a8834182efbe0cb464` |

## Serving and inference

| Metric | Verified value |
|---|---|
| AWS instance | `g5.2xlarge` |
| Availability zone | `us-east-2b` |
| GPU | NVIDIA A10G |
| vLLM context | 8,192 tokens |
| Frontend/API output budget | up to 4,096 tokens, subject to remaining context |
| Internal model IDs | `qwen35-base`, `aurorium` adapter |
| Public model route | FastAPI only; the internal vLLM `/v1/models` route is not exposed publicly |
| Containers | vLLM, Caddy, FastAPI, Rust gateway all running |
| HTTPS health | `https://3.134.167.80.sslip.io/health` returned HTTP 200 |

The observed idle GPU sample was **0% utilization, 20,019 / 23,028 MiB VRAM,
38°C, 61.55 W**. These values change with traffic.

## Frontend and deployment

- Frontend: https://aurorium-mind.vercel.app
- Explainer: https://aurorium-mind.vercel.app/explainer.html
- Verified production deployment: `aurorium-mind-jav2kkvcl-auroriumnexus-6067s-projects.vercel.app`
- Deployment status: Ready / Production
- Git commit: `0dd819e` (`expand context budget and refresh chat interface`)
- UI includes streaming responses, token/TFT/TPS metrics, compact traces, GPU telemetry, and inference pipeline details.

## Model publication

- Public adapter: https://huggingface.co/auro-rirum/aurorium-mind-qwen35-4b-qlora
- Public synthetic dataset: https://huggingface.co/datasets/auro-rirum/aurorium-mind-sft-100k
- Published files: `adapter_model.safetensors`, `adapter_config.json`, `training_manifest.json`, `README.md`
- Excluded: raw data, conversation exports, checkpoints, base-model weights, and secrets.

## AWS security and storage

- Root volume: encrypted 300 GiB `gp3`, in use
- Inbound security group: TCP 443 only
- Management: AWS Systems Manager (SSM), not SSH
- Stable public endpoint: EIP `3.134.167.80`

## Evidence boundary

Sanitized logs, trainer state metadata, manifests, TensorBoard events, and
evaluation artifacts are retained in encrypted S3. This repository contains no
private corpus rows, credentials, or model weights.
