# Contributing to AgentReady

This is a public, provider-agnostic project. Before opening a pull request:

- Make the contribution work without your own server, company tenant, personal data or account keys.
- Use native product interfaces first; if a duplicate integration is proposed, explain why the official CLI/MCP cannot do it.
- Keep macOS install identifiers curated and literal. Registry entries may not embed shell commands, curl pipelines or downloadable executables.
- Ensure dry-run output is useful before asking for `--apply`; no silent privilege or permission changes.
- Add tests and rerun `python3 -m unittest discover -s tests -v`.
- Mark actual tested behavior separately from public documentation and planned functionality.
- Ensure third-party applications retain their independent license and terms.

Proposed adapters should state: product, owner, supported platforms, native source of truth, installation mechanism, permission prompts, supported transport, safe first read probe and evidence.
