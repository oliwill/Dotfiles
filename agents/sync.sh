#!/usr/bin/env bash
# sync.sh — 终端启动时自动对齐：git pull + apply
# 无网络或本地有未提交改动时静默跳过，绝不阻塞终端启动
# 用法: bash agents/sync.sh

set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO" || exit 0

# 无网络时静默退出（3 秒超时）
git fetch --quiet --timeout=3 origin 2>/dev/null || exit 0

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse '@{u}' 2>/dev/null || echo "$LOCAL")

if [ "$LOCAL" != "$REMOTE" ]; then
    if git pull --ff-only --quiet 2>/dev/null; then
        bash agents/apply.sh
        echo "[dotsync] 已对齐到 $(git rev-parse --short HEAD)"
    else
        echo "[dotsync] 本地有未提交改动，跳过自动对齐（可先运行 bash agents/push.sh）"
    fi
fi
exit 0
