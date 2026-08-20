#!/usr/bin/env bash
# 對一個公開 repo 開啟 GitHub Pages。
#
#   ./scripts/deploy-pages.sh <repo> [mode]
#
#   mode = jekyll (預設)  純 Markdown repo：塞一份 _config.yml，從預設分支根目錄 serve
#          workflow       前端 build repo：改用 GitHub Actions workflow 來源（需自備 workflow）
#
# 用 GitHub Contents API 直接寫遠端，不會動到本機 working tree。
set -euo pipefail
USER="${GH_USER:-jjfishjj}"
REPO="${1:?usage: deploy-pages.sh <repo> [jekyll|workflow]}"
MODE="${2:-jekyll}"

BRANCH=$(gh api "repos/$USER/$REPO" --jq '.default_branch')
echo "→ $USER/$REPO (branch: $BRANCH, mode: $MODE)"

if [ "$MODE" = "jekyll" ]; then
  if gh api "repos/$USER/$REPO/contents/_config.yml" >/dev/null 2>&1; then
    echo "  _config.yml 已存在，略過"
  else
    DESC=$(gh api "repos/$USER/$REPO" --jq '.description // ""')
    CONTENT=$(printf 'theme: jekyll-theme-cayman\ntitle: %s\ndescription: >-\n  %s\nexclude:\n  - venv\n  - node_modules\n' \
      "$(echo "$REPO" | tr '-' ' ')" "$DESC" | base64)
    gh api -X PUT "repos/$USER/$REPO/contents/_config.yml" \
      -f message="chore: add Jekyll config for GitHub Pages" \
      -f content="$CONTENT" -f branch="$BRANCH" --jq '.commit.sha' | cut -c1-8 | xargs echo "  _config.yml committed:"
  fi
  gh api -X POST "repos/$USER/$REPO/pages" \
    -f "source[branch]=$BRANCH" -f "source[path]=/" --jq '.html_url' 2>/dev/null \
    || gh api -X PUT "repos/$USER/$REPO/pages" \
         -f "source[branch]=$BRANCH" -f "source[path]=/" >/dev/null
else
  gh api -X POST "repos/$USER/$REPO/pages" -f "build_type=workflow" --jq '.html_url' 2>/dev/null \
    || gh api -X PUT "repos/$USER/$REPO/pages" -f "build_type=workflow" >/dev/null
fi

echo "  → https://$USER.github.io/$REPO/"
echo "  等待 build..."
for _ in $(seq 1 20); do
  ST=$(gh api "repos/$USER/$REPO/pages/builds/latest" --jq '.status' 2>/dev/null || echo "?")
  [ "$ST" = "built" ] && { echo "  ✅ built"; exit 0; }
  [ "$ST" = "errored" ] && { gh api "repos/$USER/$REPO/pages/builds/latest" --jq '.error.message'; exit 1; }
  sleep 6
done
echo "  ⏳ 仍在 build，稍後用 gh api repos/$USER/$REPO/pages/builds/latest 查看"
