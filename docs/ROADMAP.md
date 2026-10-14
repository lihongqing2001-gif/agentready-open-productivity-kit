# Productization roadmap

## v0.1 — included in this package

- Vendor-neutral Agent Skills: bootstrap, integration audit, daily brief, capture.
- Profiles: starter/team/life/power.
- macOS Homebrew planning + explicit install; no silent upgrades or cleanup.
- Local presence checks, permissions overview, sanitized inventory.
- Native-source architecture, integration/verification guidance.
- Automated standard-library tests.

## v0.2 — shipped in this package

- Interactive profile wizard writing only nonsecret enabled/disabled adapters.
- Capability ownership map and offline Markdown onboarding checklist.
- Fixed-route, explicit `--live` local/HTTPS provider probes for HomeBox and NocoBase, plus authenticated HomeBox identity and NocoBase MCP initialize probes. No record access or change.
- Synthetic localhost HTTP integration tests and CI dry-run probes.

## v0.3 — planned

- Validated connector contract for more vendors (Google Calendar/Workspace, Outlook, Todoist, Notion and Feishu), including authentication, authorization and sample business workflows.
- A grouped macOS permission **guide** (no TCC bypass) and native App/CLI install verification on physical macOS.
- Add Linux/Windows installer backends only when separately audited and tested.
- Source freshness reports, partial failure/resume state and clear idempotency semantics.
- Signing/notarization considerations if an app binary is distributed.

## v0.4 — planned

- Approved backup/restore and migration helpers (no raw authentication store copying).
- Synthetic provider workflow tests covering daily brief, deduplication and write confirmations.
- Agent integrations with real permission/auth failures and safe retries.

## v1.0

- User-tested onboarding from blank macOS to working native apps + source-verified daily briefing.
- Reproducible CI, published checksums, security review, versions and upgrade strategy.
- Optional no-code visual entry (NocoBase or a cloud SaaS), explicitly not required for base Skills.

## Ways others can contribute

1. Propose a portable adapter with clear native ownership and installation/permission instructions.
2. Keep all examples free of tokens, usernames, company assets, server domains and event data.
3. Add tests for safety and detection; mark what is checked vs merely documented.
4. Respect package and SaaS licenses; our MIT license covers only this project's original code and docs.
