# AgentReady v0.4：普通用户快速开始

AgentReady 是一组可下载的 Agent Skills 和本地工具，用来复用你已有的 Dayflow、Codex 或其他 Agent、飞书 CLI 和 Apple 原生应用。它不是另一套聊天服务或日历系统；Hermes 是可选的。

## 下载并启动

从 GitHub 下载 ZIP 解压，或克隆仓库：

```bash
git clone https://github.com/lihongqing2001-gif/agentready-open-productivity-kit.git
```

在 Codex 或支持 Agent Skills 的客户端中打开仓库，并输入：

> 使用 `agentready-workflow`，带我一次性配置 Dayflow、当前 Agent 和飞书的日报/周报。先检查并复用已有软件与连接；把需要我点的系统权限集中列出。完成授权后做真实只读验证，配置一个日报/周报发送方，不创建重复调度。我的公司数据只能留在我选定的公司通道。

如果 Agent 没有自动发现 `.agents/skills/`，按该 Agent 的官方说明，将需要的 Skill 文件夹安装到它支持的目录；不要覆盖同名 Skill。保留仓库，因为 Skills 会引用仓库里的 `agentready.py` 和文档。Skills 不会自动获得终端、屏幕录制、MCP 或账号权限。

## 检查与选择

环境检测默认离线，不安装、不登录：

```bash
python3 agentready.py doctor --profile starter
python3 agentready.py coverage --profile starter
python3 agentready.py report --profile starter --output .reports/onboarding.md
python3 agentready.py wizard --profile life --output my-config.json
python3 agentready.py plan --profile life --config my-config.json
```

预设有 `starter`、`team`、`life`、`power`。安装预览不会更改设备；只有明确批准安装批次后，才执行 macOS 安装：

```bash
python3 agentready.py install --profile life --config my-config.json
python3 agentready.py install --profile life --config my-config.json --apply
```

## 一次授权、真实验收

按 `agentready-workflow` 和 `docs/REPORTING_WORKFLOW.md` 完成 Dayflow 官方版本检查、录屏与 AI 分析选择、已有 agent 的 CLI/MCP 接入、飞书 OAuth、私有配置及唯一调度。需要系统设置或浏览器登录的权限由本人完成；助手应集中列出这些步骤，不得绕过 TCC 或复制凭据。

分别验收 Dayflow 的真实采集→分析→Timeline→CLI/MCP 读取，以及飞书日历/任务所需的真实只读调用。只看到软件已安装、登录成功或 MCP 握手，不代表业务流程通过。选择一个日报最终发送方；如使用已有日报 bot 合并，先确认其授权入口，再核对接收回执、合并报告、消息 ID 和原私聊读回。公司数据留在用户指定的公司通道，原始截图不进入报告。

## 日常使用与验收状态

日报使用上一个本地自然日；周一周报覆盖上周一至周日并核查真实周末消息。报告为本地私有 Markdown，结合明确授权的飞书日报/任务、本机 Dayflow 工作观察和有来源 ID 的 Codex 结论。观察、计划和提交记录都不能单独证明业务完成；缺失数据必须标为 PARTIAL/BLOCKED。

调度必须复用现有任务并确认仅有一个最终发送方。启用调度不等于验收：首次定时运行后还要核对来源回执、消息 ID、目标会话和读回。电脑休眠或离线时可能错过运行，应按周期幂等补跑一次。

Skills 不携带任何用户的账号、公司聊天、私有路径、Dayflow 截图或云端权限。工作与个人数据默认分开；Reminders、日历的跨设备同步需分别在设备上验证。
