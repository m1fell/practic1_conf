#!/usr/bin/env bash
set -u
echo "=== YAML должен переопределить --vfs ==="
python3 main.py --vfs vfs_examples/minimal --config config/config.yaml </dev/null
echo "=== YAML должен переопределить --script ==="
python3 main.py --script scripts/test_stage1.txt --config config/config.yaml </dev/null
