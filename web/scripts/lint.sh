#!/usr/bin/env bash
# ESLint entry point for pre-commit. Skips cleanly when web deps aren't installed
# so `make lint` still works for people who only touch the backend.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -d node_modules ]; then
  echo "eslint (web): skipped - run 'npm --prefix web install' to enable"
  exit 0
fi

exec npx eslint .
