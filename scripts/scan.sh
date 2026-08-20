#!/usr/bin/env bash
# 掃描 GitHub 帳號下所有公開 repo 的 Pages 狀態，產生 inventory.json
# 用法: ./scripts/scan.sh [github-user]
set -euo pipefail
USER="${1:-jjfishjj}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
gh repo list "$USER" --limit 200 --json name,description,visibility,url,pushedAt,primaryLanguage \
  | python3 "$ROOT/scripts/_scan.py" "$USER" "$ROOT/inventory.json"
