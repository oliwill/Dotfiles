#!/usr/bin/env bash
# push.sh — 把本机改动回收到仓库并推送（apply.sh 的反向操作）
# 从本机 live 配置重新导入仓库，密钥自动替换回占位符，然后提交推送
# 用法: bash agents/push.sh ["提交说明"]

set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(dirname "$AGENTS_DIR")"
SECRETS_FILE="${SECRETS_FILE:-$HOME/.config/dotfiles/secrets.env}"

case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) OS=windows ;;
    Darwin*)              OS=mac ;;
    *)                    OS=linux ;;
esac

[ -f "$SECRETS_FILE" ] && source "$SECRETS_FILE" || true

# 把值替换回占位符（防止密钥入库）
mask() { # mask <file> <占位符> <值>
    local file="$1" ph="$2" val="${3:-}"
    [ -n "$val" ] && sed -i "s|$val|$ph|g" "$file" || true
}

# 1. Skills：以 ~/.agents/skills 为源（pi 独有的 modlens 也收编）
mkdir -p "$AGENTS_DIR/skills"
cp -r "$HOME/.agents/skills/." "$AGENTS_DIR/skills/"
[ -d "$HOME/.pi/agent/skills/modlens" ] && cp -r "$HOME/.pi/agent/skills/modlens" "$AGENTS_DIR/skills/"
find "$AGENTS_DIR/skills" -depth -type d \( -name .git -o -name __pycache__ -o -name node_modules \) -exec rm -rf {} + 2>/dev/null || true
find "$AGENTS_DIR/skills" -name .DS_Store -delete 2>/dev/null || true
echo "[回收] skills"

# 2. Pi
cp "$HOME/.pi/agent/settings.json" "$AGENTS_DIR/pi/settings.json" 2>/dev/null || true
echo "[回收] pi/settings.json"

# 3. Claude
claude_dest="$AGENTS_DIR/claude/settings.json"
[ "$OS" = windows ] && claude_dest="$AGENTS_DIR/claude/settings-windows.json"
cp "$HOME/.claude/settings.json" "$claude_dest" 2>/dev/null || true
[ -d "$HOME/.claude/rules" ] && mkdir -p "$AGENTS_DIR/claude/rules" && cp -r "$HOME/.claude/rules/." "$AGENTS_DIR/claude/rules/"
[ -f "$HOME/.claude/CLAUDE.md" ] && cp "$HOME/.claude/CLAUDE.md" "$AGENTS_DIR/claude/CLAUDE.md"
echo "[回收] claude ($claude_dest)"

# 4. Codex：重新生成模板并遮蔽密钥
codex_dest="$AGENTS_DIR/codex/config.toml.tmpl"
[ "$OS" = windows ] && codex_dest="$AGENTS_DIR/codex/config-windows.toml.tmpl"
if [ -f "$HOME/.codex/config.toml" ]; then
    cp "$HOME/.codex/config.toml" "$codex_dest"
    mask "$codex_dest" "__GLM_API_KEY__" "${GLM_API_KEY:-}"
    mask "$codex_dest" "__ZHIPU_ANTHROPIC_TOKEN__" "${ZHIPU_ANTHROPIC_TOKEN:-}"
    mask "$codex_dest" "__UTOOLS_MCP_KEY__" "${UTOOLS_MCP_KEY:-}"
    mask "$codex_dest" "__PROXY_BEARER_TOKEN__" "${PROXY_BEARER_TOKEN:-}"
    echo "[回收] codex ($codex_dest，密钥已遮蔽)"
fi
[ -f "$HOME/.codex/AGENTS.md" ] && cp "$HOME/.codex/AGENTS.md" "$AGENTS_DIR/codex/AGENTS.md"

# 5. 提交推送
cd "$REPO"
git add -A
if git diff --cached --quiet; then
    echo "[push] 无变更"
    exit 0
fi
msg="${1:-Update: $OS - $(date '+%Y-%m-%d %H:%M:%S')}"
git commit --quiet -m "$msg"
git push --quiet
echo "[push] 已推送: $msg"
