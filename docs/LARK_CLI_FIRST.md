# CLI-first Feishu provider: no Hermes required

## Why this design

`lark-cli` itself owns Feishu bot/user identity and OAuth scopes. An agent process can call it without any Hermes channel binding. Hermes is **optional** as an execution planner, assistant, cron scheduler and notifier. This avoids creating duplicate Feishu applications, OAuth grants or task databases.

Official project: https://github.com/larksuite/cli (installation: `npx @larksuite/cli@latest install`). Existing managed company builds should be reused rather than overwritten. `lark-cli auth status --json` checks existing identity; `lark-cli auth login --domain calendar,task` is an example of optional user reauthorization, not a silent bootstrapping step.

## Capability ownership

| Capability | Native primary | AgentReady | Hermes |
| --- | --- | --- | --- |
| Company messages | Feishu IM, `lark-cli im` | opt-in scoped search; preserves links | optional summarizer |
| Company tasks | Feishu Tasks, `lark-cli task` | read-only brief | optional followup |
| Company calendar | Feishu Calendar, `lark-cli calendar` | read-only current agenda | optional scheduler |
| Meetings / documents | Feishu Minutes/Docs | existing CLI skills preferred | optional orchestration |
| Personal tasks | Apple Reminders | native app or Apple CLI connector | optional reminders |
| Household inventory | HomeBox | link or native API | not required |
| Personal dashboard | NocoBase optional | link or normalized projections | not required |

## One command, honest outcomes

```bash
python3 agentready.py brief                         # completely offline preview
python3 agentready.py brief --live --lark-profile YOUR_PROFILE                  # today's *work* tasks + calendar via user OAuth
python3 agentready.py brief --live --lark-profile YOUR_PROFILE --details        # include titles, avoid shared logs
python3 agentready.py brief --live --lark-profile YOUR_PROFILE --message-query 待办  # explicit bounded IM search
```

Expected behaviors: missing lark-cli, missing scope, malformed API response, timeout -> **BLOCKED**, not 0 tasks. Pagination flag -> **PARTIAL**, not complete. Business data is never sent to a SaaS or personal server by this code. `--live` runs on the calling device/container and requires that identity already be authorized there. Command output is memory-only unless `--output` is specified.

## Current coverage and limits

- v0.3 provides an actual (opt-in) lark-cli read-only command runner, a schema-normalizing daily report, and synthetic-fixture integration tests. It **does not** create/schedule a real notification or perform AI extraction from messages.
- Calendar `+agenda` is today-oriented; live `--date` other than system-local today fails explicitly.
- The current count is fetched items, not all eligible records if the API paginates or limits the response; source link and original record are authoritative.
- The process does not independently verify what an organization allows to be exported to a personal server. Keep corporate reports in authorized workspaces. Only share a sanitized test summary with open-source contributors.
- CLI `--as user` is explicitly passed for work tasks, calendar and user-visible IM; bot mode is a separate capability with a separate ACL.

## Runtime variants

1. **Codex only:** Codex skill -> `agentready.py brief` -> `lark-cli` -> source brief. For daily delivery, use a single approved OS scheduler configured separately.
2. **Hermes optional:** Hermes Skill/Cron -> the same CLI command in its own authorized environment -> DM using an already-connected work channel. Check that the Hermes host has the CLI and OAuth itself; Mac credentials do not magically exist in a server container.
3. **Other Agent Skills client:** call the same Python CLI via the agent's terminal integration, and preserve read-only mode by default.

## v0.4 contract

Use the selected profile for every command. Verify user identity with `lark-cli --profile YOUR_PROFILE auth status --json --verify` before live use. Calendar commands include explicit local-day bounds. Task reads are bounded to one page; has_more means PARTIAL. Missing scopes are sanitized and preserved, completed tasks and cancelled events are excluded. The report never schedules notifications.
