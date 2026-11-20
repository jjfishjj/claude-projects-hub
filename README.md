# Claude Projects Hub

把本機所有 Claude / Codex 專案盤點、部署到 GitHub Pages，並集中成一頁作品集索引。

**上線位置：** https://jjfishjj.github.io/claude-projects-hub/

## 這個 repo 做什麼

| 檔案 | 用途 |
| --- | --- |
| `scripts/scan.sh` | 掃描 GitHub 帳號下所有公開 repo 的 Pages 狀態，產生 `inventory.json` |
| `scripts/_scan.py` | scan.sh 的 Python 後端（查 Pages API、排序、輸出 JSON） |
| `scripts/deploy-pages.sh` | 對單一 repo 開啟 Pages。`jekyll` 模式適用純 Markdown repo，`workflow` 模式適用前端 build repo |
| `scripts/build_hub.py` | 讀 `inventory.json` + `categories.json`，產生 `index.html` |
| `inventory.json` | 自動產生，勿手改 |
| `categories.json` | 手動維護：repo 的分類與顯示描述覆寫 |
| `index.html` | 自動產生的產品作品集與專案索引頁 |

首頁先展示 4 個可體驗的產品原型，再呈現其他產品案例；GPU、數位孿生與工具類專案收在可展開的研究索引中。`categories.json` 的 `featured` 欄位維護精選案例與頁面可見的使用者旅程，文案只描述線上頁面能看到的功能，不宣稱未驗證的商業成果。

## 更新流程

```bash
./scripts/scan.sh jjfishjj      # 重新掃描 Pages 狀態
python3 scripts/build_hub.py    # 重建 index.html
git add -A && git commit -m "chore: refresh inventory" && git push
```

## 新增一個專案到 Pages

```bash
./scripts/deploy-pages.sh <repo-name>            # Markdown / 文件型
./scripts/deploy-pages.sh <repo-name> workflow   # Vite / React 等需 build 的前端
```

部署完後把 repo 加進 `categories.json`，再跑一次更新流程。

## 設計取捨

- **不動本機 working tree**：`deploy-pages.sh` 走 GitHub Contents API 直接寫遠端分支，
  所以有大量未提交變更的 repo（例如 `Documents/NVIDIA`）也能安全部署。
- **Markdown repo 用 Jekyll `cayman` 主題**：不必寫任何 HTML，README 與 `docs/` 直接變成網站，
  `jekyll-relative-links` 讓 `docs/*.md` 之間的連結自動可點。
- **私有 repo 一律不碰**：私有 repo 開 Pages 需付費方案，且內容可能含商業資訊。
