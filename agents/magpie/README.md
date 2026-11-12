# Windows：GLM / Kimi Coding Plan 工作配置

配置于 2026-11-12，Magpie 0.1.3859。此处保存不含凭证的配置方案；各机的套餐密钥与登录保留在本机。

## 分工

| 路由 ID | 用途 | 首选 | 备用 |
| --- | --- | --- | --- |
| `group/plan-writing` | 长文阅读、资料整合、课程笔记、报告与文字编辑 | `kimi-code-cn/k3.1-pro:high` | `zhipu/glm-5.3:high` |
| `group/plan-research` | 联网检索后的分析、日常任务、代码工作 | `zhipu/glm-5.3:high` | `kimi-code-cn/k3.1-pro:high` |
| `group/plan-fast` | 标题、摘录、短改写、上下文压缩 | `zhipu/glm-5.3-flash:low` | `kimi-code-cn/k3.1-pro:low` |

各组使用 `routing=order`、`stays=session`，上下文对客户端保守声明为 `256k`。只有首选不能服务时才使用备用；两个套餐用尽时不自动转入额外付费 API。Kimi 保持思考模式，不使用消耗倍数更高的 Highspeed 版本。

## 客户端

- Codex：继续使用原有 GPT Pro，模型及推理配置不改。
- Claude Code：默认使用写作组；Opus 对应写作组，Sonnet 对应研究组，Haiku 对应快速组，子代理使用研究组。
- DeepSeek Harness：研究组，保留原有压缩设置。
- OpenCode：Build 使用研究组，Plan 使用写作组，小模型使用快速组；保留既有搜索、网页读取 MCP。
- VS Code Chat：写作组。
- Pi 与 Kimi Code：原本已用 Kimi 套餐，保留现有接入。
- WorkBuddy：保留 Magpie 接入，当前 GLM 渠道继续可用；新增组在 Magpie 刷新模型目录后可从模型菜单选择。

切换模型后开启新会话。不要把旧模型的长推理上下文直接当作新模型的最佳起点。

## 复现路由

先在目标机器确认上述 provider ID 已存在且对应自己的 Coding Plan。以下命令不包含密钥，也不替换现有 provider。

```powershell
magpie group add plan-writing models=kimi-code-cn/k3.1-pro:high,zhipu/glm-5.3:high routing=order stays=session
magpie group set plan-writing 'name=长文与写作 · Kimi优先' context=256k family=paid-plans
magpie group add plan-research models=zhipu/glm-5.3:high,kimi-code-cn/k3.1-pro:high routing=order stays=session
magpie group set plan-research 'name=研究与日常 · GLM优先' context=256k family=paid-plans
magpie group add plan-fast models=zhipu/glm-5.3-flash:low,kimi-code-cn/k3.1-pro:low routing=order stays=session
magpie group set plan-fast 'name=快速整理 · GLM Flash' context=256k family=paid-plans
```

这些组由各机 Magpie 保存；当前 Dotfiles 的 `apply.sh` 不会自动导入它们。同步 Claude 的 Windows 配置前，先在目标机器创建同名路由。Mac 的 Claude 基线配置本次不变。

## 搜索与编辑质量

Claude 的规则见 `../claude/rules/research-writing.md`。既有智谱 `web-search-prime`、`web-reader`、`zread` 保留；Kimi 通过 Magpie 的原生 WebSearch 转接已能返回网页来源。联网能力与模型本身分开验证，仍应读取原文并核对引用。

GLM Lite 的 MCP 有独立月额度，本机读数为 100 次/月；不要把可用模型调用额度误当作无限搜索次数。以服务商实时显示为准。

## 本机恢复点

修改前备份：`C:\Users\Lzw\Documents\Magpie配置备份\20261112-175618`。其中包含本机敏感配置，不加入 Git 或直接分享。恢复时只恢复需要回退的文件，避免覆盖之后的新设置。

## 依据

- [Magpie 路由与客户端设置](https://usemagpie.ai/docs/start)
- [Kimi 模型、思考模式与套餐条件](https://www.kimi.com/code/docs/en/kimi-code/models)
- [GLM Coding Plan 接口](https://usemagpie.ai/docs/glm)
- [智谱联网搜索 MCP](https://docs.bigmodel.cn/cn/coding-plan/mcp/search-mcp-server)
