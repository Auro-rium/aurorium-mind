# Fine-tuning evidence bundle

This bundle contains reproducible metadata and logs for the Aurorium Mind
QLoRA run. It intentionally excludes dataset rows, model weights, checkpoints,
and credentials.

## Run

- Base model: `Qwen/Qwen3.5-4B`
- Method: supervised fine-tuning with QLoRA
- Train split: 100,000 procedural-synthetic examples
- Disjoint evaluation split: 2,000 examples
- Epochs: 1
- Batch size: 64, gradient accumulation: 1
- Maximum sequence length: 512 during training
- Hardware: one AWS `g5.2xlarge` / NVIDIA A10G in `us-east-2`
- Final global step: 1,563
- Final eval loss: 0.05661
- Final eval token accuracy: 0.9771
- Adapter SHA-256: `0fba57e246ed38cd6a7ea5b040553079ba9f691e8afb52a8834182efbe0cb464`

## Included

- `manifests/train-100k-manifest.json`: counts, source-shard proportions, and
  SHA-256 identifiers without rows
- `checkpoints/trainer_state-*.json`: trainer log history at checkpoint steps
- `logs/full-100k-train-final.log`: complete sanitized training log
- `logs/qlora-smoke.log`: smoke-test log

The authoritative full artifacts remain in encrypted AWS S3. The adapter is
served internally as the `aurorium` LoRA module on top of the base model; the
public API exposes FastAPI rather than the internal vLLM model route. The
published adapter is available at
https://huggingface.co/auro-rirum/aurorium-mind-qwen35-4b-qlora.
