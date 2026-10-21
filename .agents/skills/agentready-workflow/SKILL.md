---
name: agentready-workflow
description: Use when someone wants to install or configure reusable Dayflow + Codex + Feishu daily briefs and Monday weekly reviews with existing apps, authorized accounts and one reporting destination.
---

# AgentReady work reporting

Use this as the single entry point for installing the skills and configuring the
Dayflow/Codex/Feishu reporting workflow. Read `docs/REPORTING_WORKFLOW.md` in
this repository; it is the setup, evidence, scheduling and recovery runbook.

1. **Initialize once.** Run `agentready-bootstrap` and `agentready-integration-audit`.
   Reuse installed Dayflow, the user's existing agent and official `lark-cli`.
   Check official Dayflow release/signature before installation. Guide the user
   through required macOS Screen Recording, provider and OAuth prompts together;
   never bypass TCC or copy credentials. Hermes is optional.
2. **Verify real capabilities.** Prove Dayflow capture → analysis → Timeline and
   a real CLI/MCP read. Verify the selected lark-cli profile and perform only
   authorized scoped reads. Distinguish installed, authenticated, reachable and
   workflow-verified. Keep company and personal sources/destinations separate.
3. **Choose one report owner and destination.** Inspect existing schedules and
   receipts first. Configure the user's own profile, chat IDs, allowed work
   categories, project paths, timezone, private output directory, and delivery
   route in an ignored local config. Reads use user identity; delivery may use
   an explicitly authorized bot or user route. If an existing reporting agent
   must consolidate reports, send it a dated, deduplicated evidence supplement
   through its approved intake and verify the consolidated message/readback.
   Never create a parallel sender or replace the destination with a self-DM.
4. **Daily report.** Collect the previous local day from configured Feishu
   reports/tasks, authorized Dayflow work observations and scoped Codex
   conclusions. Produce a private Markdown with outcomes, ongoing work, blockers
   and next actions. Cite dates and source IDs; deduplicate overlapping evidence.
   Observation or a commit alone is not proof of completion. State missing data
   and uncertainty; never infer zero activity from a failed read.
5. **Monday weekly report.** Review the previous local Monday–Sunday, including
   actual weekend messages. Combine daily reports with the week's Dayflow and
   Codex evidence, distinguish the user's work from team updates, and keep
   outcomes ahead of tool/test details. Preserve a partial status where sources
   or coverage are incomplete.
6. **Schedule and accept.** Use the existing reporting schedule in the user's
   timezone. In a split local/cloud workflow, schedule the local evidence
   supplier before the existing publisher; this is one final report route, not
   a second daily sender. If no schedule exists, configure one native scheduler.
   Save idempotency receipts and check them before delivery. A schedule being
   enabled is not acceptance: verify a real scheduled run, the destination
   message ID, and readback. On sleeping/offline hosts, report missed runs and
   catch up once per period. Do not fabricate a report or blindly retry an
   ambiguous send.

Use `agentready-daily-brief` for a one-off daily plan and
`agentready-weekly-review` for a one-off or scheduled weekly narrative. Keep
local Markdown and evidence private. Do not upload raw screenshots, tokens,
private Codex history or company content to this public repository.
