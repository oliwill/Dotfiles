#!/usr/bin/env bash
# apply.sh — 把仓库 agents/ 配置应用到本机各 Agent 配置目录
# - skills 同步到 ~/.agents/skills、~/.pi/agent/skills、~/.claude/skills 三处
# - 按 OS 自动选择配置变体（settings-windows.json / config-windows.toml.tmpl）
# - 模板中的 __XXX__ 占位符用 ~/.config/dotfiles/secrets.env 渲染，密钥永不入库
# 用法: bash agents/apply.sh

set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS_FILE="${SECRETS_FILE:-$HOME/.config/dotfiles/secrets.env}"

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) OS=windows ;;
    Darwin*)              OS=mac ;;
    *)                    OS=linux ;;
esac
echo "[apply] OS = $OS"

# 加载密钥（存在才加载；只渲染模板时才需要）
[ -f "$SECRETS_FILE" ] && source "$SECRETS_FILE" || true

# 通用模板渲染：把 __VAR__ 替换为同名环境变量的值
render() {
    local tmpl="$1" dest="$2"
    local content missing=0
    content="$(cat "$tmpl")"
    while IFS= read -r ph; do
        local var="${ph:2:${#ph}-4}"
        local val="${!var:-}"
        if [ -z "$val" ]; then
            echo "[apply] 警告: $var 未在 $SECRETS_FILE 中设置，$dest 未渲染"
            missing=1
            continue
        fi
        content="${content//$ph/$val}"
    done < <(grep -oE '__[A-Z0-9_]+__' "$tmpl" | sort -u)
    [ "$missing" = 1 ] && return 1
    mkdir -p "$(dirname "$dest")"
    printf '%s\n' "$content" > "$dest"
    chmod 600 "$dest"
    echo "[渲染] $dest"
}

# 1. Skills（三处保持一致）
# 用 tar 管道复制以排除嵌套仓库/缓存；目标只读文件（git pack）先解锁
sync_skills() {
    local target="$1"
    mkdir -p "$target"
    chmod -R +w "$target" 2>/dev/null || true
    if (cd "$AGENTS_DIR/skills" && tar cf - --exclude='.git' --exclude='__pycache__' --exclude='node_modules' --exclude='.DS_Store' .) | (cd "$target" && tar xf - 2>/dev/null); then
        echo "[同步] $target ($(ls "$AGENTS_DIR/skills" | wc -l | tr -d ' ') skills)"
    else
        echo "[apply] 警告: $target 部分文件同步失败（不影响其余配置）"
    fi
}
sync_skills "$HOME/.agents/skills"
sync_skills "$HOME/.pi/agent/skills"
sync_skills "$HOME/.claude/skills"

# 2. Pi
mkdir -p "$HOME/.pi/agent"
cp "$AGENTS_DIR/pi/settings.json" "$HOME/.pi/agent/settings.json"
echo "[同步] ~/.pi/agent/settings.json"
[ -f "$AGENTS_DIR/pi/models.json.tmpl" ] && render "$AGENTS_DIR/pi/models.json.tmpl" "$HOME/.pi/agent/models.json" || true

# 3. Claude Code
mkdir -p "$HOME/.claude"
claude_settings="$AGENTS_DIR/claude/settings.json"
[ -f "$AGENTS_DIR/claude/settings-$OS.json" ] && claude_settings="$AGENTS_DIR/claude/settings-$OS.json"
cp "$claude_settings" "$HOME/.claude/settings.json"
echo "[同步] ~/.claude/settings.json ($(basename "$claude_settings"))"
if [ -d "$AGENTS_DIR/claude/rules" ]; then
    mkdir -p "$HOME/.claude/rules"
    cp -r "$AGENTS_DIR/claude/rules/." "$HOME/.claude/rules/"
    echo "[同步] ~/.claude/rules"
fi
[ -f "$AGENTS_DIR/claude/CLAUDE.md" ] && cp "$AGENTS_DIR/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md" && echo "[同步] ~/.claude/CLAUDE.md"

# 4. Codex（模板渲染）
codex_tmpl="$AGENTS_DIR/codex/config.toml.tmpl"
[ -f "$AGENTS_DIR/codex/config-$OS.toml.tmpl" ] && codex_tmpl="$AGENTS_DIR/codex/config-$OS.toml.tmpl"
render "$codex_tmpl" "$HOME/.codex/config.toml" || echo "[apply] 跳过 codex 配置（缺密钥），请先配置 $SECRETS_FILE"
[ -f "$AGENTS_DIR/codex/AGENTS.md" ] && cp "$AGENTS_DIR/codex/AGENTS.md" "$HOME/.codex/AGENTS.md" && echo "[同步] ~/.codex/AGENTS.md"

# 5. OMP
[ -f "$AGENTS_DIR/omp/models.yml.tmpl" ] && render "$AGENTS_DIR/omp/models.yml.tmpl" "$HOME/.omp/agent/models.yml" || true
[ -f "$AGENTS_DIR/omp/config.yml" ] && mkdir -p "$HOME/.omp/agent" && cp "$AGENTS_DIR/omp/config.yml" "$HOME/.omp/agent/config.yml" && echo "[同步] ~/.omp/agent/config.yml"

echo "[apply] 完成"
