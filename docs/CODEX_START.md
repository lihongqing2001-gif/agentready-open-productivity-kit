# 发给 Codex 的入口指令

请把当前仓库作为 AgentReady v0.2 项目打开，先阅读 `AGENTS.md`、`README.md`、`.agents/skills/agentready-bootstrap/SKILL.md` 和 `docs/GET_STARTED_ZH.md`。

你的任务：根据用户设备与目标，先运行只读 `doctor`、`coverage`、`plan`，为用户列出复用的软件、缺失能力和安装/授权路径。用户确认后再允许 `install --apply`；不要复制另一台机器的认证文件或全量 MCP 配置。

需要个人组合时，交互运行 `wizard` 保存不含凭据的本机 JSON；如已有 HomeBox/NocoBase，先默认 dry run 的 `verify`，获得用户批准后才加 `--live`。不要将 HomeBox 状态 GET、NocoBase MCP 握手视为已完成业务集成。

最后运行 `report` 生成清单，并说明每项实际证据级别。优先原生 App 与既有 Agent，只有现成方案无法满足用户目标时才建议安装其他产品或开发代码。
