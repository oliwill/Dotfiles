#!/bin/bash
# apply-secrets.sh — 用 ~/.config/dotfiles/secrets.env 渲染各 Agent 含密钥的配置
# 模板中的 __GLM_API_KEY__ / __ZHIPU_ANTHROPIC_TOKEN__ 会被替换为真实值
# 渲染结果只写入各 Agent 的本地配置路径，永不写回本仓库

set -euo pipefail

AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECRETS_FILE="${SECRETS_FILE:-$HOME/.config/dotfiles/secrets.env}"

if [ ! -f "$SECRETS_FILE" ]; then
    echo "缺少 $SECRETS_FILE"
    echo "请执行: mkdir -p ~/.config/dotfiles && cp $AGENTS_DIR/secrets.env.example $SECRETS_FILE"
    echo "然后填入真实密钥后重试"
    exit 1
fi

# shellcheck disable=SC1090
source "$SECRETS_FILE"

render() {
    local tmpl="$1" dest="$2"
    sed -e "s/__GLM_API_KEY__/${GLM_API_KEY}/g" \
        -e "s/__ZHIPU_ANTHROPIC_TOKEN__/${ZHIPU_ANTHROPIC_TOKEN}/g" \
        "$tmpl" > "$dest"
    chmod 600 "$dest"
    echo "[渲染] $dest"
}

[ -n "${GLM_API_KEY:-}" ] || { echo "GLM_API_KEY 未设置"; exit 1; }
[ -n "${ZHIPU_ANTHROPIC_TOKEN:-}" ] || { echo "ZHIPU_ANTHROPIC_TOKEN 未设置"; exit 1; }

mkdir -p "$HOME/.pi/agent" "$HOME/.omp/agent" "$HOME/.codex"
render "$AGENTS_DIR/pi/models.json.tmpl"    "$HOME/.pi/agent/models.json"
render "$AGENTS_DIR/omp/models.yml.tmpl"    "$HOME/.omp/agent/models.yml"
render "$AGENTS_DIR/codex/config.toml.tmpl" "$HOME/.codex/config.toml"

echo "完成。注意 Claude Code 的 token 由 ~/.claude/settings.local.json 承载（本机独立维护）"
