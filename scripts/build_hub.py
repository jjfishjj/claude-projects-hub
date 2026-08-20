"""讀 inventory.json + categories.json，產生 index.html 作品集索引頁。"""
import json, html, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
inv = json.loads((ROOT / "inventory.json").read_text())
cfg = json.loads((ROOT / "categories.json").read_text())
cmap, order = cfg["repos"], cfg["order"]

live = [r for r in inv if r["pages_url"]]
offline = [r for r in inv if not r["pages_url"]]

buckets = {c: [] for c in order}
for r in live:
    meta = cmap.get(r["name"], {})
    r["desc"] = meta.get("desc") or r["description"] or "—"
    buckets.setdefault(meta.get("cat", "其他"), []).append(r)
for v in buckets.values():
    v.sort(key=lambda x: x["pushed_at"], reverse=True)

e = html.escape

def card(r):
    lang = f'<span class="tag">{e(r["language"])}</span>' if r["language"] else ""
    return f"""      <a class="card" href="{e(r['pages_url'])}">
        <h3>{e(r['name'])}</h3>
        <p>{e(r['desc'])}</p>
        <div class="meta">{lang}<span class="tag date">{e(r['pushed_at'])}</span>
          <span class="repo" data-href="{e(r['repo_url'])}">source ↗</span></div>
      </a>"""

sections = []
for cat in order:
    items = buckets.get(cat) or []
    if not items:
        continue
    sections.append(
        f'    <section>\n      <h2>{e(cat)} <span class="count">{len(items)}</span></h2>\n'
        f'      <div class="grid">\n' + "\n".join(card(r) for r in items) + "\n      </div>\n    </section>"
    )

offline_rows = "\n".join(
    f'        <li><a href="{e(r["repo_url"])}">{e(r["name"])}</a>'
    f'<span>{e((r["description"] or "—")[:90])}</span></li>'
    for r in sorted(offline, key=lambda x: x["name"].lower()))

built = datetime.date.today().isoformat()

HTML = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Claude Projects Hub — Jerome Kuo</title>
<meta name="description" content="本機 Claude / Codex 專案的 GitHub Pages 部署索引，共 {len(live)} 個已上線站點。">
<style>
:root {{
  --bg:#fbfbfa; --panel:#fff; --border:#e6e3dd; --fg:#1f1d1a; --muted:#6d675e;
  --accent:#c25a2b; --tagbg:#f2efe9; --shadow:0 1px 2px rgba(0,0,0,.05);
}}
@media (prefers-color-scheme:dark) {{
  :root:not([data-theme=light]) {{
    --bg:#16150f; --panel:#1e1d17; --border:#332f26; --fg:#eeebe4; --muted:#9c9486;
    --accent:#e4834f; --tagbg:#27251d; --shadow:none;
  }}
}}
*{{box-sizing:border-box}}
body {{
  margin:0; background:var(--bg); color:var(--fg);
  font:16px/1.6 ui-sans-serif,-apple-system,"Noto Sans TC",system-ui,sans-serif;
  -webkit-font-smoothing:antialiased;
}}
.wrap{{max-width:1080px;margin:0 auto;padding:56px 24px 80px}}
header{{border-bottom:1px solid var(--border);padding-bottom:28px;margin-bottom:12px}}
h1{{font-size:clamp(28px,4vw,40px);margin:0 0 8px;letter-spacing:-.02em}}
.sub{{color:var(--muted);margin:0;max-width:60ch}}
.stats{{display:flex;gap:28px;margin-top:24px;flex-wrap:wrap}}
.stat b{{display:block;font-size:26px;line-height:1.2;color:var(--accent)}}
.stat span{{font-size:13px;color:var(--muted)}}
section{{margin-top:44px}}
h2{{font-size:15px;text-transform:uppercase;letter-spacing:.09em;color:var(--muted);
   margin:0 0 16px;display:flex;align-items:center;gap:10px;font-weight:600}}
.count{{background:var(--tagbg);color:var(--muted);border-radius:99px;
  padding:1px 9px;font-size:12px;letter-spacing:0}}
.grid{{display:grid;gap:14px;grid-template-columns:repeat(auto-fill,minmax(288px,1fr))}}
.card{{display:block;background:var(--panel);border:1px solid var(--border);border-radius:12px;
  padding:18px 18px 14px;text-decoration:none;color:inherit;box-shadow:var(--shadow);
  transition:border-color .15s,transform .15s}}
.card:hover{{border-color:var(--accent);transform:translateY(-2px)}}
.card h3{{margin:0 0 7px;font-size:16px;font-weight:600;word-break:break-word}}
.card p{{margin:0 0 14px;font-size:13.5px;color:var(--muted);line-height:1.55}}
.meta{{display:flex;gap:7px;align-items:center;flex-wrap:wrap}}
.tag{{background:var(--tagbg);color:var(--muted);border-radius:5px;padding:2px 7px;font-size:11.5px}}
.repo{{margin-left:auto;font-size:11.5px;color:var(--accent);opacity:.85}}
details{{margin-top:48px;border-top:1px solid var(--border);padding-top:24px}}
summary{{cursor:pointer;color:var(--muted);font-size:14px}}
details ul{{list-style:none;padding:0;margin:16px 0 0;
  display:grid;gap:8px;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))}}
details li{{font-size:13px;display:flex;flex-direction:column;gap:2px}}
details li a{{color:var(--fg);text-decoration:none;border-bottom:1px solid var(--border)}}
details li a:hover{{color:var(--accent)}}
details li span{{color:var(--muted);font-size:12px}}
footer{{margin-top:56px;padding-top:20px;border-top:1px solid var(--border);
  color:var(--muted);font-size:12.5px}}
footer a{{color:var(--accent)}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Claude Projects Hub</h1>
    <p class="sub">本機 Claude / Codex 專案的 GitHub Pages 部署索引。每張卡片連到已上線的站點，
       右下角 source 連到原始碼 repo。</p>
    <div class="stats">
      <div class="stat"><b>{len(live)}</b><span>已上線 Pages</span></div>
      <div class="stat"><b>{len(inv)}</b><span>公開 repo</span></div>
      <div class="stat"><b>{len([c for c in order if buckets.get(c)])}</b><span>分類</span></div>
      <div class="stat"><b>{built}</b><span>最後更新</span></div>
    </div>
  </header>

{chr(10).join(sections)}

  <details>
    <summary>尚未部署 Pages 的公開 repo（{len(offline)}）</summary>
    <ul>
{offline_rows}
    </ul>
  </details>

  <footer>
    由 <a href="https://github.com/jjfishjj/claude-projects-hub">claude-projects-hub</a> 自動產生 ·
    重跑 <code>./scripts/scan.sh &amp;&amp; python3 scripts/build_hub.py</code> 即可更新
  </footer>
</div>
<script>
// 卡片內的 source 連結：獨立導向 repo，不觸發外層卡片連結
document.querySelectorAll('.repo').forEach(function (el) {{
  el.addEventListener('click', function (ev) {{
    ev.preventDefault(); ev.stopPropagation();
    window.location.href = el.dataset.href;
  }});
}});
</script>
</body>
</html>
"""
(ROOT / "index.html").write_text(HTML)
print(f"index.html built: {len(live)} live / {len(inv)} public repos")
