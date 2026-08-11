# AI Agent 配置同步层

跨设备同步 Claude Code / Pi / Codex / OMP 的配置与 Skills。密钥不入库，由本机 `secrets.env` 渲染（建议用 1Password 管理）。

## 目录结构

```
agents/
├── skills/                        # 唯一事实来源（~/.agents/skills 的全集）
├── pi/settings.json               # Pi 配置（packages 列表决定扩展，全平台共享）
├── claude/
│   ├── settings.json              # Claude 配置（Mac/Linux 基线）
│   ├── settings-windows.json      # Claude 配置（Windows 变体）
│   ├── CLAUDE.md / rules/         # 全局指令与规则
│   └── agents/                    # 子代理
├── codex/
│   ├── config.toml.tmpl           # Codex 配置（Mac 变体模板）
│   ├── config-windows.toml.tmpl   # Codex 配置（Windows 变体模板）
│   └── AGENTS.md
├── omp/                           # Oh My Pi
├── secrets.env.example            # 密钥模板（复制到 ~/.config/dotfiles/secrets.env）
├── apply.sh                       # 应用到本机（仓库 → 家目录）
├── sync.sh                        # 终端启动自动对齐（git pull + apply）
└── push.sh                        # 回收本机改动并推送（家目录 → 仓库 → 远端）
```

## 新设备接入

```bash
git clone https://github.com/oliwill/Dotfiles.git ~/Dotfiles
mkdir -p ~/.config/dotfiles
cp ~/Dotfiles/agents/secrets.env.example ~/.config/dotfiles/secrets.env
# 编辑 secrets.env，从 1Password 填入真实密钥
bash ~/Dotfiles/agents/apply.sh
```

## 自动对齐（打开终端时）

- **Windows**：已写入 PowerShell `$PROFILE`，后台静默执行 `sync.sh`，不阻塞启动。
- **macOS**：在 `~/.zshrc` 加一行：
  ```zsh
  (bash ~/Dotfiles/agents/sync.sh &!)
  ```

## 改了配置想同步到其他设备

```bash
dotsync-push            # PowerShell 函数，或直接 bash ~/Dotfiles/agents/push.sh
```

push.sh 会把本机 live 配置回收进仓库，**密钥自动替换回占位符**，然后提交推送。

## 注意事项

- **机器特定的运行时状态不同步**：codex 的 `hooks.state`、`node_repl`、`marketplaces`、`projects` 信任列表等由各机自行重新生成。
- **OS 变体**：apply.sh 按 `uname` 自动选择 `*-windows.*` 或基线文件；Windows 走本地代理（127.0.0.1:15721），Mac 走 ai.input.im，互不干扰。
- skills 目录中的嵌套 `.git`、`__pycache__`、`node_modules` 会被自动排除。
