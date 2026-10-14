# Connector playbook: verify native capability before building

The public registry defines optional sources; account owners must choose the actual apps in use. All endpoint examples are placeholders.

## Work apps (Feishu example)

- Use official Feishu desktop app for messages, native tasks and calendar. Agent integration should prefer documented `lark-cli` / official API / MCP where available and scoped to the authorized user/organization.
- Distinguish bot identity, user OAuth and per-document / Base ACL. User OAuth is not a company data export license.
- Message searches must retain source link and date. A candidate action from a conversation should be confirmed before creating a task.
- Keep full conversations within the authorized work environment by default.

## macOS capture (Dayflow example)

- Verify actual release CLI/MCP from the running installation. A source tag containing CLI code isn't proof a DMG bundles that executable.
- Recording permissions must be granted consciously; review excluded apps/windows, audio settings and any AI model data transfer.
- A local stdio MCP is only local to the agent host. A remote agent needs a separate, approved route for summary data.

## Agents and memory

- Use an existing Hermes or other long-lived AI service when already available, not duplicate agent gateways or Cron jobs.
- Verify the precise remote service identity and authenticated API endpoint; don't infer personal/company ownership from a host label.
- MCP may expose *write and destructive* tools; use server-side RBAC and explicit refusal probes, not only readOnlyHint annotations.

## Apple Calendar & Reminders

- Check which calendar/reminder account and list is selected, verify EventKit/AppleEvents authorization separately, and use trusted CLI/MCP access only where approved.
- Avoid mirrored copies of the same Feishu / iCloud event. Prefer links to original events or a one-way read model with source IDs and update timestamps.

## Inventory and dashboard

- HomeBox is appropriate for item photos, labels, receipts and maintenance. A dashboard should link to HomeBox rather than reimplementing its rich entity editor.
- NocoBase is an **optional** cross-source view; use built-in cards/list/calendar and native mobile layout. Authentication, MCP and schema must be validated against the installed version.
- Keep source IDs, UTC timestamps, `source_updated_at`, `last_sync_at`, retry/error state on read projections. Use idempotent writes and only approved fields.

## Verification levels

1. Product documented.
2. Installed or detected.
3. Connection authenticated.
4. Resource access authorized.
5. MCP/API tested with synthetic or approved data.
6. Daily user journey completed on real devices.

Never collapse these levels into a single green check.

## v0.2 verified probe contract (real, opt-in)

`agentready.py verify` supports an audited fixed-route subset, not arbitrary HTTP templates:

| Service | Unauthenticated reachability | Optional follow-up | What it proves |
| --- | --- | --- | --- |
| HomeBox | `GET /api/v1/status` | `GET /api/v1/users/self` with token from environment | Endpoint works; optional current token accepted |
| NocoBase | `GET /api/app:getInfo` | `POST /api/mcp` initialize with `--mcp` | Endpoint works; optional MCP initialize responds |

**Not tested:** records, authorization for individual collections, write access, dashboard usability, real messages, calendar data, or scheduled jobs. MCP initialize may be available without authentication, so successful handshake does not imply authenticated data access.

Safeguards: dry-run default; remote host needs `--allow-remote` plus HTTPS; URL must be a bare origin; redirects rejected; max 64 KiB responses; 5-second timeout; no arbitrary commands or adapter-supplied URLs executed; body discarded; no secrets printed; optional token comes from a process environment variable. Even read-only probes can create provider access logs.

Implement new providers by code review plus synthetic server tests, not by allowing untrusted registry JSON to specify arbitrary routes or methods. Hostile MCP servers, compromised endpoints and OAuth scopes remain separate security decisions.
