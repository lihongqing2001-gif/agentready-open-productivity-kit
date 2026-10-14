#!/usr/bin/env bash
# Explicit one-time unattended Codex launch for a user-owned working copy.
# By default dry-run; use --apply to actually launch. Does not bypass sandbox.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
usage() { echo "Usage: $0 /absolute/path/to/task.md [--apply]"; }
[[ $# -ge 1 && $# -le 2 ]] || { usage; exit 2; }
PROMPT="$1"; MODE="${2:-}"
[[ -f "$PROMPT" ]] || { echo "Prompt file not found" >&2; exit 2; }
if [[ -n "$MODE" && "$MODE" != "--apply" ]]; then usage; exit 2; fi
if ! command -v codex >/dev/null 2>&1; then echo "Codex CLI is not installed" >&2; exit 2; fi
HELP="$(codex --help 2>&1 || true)"
if [[ "$HELP" != *'--sandbox'* || "$HELP" != *'--ask-for-approval'* ]]; then
  echo "Unsupported Codex exec flags on this CLI; review 'codex exec --help' manually" >&2
  exit 2
fi
if [[ "$MODE" != "--apply" ]]; then
  echo "DRY RUN: would run codex exec in $ROOT using task $PROMPT" 
  echo "Sandbox: workspace-write; approvals: never; no bypass flags"
  exit 0
fi
umask 077
mkdir -p "$ROOT/.reports/agentready-night"
STAMP="$(date +%Y%m%d-%H%M%S)"
LOG="$ROOT/.reports/agentready-night/$STAMP.codex.log"
STATUS="$ROOT/.reports/agentready-night/$STAMP.status"
# The input is supplied via stdin, not command-line arguments. No secrets in prompt.
# Preserve the existing provider, model and credential resolver.
args=(--ask-for-approval never exec --sandbox workspace-write -C "$ROOT")
args+=(-)
(
  set +e
  codex "${args[@]}" < "$PROMPT" > "$LOG" 2>&1
  result=$?
  echo "exit_code=$result finished=$(date -u +%FT%TZ)" > "$STATUS"
  exit "$result"
) </dev/null >/dev/null 2>&1 &
PID=$!
echo "STARTED pid=$PID log=$LOG status_file=$STATUS"
echo "NOTE: the Mac must stay awake and authenticated; this script does not configure an OS service or bypass sleep."
