# Onboarding / permissions in batches

Users want **one planned authorization session**, not magic permission bypasses.

Run `python3 agentready.py permissions --profile <name>` to generate a batch checklist. Perform these batches in sequence:

1. **Account sign-in**: AI agent; chosen calendar, tasks, Feishu or equivalent. The account owner approves sign-in; the project never requests a password in plain text.
2. **macOS Privacy/TCC**: Calendar, Reminders, Screen Recording / microphone / Accessibility *only if the user's selected tool actually needs them*. Opening a settings page is not granting access. MDM-managed devices may need organization authorization.
3. **Provider OAuth**: approve specific scopes and sharing ACLs from the provider's own consent flow; the presence of an installed CLI does not imply the resource can be read.
4. **MCP/CLI**: choose individual vetted servers, local stdio vs remote HTTP transport, ownership and auth. A remote agent cannot directly launch a Mac-local stdio process on another host.
5. **Read-only proof first**: test access to a synthetic task/item and an authorized narrow calendar range. Add write operations separately with an explicit user approval and independent denial tests.
6. **Production availability**: consider offline behavior, secure backups, recovery, and connection expiry. Do not claim full readiness based on a `/health` response.

### Privacy and data boundaries

- Screenshots, audio, messages, event titles and even generated summaries can carry confidential information.
- Do not upload company content to personal clouds without company permission, even if the user possesses a token.
- Keep credentials in provider-supported login systems, Keychain or trusted managers. Never embed `.env`/API keys in portable packages, reports or agent chat.
- An agent is allowed to help the user navigate permissions, not click past security prompts or collect OTP codes without the user's appropriate participation.
