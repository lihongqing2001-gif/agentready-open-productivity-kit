# Publish AgentReady openly — guarded instructions

1. Run local tests, `git status --short`, source scans, license check and ensure prompts with organization-specific details are not in the public tree.
2. Use an authenticated GitHub CLI on **your own host**, not a copied token: `gh auth status`.
3. Inspect whether the repository exists before creating a new one: `gh repo view <owner>/agentready-open-productivity-kit`.
4. If it does not exist and the user authorized publication, create `gh repo create agentready-open-productivity-kit --public --source . --remote origin` in a new git repository.
5. Push the audited default branch; verify GitHub Actions, README, no secrets and real public URL. Report exact failure if CLI lacks permission.

The bundled artifact was **not** pushed to GitHub by the package builder. It contains no GitHub API key and is intentionally not self-publishing. Use a dry-run/secrets scan before public upload.
