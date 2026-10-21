---
name: agentready-daily-brief
description: Create a grounded daily work-and-life briefing or weekly review from only the calendars, tasks, journals, inventory reminders and notifications that the user has already connected and authorized. Trigger on daily plan, what did I do today, morning digest, end-of-day recap or weekly review.
---

# AgentReady daily briefing

Read `docs/WORKFLOWS.md` first. Work with whatever apps the user already prefers; do not require NocoBase, Hermes or Feishu.

1. Identify the user's local date and time zone. Preserve the time window and source scope precisely.
2. Use native read-only tools, CLI or provider MCP to retrieve relevant tasks and events. If no source is available, ask for a source instead of inventing entries.
3. Deduplicate repeated calendar subscriptions and tasks by stable provider/source IDs. Distinguish confirmed tasks, meeting suggestions, and inferred follow-ups.
4. Produce a compact report: upcoming events / top 3 tasks / overdue items / high-priority reminders / time spent when real measurement is available / source freshness / blockers.
5. Make source attribution clear (provider and navigable link when authorized). Mark missing services as unavailable; don't report all-clear when a source failed to load.
6. Writing back tasks, sending messages or scheduling events requires user approval and provider confirmation. Never create recurring automations without request.

Separate company and private information in output; use the official native UI to modify the canonical record.

For personal counts, preview `python3 agentready.py personal-brief`, then use `--live` only with authorized native reads. It reuses ekctl, remindctl and dayflow; never starts capture. Keep personal and company output separate. TCC and iPhone verification remain human gates.

## Connected work recap

When the user requests Dayflow + Codex + Feishu reporting, read
`docs/REPORTING_WORKFLOW.md`. Reuse the existing daily sender; enrich its report
with `weekly-review --period daily` evidence plus scoped Codex conclusions.
Group actual outcomes, ongoing work, blockers and tomorrow's actions; cite
source IDs and distinguish Dayflow observations from completed work. Never
include personal projects in company delivery by default. Save a private local
Markdown, deliver through the authorized private route if requested, and verify
message ID/readback. A standing recurring-delivery authorization does not need
fresh confirmation every day. Do not infer a missing source as zero work.
