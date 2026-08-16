# Aurorium Mind — run summary

| Field | Value |
|---|---|
| Base model | `Qwen/Qwen3.5-4B` |
| Method | QLoRA / SFT |
| Training split | 100,000 synthetic examples (not committed) |
| Evaluation split | 2,000 disjoint examples (not committed) |
| Epochs | 1 |
| Batch / accumulation | 64 / 1 |
| Max sequence length | 512 |
| Final train loss | 0.2158 |
| Final eval loss | 0.05661 |
| Final eval token accuracy | 0.9771 |
| Runtime | ~13h58m |
| Instance | AWS `g5.2xlarge` / NVIDIA A10G, `us-east-2` |
| Adapter SHA-256 | `0fba57e246ed38cd6a7ea5b040553079ba9f691e8afb52a8834182efbe0cb464` |

## Deployment evidence

- Frontend: https://aurorium-mind.vercel.app
- Backend host: `https://3.134.167.80.sslip.io`
- Runtime: vLLM + Rust gateway + FastAPI + Caddy
- Model repository: pending secure Hugging Face write credential; no token is
  stored in this repository.

The run's complete logs, checkpoints, evaluation outputs, and TensorBoard
events are preserved in the encrypted AWS S3 artifact bucket. This repository
deliberately contains no dataset rows or model weights.
