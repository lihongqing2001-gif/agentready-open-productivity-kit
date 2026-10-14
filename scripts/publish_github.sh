#!/usr/bin/env bash
# Explicit publication of an already audited, clean-history candidate.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
[[ "${1:-}" == "--apply" && $# == 1 ]] || {
  echo 'DRY RUN: requires clean audited Git tree, tests, gh authentication; use --apply to publish.'
  exit 0
}
[[ -z "$(git status --porcelain)" ]] || { echo 'Refusing dirty tree' >&2; exit 2; }
[[ ! -f docs/CODEX_OVERNIGHT.md && ! -f docs/HERMES_TRIAL_OVERNIGHT.md ]] || {
  echo 'Private handoff files must not be in a public candidate' >&2; exit 2;
}
python3 -m unittest discover -s tests -v
python3 scripts/audit_public.py
gh auth status
owner="$(gh api user --jq .login)"
repo="$owner/agentready-open-productivity-kit"
# Check the authenticated owner's repository list; API failures stop publication.
existing="$(gh repo list "$owner" --limit 1000 --json name --jq '.[].name')"
if [[ "$existing" == *'agentready-open-productivity-kit'* ]]; then
  echo "Repository exists: $repo. Review its ownership/history before any push." >&2
  exit 2
fi
gh repo create "$repo" --public --source . --remote origin
git push -u origin HEAD:main
gh repo view "$repo" --json url --jq .url
gh run list --repo "$repo" --limit 5
