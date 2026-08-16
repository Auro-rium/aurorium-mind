#!/usr/bin/env bash
set -euo pipefail

out_dir=${1:-/opt/aurorium-mind/telemetry-host}
mkdir -p "$out_dir"
while true; do
  line=$(nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw --format=csv,noheader,nounits 2>/dev/null | head -n1 || true)
  if [[ -n "$line" ]]; then
    IFS=',' read -r name util used total temp power <<< "$line"
    name=$(echo "$name" | xargs); util=$(echo "$util" | xargs); used=$(echo "$used" | xargs); total=$(echo "$total" | xargs); temp=$(echo "$temp" | xargs); power=$(echo "$power" | xargs)
    printf '{"available":true,"gpu":"%s","utilizationPct":%s,"memoryUsedMiB":%s,"memoryTotalMiB":%s,"temperatureC":%s,"powerW":%s,"timestampMs":%s}\n' "$name" "$util" "$used" "$total" "$temp" "$power" "$(date +%s%3N)" > "$out_dir/gpu.json.tmp"
    mv "$out_dir/gpu.json.tmp" "$out_dir/gpu.json"
  fi
  sleep 5
done
