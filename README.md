# My Dotfiles

我的个人配置文件仓库，旨在提供一个高效、美观且现代化的开发环境。核心基于 **Zsh** 和 **Neovim**，并集成了大量现代化的 CLI 工具。

## 🚀 快速开始

### 安装

只需一行命令即可完成从环境检查、依赖安装到配置链接的全过程。

```bash
# 克隆仓库
git clone https://github.com/yourusername/Dotfiles.git ~/Dotfiles

# 运行初始化脚本
cd ~/Dotfiles
bash init.sh
```

**`init.sh` 会自动执行以下操作：**
1.  **检测系统**：支持 Debian/Ubuntu, RHEL/CentOS, Arch Linux, macOS。
2.  **安装基础依赖**：`git`, `curl`, `build-essential`, `ripgrep`, `fd`, `bat`, `lsd`, `zoxide` 等。
3.  **安装 Zsh & Zinit**：如果未安装会自动安装。
4.  **安装 fzf**：确保模糊搜索工具可用。
5.  **链接配置**：自动备份现有配置并创建软链接。

---

## ✨ 核心特性

### 🤖 AI Agent 配置同步 (agents/)

跨设备同步 Claude Code / Pi / Codex / OMP 的配置与 300+ Skills，密钥占位符化（1Password 管理），打开终端自动从远端对齐。详见 **[agents/README.md](agents/README.md)**。

### 🐚 Shell 环境 (Zsh)

- **插件管理器**: [Zinit](https://github.com/zdharma-continuum/zinit) - 极速加载，延迟加载机制。
- **提示符**: [Powerlevel10k](https://github.com/romkatv/powerlevel10k) - 瞬时启动，信息丰富，高度可定制。
- **自动补全**: 
    - `zsh-autosuggestions`: 基于历史记录的灰色自动建议。
    - `fzf-tab`: 使用 fzf 替换默认的 Tab 选择菜单，支持实时预览（如 `cd` 预览目录，`kill` 预览进程）。
    - `commands`: 针对 `git`, `docker`, `systemd` 等的丰富补全源。
- **语法高亮**: `zsh-syntax-highlighting` - 实时检查命令语法正确性。
- **Vi 模式**: `zsh-vi-mode` - 更好的 Vim 键位支持。
- **智能跳转**: `zoxide` - 比 `cd` 更智能的目录跳转（`z dir`）。

### 🛠️ 现代命令行工具集

本配置集成了大量 Rust 编写的现代替代工具：

| 传统工具 | 现代替代 | 描述 |
| :--- | :--- | :--- |
| `ls` | **[lsd](https://github.com/lsd-rs/lsd)** / **[eza](https://github.com/eza-community/eza)** | 带图标和颜色的文件列表 |
| `cat` | **[bat](https://github.com/sharkdp/bat)** | 带语法高亮和 Git 集成的文件查看器 |
| `grep` | **[ripgrep (rg)](https://github.com/BurntSushi/ripgrep)** | 极速全文本搜索 |
| `find` | **[fd](https://github.com/sharkdp/fd)** | 简单快速的文件查找 |
| `cd` | **[zoxide](https://github.com/ajeetdsouza/zoxide)** | 智能目录跳转 |
| `top` | **[btop](https://github.com/aristocratos/btop)** | 炫酷的系统资源监控 |
| `diff` | **[delta](https://github.com/dandavison/delta)** | 更好的 Git diff 查看器 |
| `git` | **[lazygit](https://github.com/jesseduffield/lazygit)** | 终端 Git UI 神器 |
| - | **[yazi](https://github.com/sxyazi/yazi)** | 极速终端文件管理器，支持图片预览 |
| - | **[zellij](https://github.com/zellij-org/zellij)** | 现代化的终端复用器 (Tmux 替代) |
| - | **[atuin](https://github.com/atuinsh/atuin)** | 魔法般的 Shell 历史记录同步与搜索 |
| - | **[superfile](https://github.com/MHNightCat/superfile)** | 另一款强大的终端文件管理器 |

### ⌨️ 输入法 (Rime)

- **配置**: `rime/sbxlm.yaml`
- **方案**: 声笔系列 (sbzr)
- **管理**: 提供了 `sbzr`, `install:rime` 等别名工具用于管理词库和同步。

---

## 📂 目录结构

```text
~/Dotfiles
├── init.sh             # 一键安装脚本
├── zshrc               # Zsh 入口配置
├── aliases.conf        # 别名统一定义
├── config/             # 各种工具的配置文件 (nvim, yazi, wezterm 等)
├── plugins/            # Zsh 插件配置与加载逻辑
│   ├── zinit/          # Zinit 初始化
│   ├── prompt/         # P10k 主题配置
│   ├── tools/          # 核心工具安装 (btop, yazi 等)
│   ├── completion/     # 补全配置 (fzf-tab)
│   └── ...
├── scripts/            # 实用脚本库
│   ├── install/        # 安装脚本 (rime, nvim 等)
│   ├── system/         # 系统维护 (backup, disk usage)
│   └── utils/          # 通用工具 (extract, url_encode)
├── dotlink/            # 自研的软链接管理工具
├── agents/             # AI Agent 配置同步层（Claude/Pi/Codex/OMP，见 agents/README.md）
└── tools/              # 随处可用的便携脚本
```

---

## 🔧 常用别名 (Aliases)

详细列表请查看 `aliases.conf`，以下是常用精选：

- **文件管理**
    - `extract`: 通用解压（自动识别 tar, zip, 7z 等）。
    - `open`: 在文件管理器中打开当前目录。
    - `packtar`: 打包当前目录。
    - `unzip:here`: 批量解压。

- **Git**
    - `lazy`: 启动 Lazygit。
    - `git:clean`: 清理未跟踪文件。
    - `dotfiles:push`: 自动提交并推送 Dotfiles 更新。

- **开发**
    - `vim` / `vi`: 智能映射到 Neovim。
    - `rjz` / `rzj`: 中日互译 (Translate Shell)。
    - `url:encode` / `url:decode`: URL 编解码。

- **系统**
    - `update`: 系统更新 (apt/dnf/pacman/brew 智能识别)。
    - `disk:usage`: 查看目录占用。
    - `port:check`: 检查端口占用。

---

## 🔗 配置同步 (Dotlink)

本仓库包含一套自研的配置同步工具 `dotlink`，位于 `dotlink/` 目录下。

- `dotlink`: 自动扫描并创建软链接。
- `dotsync`: 更加高级的配置同步管理，支持备份、恢复和多机同步提交。
    - `dotsync push`: 提交更改。
    - `dotsync pull`: 拉取更新。
    - `dotsync backup`: 备份本地重要配置。

---

## 📝 许可证

MIT License
