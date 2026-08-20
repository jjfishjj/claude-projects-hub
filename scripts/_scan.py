"""讀 stdin 的 gh repo list JSON，查每個 repo 的 Pages 狀態，寫出 inventory.json"""
import json, subprocess, sys

user, out = sys.argv[1], sys.argv[2]
repos = json.load(sys.stdin)
result = []
for r in repos:
    if r["visibility"] != "PUBLIC":
        continue
    p = subprocess.run(["gh", "api", f"repos/{user}/{r['name']}/pages"],
                       capture_output=True, text=True)
    pages = json.loads(p.stdout).get("html_url") if p.returncode == 0 else None
    result.append({
        "name": r["name"],
        "description": r["description"] or "",
        "repo_url": r["url"],
        "pages_url": pages,
        "language": (r.get("primaryLanguage") or {}).get("name"),
        "pushed_at": r["pushedAt"][:10],
    })
result.sort(key=lambda x: (x["pages_url"] is None, x["name"].lower()))
json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
live = sum(1 for x in result if x["pages_url"])
print(f"{len(result)} public repos, {live} with Pages live -> {out}")
