---
name: agentready-lark-brief
description: Generate a read-only Feishu work briefing with the user's existing lark-cli OAuth; works with Codex alone and does not require Hermes. Use when asked for a Feishu task/calendar status or daily brief.
---

# Lark CLI-first daily brief

Use the **existing** authenticated `lark-cli` executable. Do not create another Feishu app or Hermes service. If `lark-cli` is missing, show the official install guidance at https://github.com/larksuite/cli and mark blocked instead of installing unofficial lookalikes.

Run an offline preview first:

```bash
python3 agentready.py brief
```

When account identity, access scope, and local terminal are appropriate, perform read-only user OAuth data fetch:

```bash
python3 agentready.py brief --live --lark-profile YOUR_PROFILE --details
```

Optional explicitly scoped work message search:

```bash
python3 agentready.py brief --live --lark-profile YOUR_PROFILE --message-query "待办" --details
```

`--details` emits record titles and source links to the caller; omit when logging to shared terminals. Use `--output` only for a NEW private local file. Do not send raw messages to personal storage. This CLI makes no write operations. When the calendar scope is missing, report `BLOCKED` instead of inventing an empty calendar.

**Provider model:** Feishu's CLI user/bot credentials own API permissions. Hermes is optionally a scheduler / reasoning assistant; there is no separate Hermes OAuth scope to grant. For a team, choose one scheduler. If permitted, the assistant can interpret the generated brief and ask for confirmation before writing new tasks using official Lark CLI workflows. Never auto-create tasks inferred from ambiguous messages.

Test without credentials using `python3 agentready.py brief --date 2026-10-15 --fixture-dir examples/fixtures --message-query 待办 --details`. Live mode intentionally supports system-local **today only**, because the daily `calendar +agenda` query's arbitrary-date flag has not been verified.

Verify `lark-cli --profile YOUR_PROFILE auth status --json --verify` first. On missing scopes, report the sanitized scope; no automatic OAuth. Partial pages are fetched counts, not totals. Keep company details in authorized workspaces.
