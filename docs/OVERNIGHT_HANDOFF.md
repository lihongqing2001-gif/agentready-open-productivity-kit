# Autonomous agent handoff template

This open-source repository includes `docs/prompts/GENERIC_AUTONOMOUS_PILOT.md`, a vendor-neutral agent pilot contract. Maintainers may create **private execution orders** for specific personal or enterprise environments; those orders must remain OUTSIDE the public package.

A Skill alone is not a persistent job runner. If a user wants overnight progress, the job must be submitted to an actually running agent CLI, workflow/scheduler or external agent service; verify the job ID, lifecycle status and report destination. Never assert the task has started solely because a prompt was generated.

Common acceptance: repeatable tests, accurate live/fixture distinctions, documented permission blockers, no raw credentials or personal data in public commits, idempotent workflows, and one authoritative scheduler per task.

Optional one-time terminal runner: `bash scripts/launch_codex_pilot.sh /absolute/path/to/private-task.md` previews, then add `--apply` to start with Codex's workspace-write sandbox. It stores a log and final exit status under `.reports/agentready-night/`; this is **not** a durable OS scheduling service. Do not close/sleep the host and assume the job persists. Read the actual logfile and status before claiming success.
