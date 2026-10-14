---
name: agentready-integration-audit
description: Audit connected CLI, MCP, agents, native applications and existing cloud services before implementing new integrations. Trigger when a user asks how to connect multiple apps, avoid rebuilding services, verify permissions, or map sources of truth.
---

# AgentReady integration audit

Read `docs/CONNECTORS.md`, `docs/ARCHITECTURE.md`, and `registry/adapters.json`.

- Map every desired capability to one authoritative application (tasks, calendar, inventory, notes, AI automation, daily analytics). Different owners may coexist; avoid copying full records to a separate dashboard.
- Use `python3 agentready.py plan --profile <profile>` for presence-only hints. For each integration, distinguish `configured`, `authenticated`, `resource authorized`, and `end-to-end verified`.
- Review local MCP tool names and transport (stdio or Streamable HTTP). Never assume a remote gateway can launch a local stdio server on another computer.
- Verify endpoint owner, token scope, exact resources, and expected write limits using provider-native tools. Do not print actual tokens or personal contents to diagnostic logs.
- Record data direction, conflict/duplicate rules, stale-data handling and failure path. Choose direct link over ETL when the native UI is better.
- Deliver a matrix: capability / native source / reusable CLI/MCP / status / gap / cost / priority / actual evidence.
- Reject the temptation to add another scheduler, agent or database just for aggregation.

Any production writes, OAuth authorization, public exposure, data export or installation require explicit consent and an appropriate authorization path.
