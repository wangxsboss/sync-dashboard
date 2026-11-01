# -*- coding: utf-8 -*-
"""生成同步看板 index.html（GitCode / GitHub 双标签切换）"""
import os
import subprocess
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

REPOS = [
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "platform": "gitcode",
     "note": "WorkBuddy 全部对话归档"},
    {"path": r"D:\ObsidianMirror", "name": "obsidian-notes", "platform": "gitcode",
     "note": "Obsidian 核心笔记镜像"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "gitcode",
     "note": "本看板页面的镜像"},
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "platform": "github",
     "note": "同上，海外第二份"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "github",
     "note": "本看板页面（Pages 托管）"},
]

PLAT_NAME = {"gitcode": "GitCode", "github": "GitHub"}
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
    return {
        "name": r["name"], "platform": r["platform"], "note": r["note"],
        "commits": git(p, ["rev-list", "--count", "HEAD"]) or "0",
        "count": len([x for x in git(p, ["ls-files"]).splitlines() if x]),
        "size": human(dir_size(p)),
        "updated": git(p, ["log", "-1", "--format=%ad", "--date=format:%Y-%m-%d %H:%M"]) or "-",
    }


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def card(d):
    return """
    <section class="card">
      <div class="row">
        <span class="dot ok"></span>
        <span class="name">%s</span>
      </div>
      <div class="meta">
        <div><div class="k">提交</div><div class="v">%s</div></div>
        <div><div class="k">文件</div><div class="v">%s</div></div>
        <div><div class="k">体积</div><div class="v">%s</div></div>
        <div><div class="k">最后同步</div><div class="v small">%s</div></div>
      </div>
      <div class="k note">%s</div>
    </section>""" % (esc(d["name"]), d["commits"], d["count"], d["size"],
                      esc(d["updated"]), esc(d["note"]))


def build(items):
    panels, counts = {}, {}
    for plat in ("gitcode", "github"):
        sub = [x for x in items if x["platform"] == plat]
        panels[plat] = "\n".join(card(x) for x in sub)
        counts[plat] = len(sub)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>同步看板 Sync Dashboard</title>
<style>
  :root{--bg:#f5f6f8;--card:#fff;--line:#e6e8ec;--ink:#1f2329;--ink2:#5c6672;
        --ink3:#8f97a3;--ok:#12b76a;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--ink);
       font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
       font-size:14px;line-height:1.6;padding:24px 16px 48px;-webkit-font-smoothing:antialiased;}
  .wrap{max-width:780px;margin:0 auto;}
  header{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
         flex-wrap:wrap;margin-bottom:16px;}
  h1{font-size:20px;font-weight:600;letter-spacing:.3px;}
  .sub{color:var(--ink2);font-size:13px;margin-top:2px;}
  .stamp{color:var(--ink3);font-size:12px;font-variant-numeric:tabular-nums;}

  .tabs{display:flex;background:#eceef2;border-radius:10px;padding:4px;margin-bottom:16px;}
  .tabs button{
    flex:1;border:0;background:transparent;color:var(--ink2);
    font-size:14px;font-weight:600;padding:9px 12px;border-radius:8px;
    cursor:pointer;transition:all .16s ease;font-family:inherit;
  }
  .tabs button:hover{color:var(--ink);}
  .tabs button.on{background:#fff;color:var(--ink);box-shadow:0 1px 3px rgba(16,24,40,.10);}
  .tabs .n{font-weight:400;color:var(--ink3);font-size:12px;margin-left:5px;}

  .panel{display:none;}
  .panel.on{display:block;}

  .card{background:var(--card);border:1px solid var(--line);border-radius:10px;
        padding:16px 18px;margin-bottom:12px;}
  .row{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
  .name{font-weight:600;font-size:15px;}
  .dot{width:8px;height:8px;border-radius:50%;flex:none;background:var(--ok);
       box-shadow:0 0 0 3px rgba(18,183,106,.14);}
  .meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));
        gap:12px;margin-top:14px;}
  .k{color:var(--ink3);font-size:12px;}
  .v{font-size:16px;font-weight:600;font-variant-numeric:tabular-nums;}
  .v.small{font-size:13px;font-weight:500;}
  .note{margin-top:10px;}

  footer{margin-top:20px;padding-top:16px;border-top:1px solid var(--line);
         color:var(--ink3);font-size:12px;display:flex;justify-content:space-between;
         gap:12px;flex-wrap:wrap;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>同步看板</h1>
      <div class="sub">仓库同步状态</div>
    </div>
    <div class="stamp">更新于 {{NOW}}</div>
  </header>

  <div class="tabs">
    <button id="tab-gitcode" class="on" onclick="sw('gitcode')">GitCode<span class="n">{{N1}}</span></button>
    <button id="tab-github" onclick="sw('github')">GitHub<span class="n">{{N2}}</span></button>
  </div>

  <div id="panel-gitcode" class="panel on">{{P1}}</div>
  <div id="panel-github" class="panel">{{P2}}</div>

  <footer>
    <span>自动同步：每小时执行一次</span>
    <span>全部正常</span>
  </footer>
</div>

<script>
function sw(p){
  var a = p === 'gitcode';
  document.getElementById('panel-gitcode').classList.toggle('on', a);
  document.getElementById('panel-github').classList.toggle('on', !a);
  document.getElementById('tab-gitcode').classList.toggle('on', a);
  document.getElementById('tab-github').classList.toggle('on', !a);
}
</script>
</body>
</html>
"""
    return (html.replace("{{NOW}}", now)
                .replace("{{P1}}", panels["gitcode"])
                .replace("{{P2}}", panels["github"])
                .replace("{{N1}}", str(counts["gitcode"]))
                .replace("{{N2}}", str(counts["github"])))


def main():
    items = [collect(r) for r in REPOS]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(items))
    print("已生成:", OUT)
    for d in items:
        print("  [%-7s] %-18s 提交%-3s 文件%-4s %s" %
              (PLAT_NAME[d["platform"]], d["name"], d["commits"], d["count"], d["size"]))


if __name__ == "__main__":
    main()
