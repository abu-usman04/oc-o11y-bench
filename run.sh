#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
export PYTHONUTF8=1
export UV_CACHE_DIR="$PWD/.work/uv-cache"
export UV_PYTHON_INSTALL_DIR="$PWD/.work/python"
export TMPDIR="$PWD/.work/tmp"
mkdir -p "$TMPDIR"
if [[ ! -d upstream/o11y-bench/.git ]]; then
  git clone --config core.autocrlf=false --no-checkout https://github.com/grafana/o11y-bench.git upstream/o11y-bench
fi
git -C upstream/o11y-bench checkout --detach b66d8cfbbe309d2e03e9a301baea056d9718b71b
uv sync --locked --python 3.14
uv run --no-sync python -m opencluster_bench "$@"
