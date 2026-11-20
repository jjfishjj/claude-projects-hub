"""Build a product-focused portfolio from inventory.json and categories.json."""
import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
inventory = json.loads((ROOT / "inventory.json").read_text())
config = json.loads((ROOT / "categories.json").read_text())
repo_config = config.get("repos", {})
category_order = config.get("order", [])
product_categories = set(config.get("product_categories", []))

live = [project for project in inventory if project.get("pages_url")]
offline = [project for project in inventory if not project.get("pages_url")]
projects_by_name = {project["name"]: project for project in live}

buckets = {category: [] for category in category_order}
for project in live:
    metadata = repo_config.get(project["name"], {})
    project["category"] = metadata.get("cat", "其他")
    project["display_description"] = (
        metadata.get("desc") or project.get("description") or "尚無專案說明。"
    )
    buckets.setdefault(project["category"], []).append(project)

for items in buckets.values():
    items.sort(key=lambda project: project.get("pushed_at", ""), reverse=True)

featured = []
missing_featured = []
for item in config.get("featured", []):
    project = projects_by_name.get(item["repo"])
    if project:
        featured.append((item, project))
    else:
        missing_featured.append(item["repo"])
featured_names = {project["name"] for _, project in featured}

product_projects = [
    project
    for category in category_order
    if category in product_categories
    for project in buckets.get(category, [])
    if project["name"] not in featured_names
]

lab_categories = [category for category in category_order if category not in product_categories]
for category in buckets:
    if category not in category_order and category not in product_categories:
        lab_categories.append(category)
lab_sections = [
    (category, [p for p in buckets.get(category, []) if p["name"] not in featured_names])
    for category in lab_categories
]
lab_sections = [(category, items) for category, items in lab_sections if items]
lab_count = sum(len(items) for _, items in lab_sections)

escape = html.escape


def project_card(project):
    language = project.get("language")
    language_tag = f'<span class="tag">{escape(language)}</span>' if language else ""
    return f"""<article class="project-card">
  <div class="project-tags"><span class="tag tag--category">{escape(project['category'])}</span>{language_tag}</div>
  <h3><a href="{escape(project['pages_url'], quote=True)}">{escape(project['name'])}</a></h3>
  <p>{escape(project['display_description'])}</p>
  <div class="project-links">
    <a href="{escape(project['pages_url'], quote=True)}">開啟體驗 <span aria-hidden="true">↗</span></a>
    <a href="{escape(project['repo_url'], quote=True)}" target="_blank" rel="noopener noreferrer">原始碼 <span aria-hidden="true">↗</span></a>
  </div>
</article>"""


def featured_card(item, project, index):
    flow = "".join(f"<li>{escape(step)}</li>" for step in item.get("journey", []))
    evidence = escape(item.get("evidence", "可直接開啟線上原型體驗。"))
    source_url = escape(project["repo_url"], quote=True)
    pages_url = escape(project["pages_url"], quote=True)
    lead_class = " featured-card--lead" if index == 0 else ""
    return f"""<article class="featured-card{lead_class}">
  <div class="featured-copy">
    <div class="featured-meta"><span class="eyebrow">{escape(item.get('eyebrow', '產品原型'))}</span><span class="case-number">CASE {index:02d}</span></div>
    <h3>{escape(item.get('title', project['name']))}</h3>
    <p class="featured-summary">{escape(item.get('summary', project['display_description']))}</p>
    <p class="evidence"><span class="evidence-label">可見產品範圍</span>{evidence}</p>
    <div class="featured-links">
      <a class="button button--primary" href="{pages_url}">體驗產品 <span aria-hidden="true">↗</span></a>
      <a class="text-link" href="{source_url}" target="_blank" rel="noopener noreferrer">查看原始碼 <span aria-hidden="true">↗</span></a>
    </div>
  </div>
  <div class="journey-panel">
    <span class="journey-label">使用者旅程</span>
    <ol>{flow}</ol>
  </div>
</article>"""


featured_html = "\n".join(
    featured_card(item, project, index)
    for index, (item, project) in enumerate(featured, start=1)
)

if product_projects:
    other_products_html = "\n".join(project_card(project) for project in product_projects)
    product_section = f"""<section class="section" id="more-products" aria-labelledby="more-products-title">
  <div class="section-heading">
    <div><p class="eyebrow">PRODUCT EXPLORATIONS</p><h2 id="more-products-title">更多產品原型與策略案例</h2></div>
    <span class="count">{len(product_projects)} 個</span>
  </div>
  <div class="project-grid">{other_products_html}</div>
</section>"""
else:
    product_section = ""

lab_html = "\n".join(
    f"""<section class="lab-section" aria-labelledby="lab-{index}-title">
  <div class="section-heading section-heading--compact">
    <h3 id="lab-{index}-title">{escape(category)}</h3><span class="count">{len(items)}</span>
  </div>
  <div class="project-grid">{'\n'.join(project_card(project) for project in items)}</div>
</section>"""
    for index, (category, items) in enumerate(lab_sections, start=1)
)

offline_rows = "\n".join(
    f"<li><a href=\"{escape(project['repo_url'], quote=True)}\" target=\"_blank\" rel=\"noopener noreferrer\">{escape(project['name'])}</a>"
    f"<span>{escape((project.get('description') or '尚無專案說明。')[:120])}</span></li>"
    for project in sorted(offline, key=lambda item: item["name"].lower())
)

built_date = datetime.date.today().isoformat()
featured_count = len(featured)

HTML = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI 產品作品集｜Jerome Kuo</title>
<meta name="description" content="Jerome Kuo 的 AI 產品作品集：以可體驗原型展示學習、語言與社群服務的產品流程，並收錄技術研究與專案。">
<meta property="og:title" content="AI 產品作品集｜Jerome Kuo">
<meta property="og:description" content="從問題定義到可體驗原型：先看精選產品案例，再探索技術研究與完整專案庫。">
<meta name="theme-color" content="#f5f4ef">
<style>
:root {{
  color-scheme: light dark;
  --bg:#f5f4ef; --panel:#fff; --panel-soft:#eeeee8; --line:#dfded5;
  --ink:#172923; --muted:#65736d; --accent:#23665c; --accent-hover:#164c43;
  --warm:#d58b61; --shadow:0 12px 34px rgba(24,43,36,.07);
}}
@media (prefers-color-scheme:dark) {{
  :root {{
    --bg:#111a17; --panel:#18231f; --panel-soft:#202d28; --line:#304139;
    --ink:#ecf2ed; --muted:#a5b4ab; --accent:#82c3ac; --accent-hover:#a4ddc7;
    --warm:#edaa7d; --shadow:0 12px 34px rgba(0,0,0,.18);
  }}
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{ margin:0; background:var(--bg); color:var(--ink); font:16px/1.65 ui-sans-serif,-apple-system,"Noto Sans TC",system-ui,sans-serif; -webkit-font-smoothing:antialiased; }}
a {{ color:inherit; }}
a:focus-visible, summary:focus-visible {{ outline:3px solid var(--warm); outline-offset:4px; border-radius:5px; }}
.skip-link {{ position:absolute; left:-999px; top:8px; z-index:5; background:var(--panel); padding:8px 12px; }}
.skip-link:focus {{ left:8px; }}
.wrap {{ width:min(1120px,100%); margin:0 auto; padding:28px 26px 72px; }}
.topline {{ display:flex; align-items:center; justify-content:space-between; gap:18px; color:var(--muted); font-size:12px; letter-spacing:.12em; text-transform:uppercase; }}
.topline a {{ color:var(--muted); text-decoration:none; letter-spacing:0; text-transform:none; }}
.hero {{ padding:66px 0 42px; border-bottom:1px solid var(--line); }}
.eyebrow {{ margin:0; color:var(--accent); font-size:11px; font-weight:750; letter-spacing:.13em; text-transform:uppercase; }}
h1 {{ max-width:850px; margin:12px 0 16px; font-size:clamp(36px,6vw,66px); line-height:1.12; letter-spacing:-.045em; }}
.hero-copy {{ max-width:680px; margin:0; color:var(--muted); font-size:clamp(16px,2vw,19px); }}
.hero-bottom {{ display:flex; align-items:center; justify-content:space-between; gap:24px; margin-top:30px; flex-wrap:wrap; }}
.hero-proof {{ display:flex; gap:10px 22px; flex-wrap:wrap; color:var(--muted); font-size:13px; }}
.hero-proof strong {{ color:var(--ink); font-size:16px; }}
.hero-actions {{ display:flex; align-items:center; gap:16px; flex-wrap:wrap; }}
.button {{ display:inline-flex; align-items:center; justify-content:center; gap:8px; min-height:44px; padding:10px 16px; border:1px solid transparent; border-radius:8px; font-size:14px; font-weight:700; text-decoration:none; transition:transform .18s ease,background .18s ease; }}
.button:hover {{ transform:translateY(-1px); }}
.button--primary {{ background:var(--accent); color:#fff; }}
.button--primary:hover {{ background:var(--accent-hover); }}
.text-link {{ color:var(--accent); font-size:13px; font-weight:700; text-decoration:none; }}
.section {{ margin-top:54px; }}
.section-heading {{ display:flex; align-items:flex-end; justify-content:space-between; gap:18px; margin-bottom:20px; }}
.section-heading h2 {{ margin:4px 0 0; font-size:clamp(24px,3vw,32px); line-height:1.25; letter-spacing:-.025em; }}
.section-heading p {{ margin:0; }}
.section-intro {{ max-width:650px; margin:8px 0 0; color:var(--muted); font-size:14px; }}
.count {{ color:var(--muted); font-size:12px; white-space:nowrap; }}
.featured-grid {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }}
.featured-card {{ min-width:0; display:flex; flex-direction:column; justify-content:space-between; gap:24px; padding:24px; border:1px solid var(--line); border-radius:16px; background:var(--panel); box-shadow:var(--shadow); }}
.featured-card--lead {{ grid-column:1/-1; display:grid; grid-template-columns:minmax(0,1.15fr) minmax(240px,.85fr); align-items:center; gap:34px; padding:30px; background:linear-gradient(135deg,var(--panel),color-mix(in srgb,var(--accent) 7%,var(--panel))); }}
.featured-meta {{ display:flex; align-items:center; justify-content:space-between; gap:12px; }}
.case-number {{ color:var(--muted); font-size:11px; letter-spacing:.1em; }}
.featured-card h3 {{ margin:12px 0 8px; font-size:clamp(22px,3vw,31px); line-height:1.25; letter-spacing:-.025em; }}
.featured-summary {{ margin:0; color:var(--muted); font-size:15px; }}
.evidence {{ margin:18px 0 0; padding-left:12px; border-left:2px solid var(--warm); color:var(--muted); font-size:12.5px; }}
.evidence-label {{ display:block; margin-bottom:3px; color:var(--ink); font-weight:700; }}
.featured-links {{ display:flex; align-items:center; gap:18px; margin-top:20px; flex-wrap:wrap; }}
.journey-panel {{ padding:20px; border:1px solid var(--line); border-radius:12px; background:var(--panel-soft); }}
.journey-label {{ color:var(--muted); font-size:11px; font-weight:700; letter-spacing:.1em; text-transform:uppercase; }}
.journey-panel ol {{ list-style:none; padding:0; margin:12px 0 0; counter-reset:journey; }}
.journey-panel li {{ position:relative; display:flex; align-items:center; gap:11px; padding:8px 0; color:var(--ink); font-size:13px; }}
.journey-panel li:not(:last-child)::after {{ position:absolute; left:11px; top:31px; width:1px; height:12px; background:var(--line); content:""; }}
.journey-panel li::before {{ display:grid; place-items:center; flex:0 0 23px; width:23px; height:23px; border:1px solid var(--line); border-radius:50%; color:var(--accent); font-size:10px; font-weight:700; counter-increment:journey; content:counter(journey); }}
.project-grid {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }}
.project-card {{ min-width:0; display:flex; flex-direction:column; padding:18px; border:1px solid var(--line); border-radius:12px; background:var(--panel); }}
.project-tags {{ display:flex; gap:6px; align-items:center; flex-wrap:wrap; }}
.tag {{ padding:3px 8px; border-radius:5px; background:var(--panel-soft); color:var(--muted); font-size:10.5px; }}
.tag--category {{ color:var(--accent); font-weight:700; }}
.project-card h3 {{ margin:12px 0 6px; font-size:16px; line-height:1.35; overflow-wrap:anywhere; }}
.project-card h3 a {{ text-decoration:none; }}
.project-card h3 a:hover {{ color:var(--accent); }}
.project-card p {{ flex:1; margin:0 0 16px; color:var(--muted); font-size:13px; line-height:1.55; }}
.project-links {{ display:flex; gap:16px; flex-wrap:wrap; padding-top:12px; border-top:1px solid var(--line); }}
.project-links a {{ color:var(--accent); font-size:11.5px; font-weight:700; text-decoration:none; }}
.project-links a:hover, .text-link:hover {{ text-decoration:underline; text-underline-offset:3px; }}
.archive {{ margin-top:50px; border-top:1px solid var(--line); }}
.archive details {{ border-bottom:1px solid var(--line); }}
.archive summary {{ display:flex; align-items:center; justify-content:space-between; gap:16px; padding:20px 2px; cursor:pointer; font-size:15px; font-weight:700; list-style:none; }}
.archive summary::-webkit-details-marker {{ display:none; }}
.archive summary::after {{ content:"＋"; color:var(--accent); font-size:18px; font-weight:400; }}
.archive details[open] summary::after {{ content:"−"; }}
.archive-note {{ margin:0 0 24px; color:var(--muted); font-size:13px; }}
.lab-section {{ margin:24px 0 34px; }}
.section-heading--compact {{ align-items:center; margin-bottom:14px; }}
.section-heading--compact h3 {{ margin:0; font-size:17px; }}
.archive details ul {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px 22px; list-style:none; padding:0; margin:0 0 24px; }}
.archive details li {{ display:flex; flex-direction:column; gap:3px; font-size:13px; }}
.archive details li a {{ width:fit-content; color:var(--ink); text-decoration:underline; text-decoration-color:var(--line); text-underline-offset:3px; }}
.archive details li span {{ color:var(--muted); font-size:11.5px; }}
footer {{ display:flex; justify-content:space-between; gap:16px; margin-top:42px; padding-top:20px; border-top:1px solid var(--line); color:var(--muted); font-size:12px; }}
footer a {{ color:var(--accent); text-decoration:none; }}
@media (max-width:800px) {{ .project-grid {{ grid-template-columns:repeat(2,minmax(0,1fr)); }} }}
@media (max-width:620px) {{
  .wrap {{ padding:20px 18px 52px; }} .hero {{ padding:50px 0 32px; }}
  .featured-grid {{ grid-template-columns:1fr; }} .featured-card--lead {{ grid-column:auto; grid-template-columns:1fr; gap:22px; padding:22px; }}
  .project-grid {{ grid-template-columns:1fr; }} .section-heading {{ align-items:flex-start; }}
  .archive details ul {{ grid-template-columns:1fr; }} footer {{ flex-direction:column; }}
}}
@media (prefers-reduced-motion:reduce) {{ html {{ scroll-behavior:auto; }} *,*::before,*::after {{ transition:none !important; }} }}
</style>
</head>
<body>
<a class="skip-link" href="#main">跳到主要內容</a>
<div class="wrap">
  <div class="topline"><span>Jerome Kuo · AI Product Portfolio</span><a href="https://github.com/jjfishjj" target="_blank" rel="noopener noreferrer">GitHub 個人頁 ↗</a></div>
  <header class="hero">
    <p class="eyebrow">產品策略 × AI 實作</p>
    <h1>從問題定義，到可體驗的產品。</h1>
    <p class="hero-copy">我把 AI、學習與服務流程轉成清楚、可操作的產品原型。先看幾個具體的使用者旅程；技術研究和其他實驗則整理在後面。</p>
    <div class="hero-bottom">
      <div class="hero-proof"><span><strong>{featured_count}</strong> 個精選產品原型</span><span><strong>{len(live)}</strong> 個線上作品</span></div>
      <nav class="hero-actions" aria-label="主要導覽"><a class="button button--primary" href="#featured">先看產品體驗 <span aria-hidden="true">↓</span></a><a class="text-link" href="#library">完整作品索引</a></nav>
    </div>
  </header>

  <main id="main">
    <section class="section" id="featured" aria-labelledby="featured-title">
      <div class="section-heading">
        <div><p class="eyebrow">FEATURED PRODUCT FLOWS</p><h2 id="featured-title">先看可操作的產品旅程</h2><p class="section-intro">這些是線上原型，不代表已商轉或經過正式成效驗證；每個案例都附上可見功能範圍，方便直接體驗。</p></div>
        <span class="count">{featured_count} 個精選</span>
      </div>
      <div class="featured-grid">{featured_html}</div>
    </section>

    {product_section}

    <section class="archive" id="library" aria-label="完整作品索引">
      <details>
        <summary><span>技術研究與工具</span><span class="count">{lab_count} 個線上專案</span></summary>
        <p class="archive-note">GPU、數位孿生、基礎工具與個人網站等探索作品保留在此，與產品案例分層呈現。</p>
        {lab_html}
      </details>
      <details>
        <summary><span>尚未部署 Pages 的公開 repo</span><span class="count">{len(offline)} 個</span></summary>
        <p class="archive-note">這些專案目前沒有公開的 GitHub Pages 體驗頁，連結會前往原始碼 repo。</p>
        <ul>{offline_rows}</ul>
      </details>
    </section>
  </main>

  <footer><span>最後更新：{built_date} · 由專案索引工具產生</span><span><a href="https://github.com/jjfishjj/claude-projects-hub">Hub 原始碼 ↗</a></span></footer>
</div>
</body>
</html>
"""

(ROOT / "index.html").write_text(HTML)
if missing_featured:
    print("Featured projects missing from live inventory: " + ", ".join(missing_featured))
print(f"index.html built: {featured_count} featured / {len(live)} live / {len(inventory)} public repos")
