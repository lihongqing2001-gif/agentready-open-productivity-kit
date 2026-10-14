#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$ROOT/agentready.py" "$@"
fi
echo "Python 3 is required. Install it from a trusted source, then rerun." >&2
exit 2
