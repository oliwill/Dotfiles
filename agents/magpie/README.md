# Windows：GLM / Kimi Coding Plan 工作配置

配置于 2026-11-12，Magpie 0.1.3859。此处保存不含凭证的配置方案；各机的套餐密钥与登录保留在本机。

## Codex / ChatGPT：固定官方原生连接

2026-11-13 已明确取消 Magpie 对 Codex / ChatGPT 的模型转发，使用官方 ChatGPT Pro 登录。GLM、Kimi、input、Ciii 等渠道继续留给其他工具。

- 本机及 Windows / Mac 模板均设置 `model_provider = "openai"`、`forced_login_method = "chatgpt"`，不设置模型服务的 `openai_base_url` / `chatgpt_base_url` 覆盖。
- 移除本机 `[model_providers.magpie]` 及其转发授权头。旧聊天用到的 `custom` / `ai_input` 标识仅保留为官方登录兼容入口：`requires_openai_auth = true`，无 `base_url`、转发令牌或自定义授权头。
- Magpie 本机 `providers.json` 的 `id: "codex"` 设置 `off: true`，禁止其调用 ChatGPT 订阅账号；`stash.json` 保持 `"codex.disconnected": "1"`。不要为测试或切换其他工具而重新接管 Codex。
- Windows 模板已去除旧的 `127.0.0.1:15721` 模型代理与 CC Switch 模型目录覆盖；Mac 模板已去除 input 模型地址。Windows 默认模型与本机保持 `gpt-6-astra`、`max`。
- ChatGPT 官方登录与普通网络代理是不同层面：本次没有改动系统网络代理，也没有复制或更换官方登录凭证。

验证：重启 Magpie 后，新默认入口与旧聊天兼容入口各完成一次官方 Codex 临时会话测试，均返回 `OFFICIAL_OK`；期间 Magpie 新增 Codex 转发记录为 0。两个测试均不保存聊天会话。其他提供商及套餐路由组与修改前一致。

恢复点：`C:\Users\Lzw\Documents\Magpie配置备份\20261113-135237-official-only`。原始配置备份含敏感信息，仅保存在本机。同步只提交脱敏模板与本文档，不直接回收含凭证的本机完整配置。

依据：[OpenAI 配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)、[Magpie 0.1.3969 提供商开关](https://github.com/yetone/magpie/blob/v0.1.3969/internal/provider/provider.go)、[断开接管实现](https://github.com/yetone/magpie/blob/v0.1.3969/internal/agent/applied.go)。

## 分工

| 路由 ID | 用途 | 首选 | 备用 |
| --- | --- | --- | --- |
| `group/plan-writing` | 长文阅读、资料整合、课程笔记、报告与文字编辑 | `kimi-code-cn/k3.1-pro:high` | `zhipu/glm-5.3:high` |
| `group/plan-research` | 联网检索后的分析、日常任务、代码工作 | `zhipu/glm-5.3:high` | `kimi-code-cn/k3.1-pro:high` |
| `group/plan-fast` | 标题、摘录、短改写、上下文压缩 | `zhipu/glm-5.3-flash:low` | `kimi-code-cn/k3.1-pro:low` |

各组使用 `routing=order`、`stays=session`，上下文对客户端保守声明为 `256k`。只有首选不能服务时才使用备用；两个套餐用尽时不自动转入额外付费 API。Kimi 保持思考模式，不使用消耗倍数更高的 Highspeed 版本。

## 客户端

- Codex / ChatGPT：使用官方原生连接与 ChatGPT Pro 登录，不经过 Magpie 或其他模型中转。
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

## input / Ciii 余额渠道

2026-11-12 在 Windows 本机核查并清理了失效入口，原有套餐分工与 Codex GPT Pro 设置保持不变。

- `input`：将能查询钱包余额的密钥提升为主密钥；无有效订阅的旧密钥保留在 `keys[]`，设置 `off: true`。模型目录更新为该钱包入口返回的 9 个 Claude 型号。
- `ciii-codex`：保留有效钱包主密钥；将所属分组已删除的备用密钥设置为 `off: true`。模型目录按接口查询结果更新为 10 个型号，新增 `gpt-6`，移除旧目录中的 `gpt-5.6-luna`。
- 独立的 `ai-input` 密钥返回 `INVALID_API_KEY`，该提供商设置 `off: true`，保留配置供后续更换凭证。
- 保留原有服务地址与协议设置。两个余额渠道不加入 GLM/Kimi 套餐的自动备用组。

配置通过原子替换 `providers.json` 热重载，无需重启。实测网关目录显示 input 9 个、Ciii 10 个、旧 ai-input 0 个；两次转发的候选密钥均只有有效钱包密钥，未再尝试失效密钥。

截至当日 18:47，服务尚未恢复：input 的直连与网关请求均出现 `Upstream authentication failed`；Ciii 均出现 HTTP 502，网关记录为 Cloudflare 收到源站无效或不完整响应。余额与模型查询成功不能证明生成请求成功；本次没有将这两家设为工作默认模型。商家需先恢复上游认证或源站服务，若商家要求更新客户端密钥或地址，再单独更换对应入口。

本次恢复点：`C:\Users\Lzw\Documents\Magpie配置备份\20261112-184127-input-ciii`。密钥及原始备份只留在本机，不加入此仓库；其他设备需使用各自凭证复现上述启停设置。

字段依据：[Magpie 0.1.3859 密钥配置](https://github.com/yetone/magpie/blob/v0.1.3859/internal/provider/keys.go)、[配置监听](https://github.com/yetone/magpie/blob/v0.1.3859/internal/gateway/gateway.go)。
