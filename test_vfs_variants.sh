#!/usr/bin/env bash
set -u
echo "=== Минимальная VFS ==="
python3 main.py --vfs vfs_examples/minimal --script scripts/test_stage3.txt </dev/null
echo "=== VFS с несколькими файлами ==="
python3 main.py --vfs vfs_examples/files --script scripts/test_stage3.txt </dev/null
echo "=== Вложенная VFS ==="
python3 main.py --vfs vfs_examples/nested --script scripts/test_stage3.txt </dev/null
