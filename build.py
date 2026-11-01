# -*- coding: utf-8 -*-
"""生成同步看板 index.html（仓库同步 + 服务器站点 三标签切换）"""
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

# 服务器站点清单（采集于 2026-11-01，路径 / 体积为实测值）
SERVERS = [
    {
        "host": "服务器 A",
        "ip": "120.220.73.186",
        "spec": "2核 2G · 29G 磁盘",
        "sites": [
            {"name": "闲鱼管家", "raw": "闲鱼工作台", "func": "商品采集、上下架、改价，一站式操作面板",
             "url": "http://120.220.73.186:20789", "size": "177 MB", "tag": "运行中"},
            {"name": "账号切换台", "raw": "WorkBuddy 账号切换", "func": "6 个 WorkBuddy 账号的快速切换面板",
             "url": "http://120.220.73.186:28095", "size": "44 KB", "tag": "运行中"},
            {"name": "模型接口站", "raw": "WorkBuddy2API 控制台", "func": "把 WorkBuddy 账号池包装成 OpenAI 兼容接口",
             "url": "http://120.220.73.186:28098", "size": "12 MB", "tag": "运行中"},
            {"name": "采集中心", "raw": "MediaCrawler", "func": "多平台内容批量采集抓取工具",
             "url": "http://120.220.73.186:28081", "size": "2.0 GB", "tag": "运行中"},
            {"name": "订单中枢", "raw": "xianyu-admin 主系统", "func": "订单、商品、任务调度一体的核心后台",
             "url": "http://120.220.73.186:3000", "size": "450 MB", "tag": "仅内网"},
            {"name": "网络文件柜", "raw": "OpenList", "func": "服务器文件在线浏览与下载",
             "url": "http://120.220.73.186:5244", "size": "150 MB", "tag": "仅内网"},
            {"name": "无头浏览器", "raw": "Chrome", "func": "自动化抓取用的浏览器运行环境",
             "url": "", "size": "446 MB", "tag": "后台"},
        ],
    },
    {
        "host": "服务器 B",
        "ip": "183.146.215.78",
        "spec": "1核 1G · 40G 磁盘",
        "sites": [
            {"name": "免费模型网关", "raw": "Our Free Model", "func": "免费大模型的聚合、转发与用量统计",
             "url": "http://183.146.215.78:18901", "size": "69 MB", "tag": "运行中"},
            {"name": "自动下注器", "raw": "石头岛 bot", "func": "石头岛平台定时自动下注脚本",
             "url": "", "size": "2 MB", "tag": "仅内网"},
            {"name": "服务器控制台", "raw": "宝塔面板", "func": "站点、数据库、文件的可视化运维面板",
             "url": "http://183.146.215.78:27976/5f6413e9", "size": "—", "tag": "未启动"},
        ],
    },
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


def repo_card(d):
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


def site_card(s):
    if s["url"]:
        url = '<a class="u" href="%s" target="_blank" rel="noopener">%s</a>' % (s["url"], esc(s["url"]))
    else:
        url = '<span class="u muted">仅内网，外网无法访问</span>'
    tag_cls = "warn" if s["tag"] in ("未启动", "仅内网") else "ok"
    return """
    <section class="site">
      <div class="c1">
        <span class="sname">%s</span>
        <span class="tag %s">%s</span>
        <span class="raw">%s</span>
      </div>
      <div class="c2 func">%s</div>
      <div class="c3 links">%s</div>
      <div class="c4 sz">%s</div>
    </section>""" % (esc(s["name"]), tag_cls, esc(s["tag"]), esc(s["raw"]),
                      esc(s["func"]), url, esc(s["size"]))


def server_panel():
    out = []
    for sv in SERVERS:
        cards = "\n".join(site_card(s) for s in sv["sites"])
        out.append("""
    <div class="svhead">
      <span class="svname">%s</span>
      <span class="svip">%s</span>
      <span class="svspec">%s</span>
      <span class="svcount">%d 个站点</span>
    </div>
    <div class="svcols"><span>站点</span><span>功能</span><span>网址</span><span class="r">占用</span></div>
    %s""" % (esc(sv["host"]), esc(sv["ip"]), esc(sv["spec"]), len(sv["sites"]), cards))
    return "\n".join(out)


def build(items):
    panels, counts = {}, {}
    for plat in ("gitcode", "github"):
        sub = [x for x in items if x["platform"] == plat]
        panels[plat] = "\n".join(repo_card(x) for x in sub)
        counts[plat] = len(sub)

    site_total = sum(len(sv["sites"]) for sv in SERVERS)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="noindex, nofollow, noarchive">
<meta name="googlebot" content="noindex, nofollow">
<title>同步看板 Sync Dashboard</title>
<style>
  :root{--bg:#f5f6f8;--card:#fff;--line:#e6e8ec;--ink:#1f2329;--ink2:#5c6672;
        --ink3:#8f97a3;--ok:#12b76a;--warn:#f79009;--link:#2f6bff;}
  *{box-sizing:border-box;margin:0;padding:0;}
  body{background:var(--bg);color:var(--ink);
       font-family:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
       font-size:14px;line-height:1.6;padding:24px 16px 48px;-webkit-font-smoothing:antialiased;}
  .wrap{max-width:880px;margin:0 auto;}
  header{display:flex;align-items:baseline;justify-content:space-between;gap:12px;
         flex-wrap:wrap;margin-bottom:16px;}
  h1{font-size:20px;font-weight:600;letter-spacing:.3px;}
  .sub{color:var(--ink2);font-size:13px;margin-top:2px;}
  .stamp{color:var(--ink3);font-size:12px;font-variant-numeric:tabular-nums;}

  .tabs{display:flex;background:#eceef2;border-radius:10px;padding:4px;margin-bottom:16px;gap:2px;}
  .tabs button{
    flex:1;border:0;background:transparent;color:var(--ink2);
    font-size:13.5px;font-weight:600;padding:9px 6px;border-radius:8px;
    cursor:pointer;transition:all .16s ease;font-family:inherit;white-space:nowrap;
  }
  .tabs button:hover{color:var(--ink);}
  .tabs button.on{background:#fff;color:var(--ink);box-shadow:0 1px 3px rgba(16,24,40,.10);}
  .tabs .n{font-weight:400;color:var(--ink3);font-size:11px;margin-left:4px;}

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

  .svhead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;
          margin:22px 4px 10px;padding-bottom:8px;border-bottom:1px solid var(--line);}
  .svhead:first-child{margin-top:0;}
  .svname{font-size:15px;font-weight:600;}
  .svip{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--ink2);}
  .svspec{font-size:12px;color:var(--ink3);}
  .svcount{margin-left:auto;font-size:12px;color:var(--ink3);}
  .svcols{display:grid;grid-template-columns:132px minmax(150px,1fr) minmax(170px,220px) 72px;
          gap:14px;padding:0 14px 6px;font-size:11px;color:var(--ink3);letter-spacing:.3px;}
  .svcols .r{text-align:right;}
  @media (max-width:640px){ .svcols{display:none;} }

  .site{display:grid;grid-template-columns:132px minmax(150px,1fr) minmax(170px,220px) 72px;
        gap:10px 14px;align-items:center;background:var(--card);border:1px solid var(--line);
        border-radius:9px;padding:11px 14px;margin-bottom:8px;transition:border-color .15s,box-shadow .15s;}
  .site:hover{border-color:#d5dae2;box-shadow:0 2px 8px rgba(16,24,40,.06);}
  .c1{display:flex;flex-direction:column;gap:2px;min-width:0;}
  .sname{font-weight:600;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .raw{font-size:11px;color:var(--ink3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .tag{align-self:flex-start;font-size:10.5px;padding:0 7px;border-radius:20px;border:1px solid;line-height:1.7;}
  .tag.ok{background:#ecfdf3;color:#067647;border-color:#d1fadf;}
  .tag.warn{background:#fffaeb;color:#b54708;border-color:#fedf89;}
  .c2.func{font-size:13px;color:var(--ink2);min-width:0;}
  .c3.links{font-size:12px;min-width:0;word-break:break-all;}
  .u{color:var(--link);text-decoration:none;}
  .u:hover{text-decoration:underline;}
  .muted{color:var(--ink3);}
  .c4.sz{font-size:12.5px;font-weight:600;color:var(--ink2);
         font-variant-numeric:tabular-nums;text-align:right;white-space:nowrap;}

  @media (max-width:640px){
    .site{grid-template-columns:1fr;gap:5px;padding:12px 14px;}
    .c4.sz{text-align:left;}
    .svcount{margin-left:0;}
  }

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
      <div class="sub">仓库同步 · 服务器站点</div>
    </div>
    <div class="stamp">更新于 {{NOW}}</div>
  </header>

  <div class="tabs">
    <button id="tab-gitcode" class="on" onclick="sw('gitcode')">GitCode<span class="n">{{N1}}</span></button>
    <button id="tab-github" onclick="sw('github')">GitHub<span class="n">{{N2}}</span></button>
    <button id="tab-servers" onclick="sw('servers')">服务器<span class="n">{{N3}}</span></button>
  </div>

  <div id="panel-gitcode" class="panel on">{{P1}}</div>
  <div id="panel-github" class="panel">{{P2}}</div>
  <div id="panel-servers" class="panel">{{P3}}</div>

  <footer>
    <span>自动同步：每小时执行一次</span>
    <span>站点数据采集于 {{NOW}}</span>
  </footer>
</div>

<script>
var TABS = ['gitcode','github','servers'];
function sw(p){
  TABS.forEach(function(k){
    var on = (k === p);
    document.getElementById('panel-' + k).classList.toggle('on', on);
    document.getElementById('tab-' + k).classList.toggle('on', on);
  });
}
</script>
</body>
</html>
"""
    return (html.replace("{{NOW}}", now)
                .replace("{{P1}}", panels["gitcode"])
                .replace("{{P2}}", panels["github"])
                .replace("{{P3}}", server_panel())
                .replace("{{N1}}", str(counts["gitcode"]))
                .replace("{{N2}}", str(counts["github"]))
                .replace("{{N3}}", str(site_total)))


def main():
    items = [collect(r) for r in REPOS]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(items))
    print("已生成:", OUT)
    for d in items:
        print("  [%-7s] %-18s 提交%-3s 文件%-4s %s" %
              (PLAT_NAME[d["platform"]], d["name"], d["commits"], d["count"], d["size"]))
    for sv in SERVERS:
        print("  [%s] %s · %d 个站点" % (sv["host"], sv["ip"], len(sv["sites"])))


if __name__ == "__main__":
    main()
