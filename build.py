# -*- coding: utf-8 -*-
"""生成同步看板 index.html 并推送"""
import os
import subprocess
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

REPOS = [
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "label": "GitCode",
     "note": "WorkBuddy 全部对话归档", "cls": ""},
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "label": "GitHub",
     "note": "同上，海外第二份", "cls": "gh"},
    {"path": r"D:\ObsidianMirror", "name": "obsidian-notes", "label": "GitCode",
     "note": "Obsidian 核心笔记镜像", "cls": ""},
]

OUT = r"D:\SyncDashboard\index.html"


def git(path, args):
    r = subprocess.run(["git"] + args, cwd=path, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "").strip()


def human(n):
    for unit in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return "%.1f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0
    return "%.1f TB" % n


def dir_size(p):
    total = 0
    for root, dirs, files in os.walk(p):
        dirs[:] = [d for d in dirs if d != ".git"]
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def collect(r):
    p = r["path"]
    commits = git(p, ["rev-list", "--count", "HEAD"]) or "0"
    files = [x for x in git(p, ["ls-files"]).splitlines() if x]
    last = git(p, ["log", "-1", "--format=%ad", "--date=format:%Y-%m-%d %H:%M"])
    return {
        "name": r["name"], "label": r["label"], "cls": r["cls"], "note": r["note"],
        "commits": commits, "count": len(files), "size": human(dir_size(p)),
        "updated": last or "—", "files": files,
    }


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(items):
    cards = []
    for d in items:
        rows = "\n".join(
            '        <li>%s</li>' % esc(f) for f in d["files"]
        ) or '        <li class="empty">（空仓库）</li>'
        cards.append("""
  <section class="card">
    <div class="row">
      <span class="dot ok"></span>
      <span class="name">%(name)s</span>
      <span class="plat %(cls)s">%(label)s</span>
    </div>
    <div class="meta">
      <div><div class="k">提交</div><div class="v">%(commits)s</div></div>
      <div><div class="k">文件</div><div class="v">%(count)s</div></div>
      <div><div class="k">体积</div><div class="v">%(size)s</div></div>
      <div><div class="k">最后同步</div><div class="v small">%(updated)s</div></div>
    </div>
    <div class="k note">%(note)s</div>
    <details>
      <summary>查看文件清单（%(count)s 个）</summary>
      <ul class="files">
%(rows)s
      </ul>
    </details>
  </section>""" % {
            "name": esc(d["name"]), "label": esc(d["label"]), "cls": d["cls"],
            "commits": d["commits"], "count": d["count"], "size": d["size"],
            "updated": esc(d["updated"]), "note": esc(d["note"]), "rows": rows,
        })

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>同步看板 · Sync Dashboard</title>
<style>
  :root{--bg:#f5f6f8;--card:#fff;--line:#e6e8ec;--ink:#1f2329;--ink2:#5c6672;--ink3:#8f97a3;--ok:#12b76a;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--ink);font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
       font-size:14px;line-height:1.6;padding:24px 16px 48px;-webkit-font-smoothing:antialiased;}
  .wrap{max-width:780px;margin:0 auto;}
  header{display:flex;align-items:baseline;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:20px;}
  h1{font-size:20px;font-weight:600;letter-spacing:.3px;}
  .sub{color:var(--ink2);font-size:13px;margin-top:2px;}
  .stamp{color:var(--ink3);font-size:12px;font-variant-numeric:tabular-nums;}
  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin-bottom:12px;}
  .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
  .name{font-weight:600;font-size:15px;}
  .plat{font-size:12px;padding:1px 8px;border-radius:20px;background:#eef2ff;color:#3b5bdb;border:1px solid #dbe3ff;}
  .plat.gh{background:#f3f4f6;color:#374151;border-color:#e5e7eb;}
  .dot{width:8px;height:8px;border-radius:50%;flex:none;background:var(--ok);box-shadow:0 0 0 3px rgba(18,183,106,.14);}
  .meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:12px;margin-top:14px;}
  .k{color:var(--ink3);font-size:12px;}
  .v{font-size:16px;font-weight:600;font-variant-numeric:tabular-nums;}
  .v.small{font-size:13px;font-weight:500;}
  .note{margin-top:10px;}
  details{margin-top:12px;border-top:1px dashed var(--line);padding-top:10px;}
  summary{cursor:pointer;color:var(--ink2);font-size:13px;user-select:none;outline:none;}
  summary:hover{color:var(--ink);}
  .files{margin-top:10px;max-height:280px;overflow:auto;list-style:none;
         font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;color:var(--ink2);}
  .files li{padding:3px 6px;border-radius:4px;word-break:break-all;}
  .files li:nth-child(odd){background:#fafbfc;}
  .files li.empty{color:var(--ink3);}
  footer{margin-top:20px;padding-top:16px;border-top:1px solid var(--line);color:var(--ink3);
         font-size:12px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>同步看板</h1>
      <div class="sub">GitCode · GitHub 仓库同步状态</div>
    </div>
    <div class="stamp">更新于 {{NOW}}</div>
  </header>
{{CARDS}}
  <footer>
    <span>自动同步：每小时执行一次</span>
    <span>共 {{TOTAL}} 个文件</span>
  </footer>
</div>
</body>
</html>
"""
    html = (html.replace("{{NOW}}", now)
                .replace("{{CARDS}}", "\n".join(cards))
                .replace("{{TOTAL}}", str(sum(d["count"] for d in items))))
    return html


def main():
    items = [collect(r) for r in REPOS]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(items))
    print("已生成:", OUT)
    for d in items:
        print("  %-20s %-8s 提交%s 文件%s %s" % (d["name"], d["label"], d["commits"], d["count"], d["size"]))


if __name__ == "__main__":
    main()
