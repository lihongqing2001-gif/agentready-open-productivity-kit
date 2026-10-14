# AgentReady v0.4 — 给普通用户的五步使用指南

AgentReady 是一套 **给现有 AI Agent 使用的技能和工具箱**，不是另一款 AI 聊天应用，也不是必须部署的服务器。用户无需拥有 Hermes、飞书或 NocoBase；这些只是可选软件。

## 0. 需要准备什么

- macOS 用户：Python 3（用于生成计划）、现有 Codex 或其他能调用本地项目指令的 Agent。安装软件时可以选用 Homebrew。
- Windows/Linux 用户：目前仅提供规划与检查，不执行自动软件安装。
- 对隐私敏感的用户可以不启用录屏、云服务或任何网络探测。

## 1. 打开仓库

下载或克隆项目后，在 Agent（如 Codex）中打开项目目录，让 Agent 阅读 `README.md` 与 `.agents/skills/agentready-bootstrap/SKILL.md`，并说：

> 帮我用 AgentReady 初始化个人效率环境。先只检测和出方案。我的目标是管理日程、待办和个人物品，优先复用已安装软件，不新增重复 AI 服务。请解释每项将进行的真实修改。

## 2. 按预设生成环境报告（离线）

```bash
python3 agentready.py doctor --profile starter
python3 agentready.py coverage --profile starter
python3 agentready.py report --profile starter --output .reports/onboarding.md
```

预设：`starter`（基础）、`team`（飞书工作）、`life`（生活/物品）、`power`（工作生活全套）。不强制任何预设安装所有软件。

## 3. 用交互向导选择自己需要的东西

```bash
python3 agentready.py wizard --profile life --output my-config.json
python3 agentready.py plan --profile life --config my-config.json
```

向导只保存选中的软件名称，不保存账号、密码、密钥、日历或聊天数据。

## 4. 只在确认后安装、登录与授权

```bash
python3 agentready.py install --profile life --config my-config.json  # 默认只预览
python3 agentready.py permissions --profile life --config my-config.json
# 真正安装仅支持 macOS，并需要明确批准
python3 agentready.py install --profile life --config my-config.json --apply
```

macOS 的屏幕录制、日历、提醒事项等系统权限以及飞书 OAuth 等仍由用户本人授权，工具不能静默代替用户点击。

## 5. 选择性检查已部署服务连接（可选）

```bash
# 无 --live 时不会联网
python3 agentready.py verify --service homebox --url http://127.0.0.1:17745
# 用户同意后才真正测试本地服务可达性
python3 agentready.py verify --service homebox --url http://127.0.0.1:17745 --live
```

当前提供 **HomeBox/NocoBase 两种固定路由的诊断探针**，不是自动连接所有账号。HTTP 可达不等于用户已登录；MCP 握手成功不等于能读取授权数据。真实日历和工作流要另行验收。

## 最终你能得到什么？

当前版本可以获得：设备现状清单、选用的软件组合、安装计划、授权清单、能力覆盖图和可选服务诊断。v0.4 支持只读飞书简报与个人原生工具统计；真实授权、录屏分析、iPhone 同步仍需分别验收。 日报和收集箱 Skills 已有操作说明，但需要真实且已授权的提供方连接后才能执行。
