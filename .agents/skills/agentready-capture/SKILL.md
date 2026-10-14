---
name: agentready-capture
description: Convert user-authorized text, notes or chats into structured next actions, calendar events, journal entries or inventory records without duplicating data sources. Trigger on remember this, record this, turn this into tasks, log an item, organize my day or capture from messages.
---

# AgentReady capture inbox

Read `docs/WORKFLOWS.md` and `docs/CONNECTORS.md`.

1. Take only user-supplied or authorized accessible material; avoid scraping personal or company chat outside permitted integrations.
2. Classify items as `task`, `calendar`, `journal`, `asset`, `reference` or `ignore`.
3. Extract a normalized draft with `title`, `due_at`, `timezone`, `source`, `source_id`, `description`, `destination` and `confidence`. Do not invent deadlines.
4. If task vs event is ambiguous, show the draft and ask before writing.
5. Choose the canonical native destination: e.g. Apple Reminders for personal task, Feishu Task for company task, HomeBox for owned item, personal notes app for journal.
6. Check for an existing record by provider ID or stable source+title+time combination; never blindly replay create operations.
7. After approval, call a verified provider API/CLI/MCP and report the external ID/link. On failure, keep the candidate as a draft; never claim success.

Sensitive messages and private files are not copied into an unrelated dashboard by default.
