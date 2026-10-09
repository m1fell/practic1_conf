#!/usr/bin/env bash
set -u
echo "=== Проверка --vfs ==="
python3 main.py --vfs vfs_examples/minimal --script scripts/test_stage1.txt </dev/null
echo "=== Проверка --script ==="
python3 main.py --script scripts/test_stage2.txt </dev/null
echo "=== Проверка --config ==="
python3 main.py --config config/config.yaml </dev/null
echo "=== Проверка неверного параметра VFS ==="
python3 main.py --vfs vfs_examples/does_not_exist </dev/null
echo "=== Проверка неверного стартового скрипта ==="
python3 main.py --vfs vfs_examples/minimal --script scripts/not_found.txt </dev/null
