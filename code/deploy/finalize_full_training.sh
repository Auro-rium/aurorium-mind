#!/usr/bin/env bash
# Guarded handoff for the 100k run. It is safe to leave running while the main
# trainer works: it exports only after a successful train summary is present.
set -Eeuo pipefail

root=/opt/aurorium-mind
main_pid_file="$root/full-train.pid"
main_log=/var/log/aurorium-mind/full-100k-train.log
final_log=/var/log/aurorium-mind/full-100k-finalize.log
output="$root/full-100k-output"
bucket=aurorium-mind-145023103669-us-east-2

while pid=$(cat "$main_pid_file" 2>/dev/null) && kill -0 "$pid" 2>/dev/null; do
  sleep 60
done

if ! tr '\r' '\n' < "$main_log" | grep -q 'train_runtime'; then
  echo "main training did not produce a successful train summary; refusing export" | tee -a "$final_log"
  exit 1
fi

if [[ -f "$output/adapter_model.safetensors" && -f "$output/adapter_config.json" ]]; then
  echo "adapter already exported" | tee -a "$final_log"
  exit 0
fi

checkpoint=$(find "$output" -maxdepth 1 -type d -name 'checkpoint-*' -printf '%f\n' | sort -V | tail -n 1)
if [[ -z "$checkpoint" ]]; then
  echo "no checkpoint available after successful run; refusing export" | tee -a "$final_log"
  exit 1
fi

cd "$root"
source .venv/bin/activate
python code/train_qlora.py \
  --train data/train-100k.jsonl \
  --eval holdout/eval-2k-disjoint.jsonl \
  --data-report data/train-100k-manifest.json \
  --allow-synthetic-prompt-augmentation \
  --output "$output" \
  --epochs 1 \
  --max-steps 1563 \
  --resume-from-checkpoint "$output/$checkpoint" \
  --per-device-train-batch-size 64 \
  --gradient-accumulation-steps 1 \
  --max-length 512 \
  --telemetry-dir "$root/telemetry/tensorboard-full-100k" \
  >> "$final_log" 2>&1

test -s "$output/adapter_model.safetensors"
test -s "$output/adapter_config.json"
aws s3 sync "$output" "s3://$bucket/artifacts/full-100k-output/" --sse AES256 --no-progress
aws s3 cp "$final_log" "s3://$bucket/telemetry/full-100k-finalize.log" --sse AES256 --no-progress
echo "adapter export complete" | tee -a "$final_log"
