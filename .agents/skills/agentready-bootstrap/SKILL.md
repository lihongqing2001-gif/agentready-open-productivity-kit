---
name: agentready-bootstrap
description: Help a person initialize a new computer as an AI-assisted productivity workstation using an existing agent, native apps, package manifests, permissions checklist, and repeatable verification. Trigger on new computer setup, onboarding, reinstall, migration or automation bootstrapping.
---

# AgentReady bootstrap

Read the project `README.md`, `AGENTS.md`, and `docs/AUTHORIZATION.md` first.

1. Ask only for the intended platform and goal if not available. Let users choose `starter`, `team`, `life`, or `power`. macOS has the only automated installer in v0.2; all other platforms are planning-only.
2. Run `python3 agentready.py doctor --profile <name>`, then `coverage` and `plan`. Offer `wizard --profile <name> --output my-config.json` if they want a reusable personal selection. Read `registry/adapters.json` and check for other existing tools before adding anything.
3. Generate a macOS installation preview with `python3 agentready.py brewfile --profile <name>`; explain the installed/not-installed distinction, native apps, remote-only apps and possible conflicts.
4. Run `python3 agentready.py install --profile <name> --apply` **only after the user explicitly approves the entire install batch**. `install` without `--apply` is a dry run.
5. Run `permissions` and walk the user through required permissions and OAuth screens. Never bypass the OS prompt, collect credentials or make raw keychain exports.
6. Connect to *existing* services before proposing deployment. Do not import all MCP servers from another machine; connect scoped, vetted servers one by one using the agent's documented method.
7. Optionally probe a supported existing HomeBox/NocoBase endpoint using `verify`, initially without `--live`, then with explicit user approval. Status and MCP initialize are NOT business access tests. Verify each actual read/write path with non-sensitive data, label results `verified`, `not tested`, `blocked`, or `failed`. CLI installed != authenticated; MCP handshake != business workflow passed.
8. Generate `report --profile <name> --output .reports/onboarding.md` for a repeatable checklist. Provide evidence, service owner and next action. Stop when a boundary or provider identity is unresolved.

Never move company messages or code into a personal instance without permitted scope. No duplicate cron or AI gateway. Do not call `brew bundle cleanup`, change machine security policy, or promise a one-click authorization bypass.
