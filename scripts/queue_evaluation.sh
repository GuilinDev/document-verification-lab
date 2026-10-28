#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for attempt in $(seq 1 180); do
  if [ -f results/ocr.jsonl ] && [ "$(wc -l < results/ocr.jsonl)" -eq 120 ]; then break; fi
  sleep 10
done
test "$(wc -l < results/ocr.jsonl)" -eq 120
.render/bin/python scripts/render_candidates.py > logs/render.log 2>&1
nice -n 10 .venv/bin/python scripts/run_verifier.py > logs/verifier.log 2>&1
echo EVALUATION_COMPLETE
