# Security policy

AgentReady is intentionally **dry-run first** and does not perform a blanket export of passwords, SSH identities, chat logs, company documents, or device permissions.

- Any real installation requires `install --apply` and explicit user approval.
- The CLI's read-only planning commands do not make network requests or send telemetry.
- Do not publish real connection endpoints, API keys, OAuth tokens, personal `.env`, Keychain exports or signed cookies in issues and screenshots.
- For company-owned data, follow organization policies and limit any export to approved scope.
- MCP servers are not automatically trusted: their tool schemas may include write/destructive actions. Audit server authorization and read/write denial behavior.
- Do not run unauthenticated agent Dashboards on public addresses.
- Report vulnerabilities privately to the project maintainers before public disclosure (maintainer contact to be configured before GitHub publication).

This project does not audit third-party packages or make their licenses our own. Users should verify download origin, version and provider terms.

## v0.2 network probes

`verify` performs **no request** without explicit `--live`. Only fixed HomeBox/NocoBase status/identity/MCP-initialize routes are allowed. Loopback HTTP is permitted; non-loopback destinations require HTTPS and `--allow-remote`. Redirects are refused. It does not print or persist endpoint response bodies, access tokens, or user data. Tokens are supplied through named process environment variables, not command-line token literals. Provider-side logs may still record access. For trusted internal domains, inspect TLS and the endpoint owner before use.

A NocoBase MCP handshake does not prove authenticated resource access. Authenticate with least-privilege credentials and separately test protected read vs denied write actions before any production automation.
