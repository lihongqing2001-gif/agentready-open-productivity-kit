# AgentReady project instructions

This is a reusable, public template. Do not assume the user's hardware, company, assistant, calendar provider or cloud architecture.

- Prefer installed applications, documented native integrations, then MCP/CLI/API. Build custom UI or scripts only when the native experience cannot meet the need.
- Start with `python3 agentready.py doctor --profile starter` and `coverage`; optionally run `wizard` for nonsecret config and ask the user to choose a profile. Never run installation by default.
- `install --apply` is a real change and requires approval; no secret migration, aggressive cleanup, permission bypass or service deployment without explicit authorization.
- Profiles are recipes, not entitlements. A named vendor does not imply an account exists.
- Use provider-native app for full CRUD where possible; cross-source dashboard is an optional read model, not a system of record.
- Company vs personal data never cross by default. Ask for sanctioned routes if requested.
- Reports must distinguish installed, logged in, API reachable and fully validated.
- Automated installers only support macOS in this release; other OS receive a plan.

Portable skills are at `.agents/skills/` and use the Agent Skills open standard. Consult agent-specific skill installation documentation if the agent doesn't search that location.

- Connector `verify` is offline by default. Request explicit authorization before using `--live`, `--allow-remote`, or tokens from secret managers. Do not treat HTTP 200 or MCP handshake as proof of a business integration.
