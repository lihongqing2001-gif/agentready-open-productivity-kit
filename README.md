# AgentReady — 人人可用的 AI 效率工作台初始化包

**Portable Agent Skills + native app first + configurable connectors + repeatable onboarding.**

AgentReady is a reusable productivity setup project, **not** an export of one person's Mac, company's Feishu workspace, servers or credentials. It helps a person who already has an AI agent to connect the tools they prefer and build a sustainable daily operating workflow without writing a new dashboard from scratch.

> Status: **v0.4 developer preview**. Offline setup, synthetic CLI end-to-end tests, explicit lark-cli profile selection, scope error reporting, and opt-in personal CLI counts are implemented. Live work task reads were verified on one authorized Mac; calendar scope and Apple TCC/iPhone acceptance remain separate gates. No capture, account migration, notification delivery or public CI success is implied.

## Quick start (macOS + Python 3)

```bash
python3 agentready.py catalog
python3 agentready.py doctor --profile starter
python3 agentready.py plan --profile power
python3 agentready.py permissions --profile power
python3 agentready.py coverage --profile power
python3 agentready.py report --profile power --output .reports/power-onboarding.md
python3 agentready.py install --profile starter        # preview only
python3 agentready.py install --profile starter --apply # changes your Mac, requires approval
```

Run `bash bootstrap.sh plan --profile team` if you prefer the shell entrypoint. Installing Homebrew, Apple privacy grants, Feishu OAuth, third-party sign-in and server provisioning are outside silent automation.

### Which profile?

| Profile | Who it's for | Primary tools |
| --- | --- | --- |
| `starter` | Anyone starting with an AI agent | Codex + Apple Calendar/Reminders/Shortcuts |
| `team` | People working with Feishu | Codex + Feishu + Apple native apps |
| `life` | Personal planning and assets | Apple + HomeBox + optional NocoBase + Obsidian |
| `power` | Full work-life AI workflow | Feishu, Dayflow, Hermes, HomeBox, NocoBase, notes, etc. |

Vendor choices are **swappable**. Codex is the initial bootstrap agent, not a monopoly: Agent Skills is a vendor-neutral format. Other compatible agents can read the same SKILL.md instructions, but actual discovery, terminal access and API connectors vary per agent.

Optional local overrides without secrets:

```bash
cp examples/user-config.example.json my-config.json
python3 agentready.py plan --profile life --config my-config.json
python3 agentready.py brewfile --profile life --config my-config.json
```

Keep `my-config.json` private; the default `.gitignore` excludes it. Do not put passwords, session cookies or raw API keys in JSON.

## New in v0.3: lark-cli-first daily brief (Hermes optional)

Feishu/Lark is now a **native CLI provider**, not a Hermes-dependent integration. With your existing lark-cli OAuth, run:

```bash
python3 agentready.py brief                                        # offline preview, no Feishu read
python3 agentready.py brief --date 2026-10-15 --fixture-dir examples/fixtures --details  # synthetic test
python3 agentready.py brief --live --lark-profile YOUR_PROFILE --details                         # today's work tasks + agenda
python3 agentready.py brief --live --message-query 待办              # optional scoped message search
```

`--live` does not log in, install packages, send messages or write Feishu records. It calls the existing lark-cli executable as the current user. Missing OAuth and unknown response schemas are **BLOCKED** rather than reported as zero records. It intentionally does **not** infer tasks from messages. Company information must stay within authorized boundaries.

See [CLI-first Feishu design](docs/LARK_CLI_FIRST.md) and [overnight agent handoff](docs/OVERNIGHT_HANDOFF.md). Extra Skill: `agentready-lark-brief`. GitHub publication: see [guarded publish guide](docs/PUBLISH_GITHUB.md).

## Previous v0.2: guided setup and connection checks

Run an **interactive nonsecret** onboarding wizard to select existing tools (no installation or login):

```bash
python3 agentready.py wizard --profile life --output my-config.json
python3 agentready.py coverage --profile life --config my-config.json
python3 agentready.py plan --profile life --config my-config.json
```

The wizard writes only `enable`/`disable` adapter IDs. No service URL, secret, account or session data is captured. It refuses to overwrite a file.

For user-owned, opt-in read-only endpoint probes:

```bash
# No network access unless --live is supplied
python3 agentready.py verify --service homebox --url http://127.0.0.1:17745

# Explicitly check a localhost HomeBox instance. Only /api/v1/status is queried.
python3 agentready.py verify --service homebox --url http://127.0.0.1:17745 --live

# When already authorized, verify login with only GET /api/v1/users/self;
# store the token in your own environment/secret manager, not in config JSON.
python3 agentready.py verify --service homebox --url http://127.0.0.1:17745 --live --token-env HOMEBOX_TOKEN

# NocoBase /api/app:getInfo and optionally a protocol initialize (not business operations)
python3 agentready.py verify --service nocobase --url http://127.0.0.1:18022 --live --mcp

# Remote services: HTTPS AND explicit --allow-remote required
python3 agentready.py verify --service nocobase --url https://your-instance.example \
  --live --allow-remote --mcp --token-env NOCOBASE_TOKEN
```

A successful status URL is **only service reachability**; a successful MCP `initialize` is **only protocol compatibility**, not proof of collection permissions, user identity, or complete workflows. HomeBox account auth is separately tested only when a token environment variable is provided. The program discards response bodies and prints no token or user content. It does not automatically contact remote servers, install servers, change permissions, invoke tools, or import data.

Endpoint probes support HomeBox and NocoBase; a separate `brief --live` command now invokes existing lark-cli only with explicit opt-in. For Feishu, Apple Calendar, Hermes and Dayflow, follow their native sign-in/CLI/MCP instructions; they are **not** silently authenticated by this CLI. See [v0.2 connector contract](docs/CONNECTORS.md).

## Reusable skills

- **agentready-bootstrap** — machine setup, profiles, permissions, migrations.
- **agentready-integration-audit** — inspect native apps, CLI/MCP and reuse before adding services.
- **agentready-daily-brief** — morning, evening and weekly digests, grounded in connected sources.
- **agentready-weekly-review** — evidence-based Monday weekly report with deduplication and partial-source handling.
- **agentready-lark-brief** — Feishu user-OAuth tasks/calendar briefing using lark-cli, no Hermes required.
- **agentready-capture** — convert user-authorized messages into draft tasks, events, records and assets.
- **agentready-workflow** — one-time setup and recurring Dayflow + Codex + Feishu daily/weekly reporting, with a single configured delivery route.

Skills live under `.agents/skills/`. Download or clone this repository, open it in Codex or another compatible agent, then request: “Use `agentready-workflow` to set up and verify my Dayflow + Codex + Feishu daily and weekly reports.” If the agent does not discover repository Skills, follow its official instructions to copy the needed Skill folders without overwriting existing Skills. Keep this checkout available because its Skills reference the repository CLI and docs. Skills do **not** automatically grant tool permissions.

## Design principles

1. **Native-first**: Apple/Feishu/HomeBox/Obsidian retain their native interface and master data.
2. **Agent-first**: use an existing Codex/Hermes/other compatible agent for intelligence. Do not spawn duplicate agents or schedulers.
3. **Portable**: profiles select adapters; no personal hostname, account ID, workspace or token in code.
4. **Explicit changes**: dry-run by default; Homebrew install requires `--apply`; no `brew cleanup`.
5. **Verifiable**: `CLI present` ≠ `OAuth logged in` ≠ `MCP list succeeded` ≠ `business use case passed`.
6. **Flexible entry**: the phone can be a home-screen web shortcut, Feishu, or native apps. A cross-source dashboard is optional.

## Architecture

```text
Human + existing AI agent (Codex / compatible Agent Skills consumer)
               |
         portable Skills
               |
       profile + adapter registry
          /       |       \\
       Apps     CLI/MCP    OAuth checklist
          \       |       /
          Native data sources
 (Calendar/Reminders/Feishu/HomeBox/Notes ...)
               |
 Optional read-only summary / dashboard (NocoBase or native)
```

## Documentation

- [中文五步上手](docs/GET_STARTED_ZH.md)
- [复制给 Codex 的启动指令](docs/CODEX_START.md)
- [真人试点验收清单](docs/PILOT_ACCEPTANCE.md)
- [Architecture and adapter contracts](docs/ARCHITECTURE.md)
- [Permissions and onboarding](docs/AUTHORIZATION.md)
- [Connectors and provider boundaries](docs/CONNECTORS.md)
- [Ready-to-run daily workflows](docs/WORKFLOWS.md)
- [Public release plan and contribution guide](docs/ROADMAP.md)
- [Security](SECURITY.md)

## Developer checks

```bash
python3 -m unittest discover -s tests -v
python3 agentready.py plan --profile starter --json
python3 agentready.py brewfile --profile power
python3 agentready.py coverage --profile life --json
python3 agentready.py verify --service nocobase --url http://127.0.0.1:18022 # dry-run
```

The project is a reusable **framework and workflow pack**, not a production SSO platform, MDM solution or installed mobile application. No telemetry or network calls occur in the stdlib planning commands.

### Optional autonomous pilot launch (Codex CLI)

Run `bash scripts/launch_codex_pilot.sh /absolute/path/to/task.md` to preview and `... --apply` to launch a restricted background `codex exec` on your own always-awake machine. The runner prints a PID and private log/status paths, is **not** an OS-level daemon, and cannot wake a sleeping Mac. It does not circumvent approvals or run GitHub publication by itself. See `docs/OVERNIGHT_HANDOFF.md`.

## v0.4: one-time setup and daily use

Use your existing agent to read `.agents/skills/agentready-bootstrap/SKILL.md`.
Choose a profile, run `doctor`, `coverage`, `plan`, and generate a private
`report`. Built-in Apple apps need no installer. Approve native permissions once;
recheck real reads afterwards. Never copy OAuth sessions or provider keys.

```bash
python3 agentready.py personal-brief              # preview, no reads
python3 agentready.py personal-brief --live       # ekctl + remindctl + dayflow
python3 agentready.py brief --lark-profile YOUR_PROFILE # work preview
python3 agentready.py brief --live --lark-profile YOUR_PROFILE
python3 -m unittest discover -s tests -v          # includes synthetic CLI E2E
```

`personal-brief` reports counts only, using existing native tools. It never
starts screen capture, writes reminders, installs a calendar app, or contacts
Feishu. Permission failures stay BLOCKED and other sources continue.
`ekctl` uses EventKit's full-access OS permission; this workflow only executes
read commands. iCloud/iPhone synchronization must be checked on both devices.
Dayflow must independently complete its consent, app exclusions and local AI
setup. A zero activity count is not proof that capture works.

Work and personal reports are separate. Missing tools or scopes do not require
reinstallation of the whole kit. After authorization, rerun the same read command.
Reports with `--output` are owner-only and never overwrite existing evidence.
Only explicitly query messages; records are evidence, not inferred commitments.

### Rollback and execution

Keep a baseline Git branch; revert project commits without modifying app data.
Tests use temporary synthetic environments and do not require account login.
The optional Codex launcher preserves provider/model/credentials and writes a
private PID/log/exit-status receipt. It is a one-shot shell process, not a
persistent OS scheduler; close/logout/sleep survival is not guaranteed.
See `docs/PUBLISH_GITHUB.md` for publication gates. Never publish `.reports/`.

## Connected daily and Monday weekly reports

Use `agentready-workflow` with your existing agent. It guides initial setup and
authorization, verifies live Dayflow and scoped lark-cli reads, then combines
Feishu daily reports/weekend updates, Dayflow work observations and scoped
Codex conclusions into private Markdown. Configure one final publisher: either
an authorized self-DM route or an existing reporting agent's approved intake.
See [one-time setup, evidence and scheduling](docs/REPORTING_WORKFLOW.md).
No screenshot upload, new agent or additional scheduler is required.

```bash
python3 agentready.py weekly-review # offline plan, no reads
python3 agentready.py weekly-review --date 2026-10-21 --fixture-dir examples/review-fixtures
```

The CLI collects evidence. Your agent writes the narrative; synthetic tests do
not prove live authentication, delivery, or a future scheduled run.
