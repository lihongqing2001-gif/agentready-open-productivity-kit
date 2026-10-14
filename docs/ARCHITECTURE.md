# Architecture & adapter contract

AgentReady is an **environment planner + portable skill collection**, not a centralized data lake. An agent user can select a preset, install missing desktop apps, connect account-scoped tools and run productive workflows in native apps. No front-end project or cloud account is required.

## Layers

1. User-selected `profiles/*.json`: an ordered list of adapter IDs.
2. `registry/adapters.json`: curated labels, local-presence probes, macOS Brew packages, manually required setup/permissions. Presence detection does not imply auth or functionality.
3. `agentready.py`: standard-library CLI; no network calls or telemetry for `doctor`, `plan`, `permissions`, `brewfile`, `inventory`.
4. `.agents/skills/*`: agent-agnostic workflow instructions. Execution depends on which tools the running agent actually possesses.
5. Native systems of record: the tasks source is a task provider, calendar source a calendar provider, household object HomeBox, company work Feishu, etc.
6. Optional aggregation: NocoBase can display source URLs and computed, approved summaries; don't migrate full records just for the dashboard.

## Adapter schema (v1)

Each named entry in `registry/adapters.json` defines:

- `label`, `category`, `purpose`: user-facing metadata.
- `probe.commands` and `probe.mac_apps`: local presence hints only.
- `macos_install.brew` / `cask`: **fixed** Homebrew identifiers in curated registry. No scripts, arbitrary shell snippets or user-supplied executable commands.
- `setup` and `permissions`: human-readable actions, not performed automatically.

Optional components that only run on a server (Hermes gateway, HomeBox, NocoBase) have *no macOS package installation*. Their actual endpoint and owner must be confirmed before a connector is registered. v1 does not store service URLs in its public config.

## Source-of-truth choices

| Domain | Typical master | AI allowed behavior |
| --- | --- | --- |
| Personal events | Apple / chosen calendar | list, recommend, create only after approval |
| Personal todos | Apple Reminders / Todoist | summarize, suggest, update on explicit request |
| Team tasks | Feishu Tasks / team system | authorized queries, traceable drafts |
| Household assets | HomeBox | deep link, summarize maintenance; don't duplicate item CRUD |
| Work capture | Dayflow local data | local summary, exclude sensitive windows before export |
| AI jobs | Existing Hermes/other scheduler | do not create a second competing scheduler |

## Cross-agent & cross-platform

The skill files conform to the Agent Skills `SKILL.md` frontmatter convention. Codex can use the checked-out repository skill folder; Claude Code / OpenCode / others require the appropriate agent-specific discovery location and execution permissions. The skill standard does not standardize all permission APIs, MCP configurations or token storage.

Installer v0.1 only supports **macOS + Homebrew**. Linux and Windows are profile-and-docs consumers, *not* full install targets yet. A future adapter-specific package executor can add apt, winget or Nix without expanding privilege in the base CLI.

## Contribution boundary

Do not merge adapters that automatically scrape private chats, bypass macOS TCC, modify cloud OAuth scopes without consent, copy agent authentication stores, or expose an unauthenticated dashboard on `0.0.0.0`.

## v0.2 capability layer

`registry/capabilities.json` maps goals to selectable native providers. `coverage` reports selected providers (not authenticated services). `wizard` creates a nonsecret local selection file and `report` compiles an offline onboarding checklist.

`agentready_connectors.py` holds reviewed, fixed-route opt-in network probes; generic adapter registry changes cannot execute arbitrary HTTP requests. Product owners can add tested adapters without implying they are already authenticated. No single green check means a complete workflow; see six verification levels above.
