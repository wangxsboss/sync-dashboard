# -*- coding: utf-8 -*-
"""生成同步看板 index.html —— 纸质台账风格，三标签（GitCode / GitHub / 服务器）"""
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
     "note": "本页面的源码镜像"},
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "platform": "github",
     "note": "海外第二份，防单点失效"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "github",
     "note": "本页面托管源（GitHub Pages）"},
]

SERVERS = [
    {
        "host": "服务器 A", "ip": "120.220.73.186", "spec": "2 核 2G · 29G",
        "sites": [
            {"name": "闲鱼管家", "raw": "闲鱼工作台", "func": "商品采集、上下架、改价，一站式操作面板",
             "url": "http://120.220.73.186:20789", "size": "177 MB", "tag": "运行中"},
            {"name": "账号切换台", "raw": "WorkBuddy 账号切换", "func": "六个 WorkBuddy 账号的快速切换",
             "url": "http://120.220.73.186:28095", "size": "44 KB", "tag": "运行中"},
            {"name": "模型接口站", "raw": "WorkBuddy2API", "func": "账号池包装成 OpenAI 兼容接口",
             "url": "http://120.220.73.186:28098", "size": "12 MB", "tag": "运行中"},
            {"name": "采集中心", "raw": "MediaCrawler", "func": "多平台内容批量采集抓取",
             "url": "http://120.220.73.186:28081", "size": "2.0 GB", "tag": "运行中"},
            {"name": "订单中枢", "raw": "xianyu-admin", "func": "订单、商品、任务调度的核心后台",
             "url": "http://120.220.73.186:3000", "size": "450 MB", "tag": "仅内网"},
            {"name": "网络文件柜", "raw": "OpenList", "func": "服务器文件在线浏览与下载",
             "url": "http://120.220.73.186:5244", "size": "150 MB", "tag": "仅内网"},
            {"name": "无头浏览器", "raw": "Chrome", "func": "自动化抓取用的浏览器环境",
             "url": "", "size": "446 MB", "tag": "后台"},
        ],
    },
    {
        "host": "服务器 B", "ip": "183.146.215.78", "spec": "1 核 1G · 40G",
        "sites": [
            {"name": "免费模型网关", "raw": "Our Free Model", "func": "免费大模型聚合、转发与用量统计",
             "url": "http://183.146.215.78:18901", "size": "69 MB", "tag": "运行中"},
            {"name": "自动下注器", "raw": "石头岛 bot", "func": "石头岛平台定时下注脚本",
             "url": "", "size": "2 MB", "tag": "仅内网"},
            {"name": "服务器控制台", "raw": "宝塔面板", "func": "站点、数据库、文件的可视化运维",
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
            return ("%d B" % n) if unit == "B" else ("%.1f|%s" % (n, unit))
        n /= 1024.0
    return "%.1f|TB" % n


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
    sz = human(dir_size(p))
    num, unit = (sz.split("|") + [""])[:2] if "|" in sz else (sz, "")
    return {
        "name": r["name"], "platform": r["platform"], "note": r["note"],
        "commits": git(p, ["rev-list", "--count", "HEAD"]) or "0",
        "count": len([x for x in git(p, ["ls-files"]).splitlines() if x]),
        "num": num, "unit": unit,
        "updated": git(p, ["log", "-1", "--format=%ad", "--date=format:%m-%d %H:%M"]) or "-",
    }


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def repo_row(d):
    unit = '<s>%s</s>' % d["unit"] if d["unit"] else ""
    return """
      <article class="row">
        <div class="lead">
          <h2>%s</h2>
          <p>%s</p>
        </div>
        <dl class="figs">
          <div><dt>提交</dt><dd>%s</dd></div>
          <div><dt>文件</dt><dd>%s</dd></div>
          <div><dt>体积</dt><dd>%s%s</dd></div>
          <div><dt>最后同步</dt><dd class="tm">%s</dd></div>
        </dl>
      </article>""" % (esc(d["name"]), esc(d["note"]), d["commits"], d["count"],
                       d["num"], unit, esc(d["updated"]))


def site_row(s):
    if s["url"]:
        link = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (s["url"], esc(s["url"]))
    else:
        link = '<span class="nil">仅内网</span>'
    cls = "warn" if s["tag"] in ("仅内网", "未启动") else ("idle" if s["tag"] == "后台" else "ok")
    return """
      <div class="site">
        <div class="s1"><b>%s</b><i class="%s">%s</i><em>%s</em></div>
        <div class="s2">%s</div>
        <div class="s3">%s</div>
        <div class="s4">%s</div>
      </div>""" % (esc(s["name"]), cls, esc(s["tag"]), esc(s["raw"]),
                   esc(s["func"]), link, esc(s["size"]))


def server_panel():
    out = []
    for sv in SERVERS:
        rows = "".join(site_row(s) for s in sv["sites"])
        out.append("""
      <section class="group">
        <div class="ghead">
          <h2>%s</h2>
          <code>%s</code>
          <span class="spec">%s</span>
          <span class="cnt">%d 个站点</span>
        </div>
        <div class="cols"><span>站点</span><span>功能</span><span>网址</span><span>占用</span></div>
        %s
      </section>""" % (esc(sv["host"]), esc(sv["ip"]), esc(sv["spec"]),
                        len(sv["sites"]), rows))
    return "\n".join(out)


def build(items):
    panels, counts = {}, {}
    for plat in ("gitcode", "github"):
        sub = [x for x in items if x["platform"] == plat]
        panels[plat] = "\n".join(repo_row(x) for x in sub)
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
<meta name="color-scheme" content="light">
<title>同步台账 · Sync Ledger</title>
<style>
  :root{
    --paper:#f6f3ec;
    --paper:#oklch(96.8% 0.008 85);
    --ink:#171614;
    --ink:#oklch(22% 0.008 80);
    --ink-2:#5a564d;
    --ink-3:#918b7e;
    --rule:#ddd6c8;
    --rule-soft:#eae4d8;
    --accent:#b23a1c;
    --accent:#oklch(50% 0.14 35);
    --ok:#1c6b4f;
    --warn:#9a6a12;

    --s1:4px; --s2:8px; --s3:12px; --s4:16px; --s5:24px; --s6:36px; --s7:56px;

    --sans:-apple-system,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
    --mono:ui-monospace,"Cascadia Mono",SFMono-Regular,Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  html{-webkit-text-size-adjust:100%;}
  body{
    background:var(--paper);
    color:var(--ink);
    font-family:var(--sans);
    font-size:14px;line-height:1.55;
    padding:clamp(20px,4vw,56px) clamp(16px,4vw,40px) 72px;
    -webkit-font-smoothing:antialiased;
    text-rendering:optimizeLegibility;
  }
  .page{max-width:940px;margin:0 auto;}

  /* ---------- 报头 ---------- */
  header{
    display:flex;align-items:flex-start;justify-content:space-between;
    gap:var(--s5);flex-wrap:wrap;
    padding-bottom:var(--s5);border-bottom:2px solid var(--ink);
  }
  .kicker{
    font-family:var(--mono);font-size:10.5px;letter-spacing:.22em;
    text-transform:uppercase;color:var(--accent);margin-bottom:var(--s2);
  }
  h1{
    font-size:clamp(26px,4vw,38px);font-weight:700;letter-spacing:-.02em;
    line-height:1.1;
  }
  .lede{color:var(--ink-2);font-size:13px;margin-top:var(--s2);max-width:46ch;}
  .stamp{
    text-align:right;font-family:var(--mono);font-size:11px;color:var(--ink-3);
    line-height:1.7;white-space:nowrap;
  }
  .stamp b{display:block;color:var(--ink);font-weight:600;font-size:12.5px;}

  /* ---------- 标签页 ---------- */
  .tabs{display:flex;gap:var(--s5);margin-top:var(--s5);border-bottom:1px solid var(--rule);}
  .tabs button{
    appearance:none;background:none;border:0;border-bottom:2px solid transparent;
    font-family:inherit;font-size:13px;font-weight:600;letter-spacing:.02em;
    color:var(--ink-3);padding:0 0 10px;margin-bottom:-1px;cursor:pointer;
    transition:color .18s cubic-bezier(.16,1,.3,1),border-color .18s cubic-bezier(.16,1,.3,1);
  }
  .tabs button:hover{color:var(--ink-2);}
  .tabs button.on{color:var(--ink);border-bottom-color:var(--accent);}
  .tabs button span{
    font-family:var(--mono);font-size:10.5px;font-weight:500;color:var(--ink-3);
    margin-left:5px;vertical-align:top;
  }

  /* ---------- 面板 ---------- */
  .panel{display:none;padding-top:var(--s2);}
  .panel.on{display:block;animation:fade .28s cubic-bezier(.16,1,.3,1) both;}
  @keyframes fade{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}

  /* ---------- 仓库行 ---------- */
  .row{
    display:flex;align-items:center;justify-content:space-between;gap:var(--s5);
    padding:var(--s4) 0;border-bottom:1px solid var(--rule-soft);flex-wrap:wrap;
  }
  .row:last-child{border-bottom:0;}
  .lead h2{font-size:16px;font-weight:650;letter-spacing:-.01em;}
  .lead p{font-size:12.5px;color:var(--ink-3);margin-top:2px;}
  .figs{display:flex;gap:clamp(18px,3vw,34px);}
  .figs div{text-align:right;}
  .figs dt{
    font-size:10px;letter-spacing:.11em;color:var(--ink-3);
    text-transform:uppercase;margin-bottom:1px;
  }
  .figs dd{
    font-family:var(--mono);font-size:16px;font-weight:600;
    font-variant-numeric:tabular-nums;letter-spacing:-.01em;
  }
  .figs dd s{text-decoration:none;font-size:11px;color:var(--ink-3);margin-left:3px;font-weight:500;}
  .figs dd.tm{font-size:12.5px;font-weight:500;color:var(--ink-2);}

  /* ---------- 服务器分组 ---------- */
  .group{margin-top:var(--s7);}
  .group:first-child{margin-top:var(--s5);}
  .ghead{
    display:flex;align-items:baseline;gap:var(--s3);flex-wrap:wrap;
    padding-bottom:var(--s2);border-bottom:1px solid var(--ink);
  }
  .ghead h2{font-size:15px;font-weight:700;letter-spacing:.02em;}
  .ghead code{
    font-family:var(--mono);font-size:12px;color:var(--ink-2);
    background:none;padding:0;
  }
  .ghead .spec{font-size:11.5px;color:var(--ink-3);}
  .ghead .cnt{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink-3);}

  .cols{
    display:grid;grid-template-columns:148px minmax(140px,1fr) 196px 62px;
    gap:var(--s4);padding:var(--s2) var(--s2) var(--s1);
    font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--ink-3);
  }
  .cols span:last-child{text-align:right;}

  .site{
    display:grid;grid-template-columns:148px minmax(140px,1fr) 196px 62px;
    gap:var(--s4);align-items:center;
    padding:11px var(--s2);border-bottom:1px solid var(--rule-soft);
    border-left:2px solid transparent;
    transition:background .18s cubic-bezier(.16,1,.3,1),border-color .18s cubic-bezier(.16,1,.3,1);
  }
  .site:hover{background:rgba(178,58,28,.035);border-left-color:var(--accent);}
  .site:last-child{border-bottom:0;}

  .s1{display:flex;flex-direction:column;gap:1px;min-width:0;}
  .s1 b{font-size:13.5px;font-weight:650;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .s1 i{
    font-style:normal;font-size:10px;letter-spacing:.06em;
    padding:0;line-height:1.5;
  }
  .s1 i.ok{color:var(--ok);}
  .s1 i.warn{color:var(--warn);}
  .s1 i.idle{color:var(--ink-3);}
  .s1 em{
    font-style:normal;font-size:10.5px;color:var(--ink-3);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
  }
  .s2{font-size:12.5px;color:var(--ink-2);min-width:0;}
  .s3{font-size:11.5px;min-width:0;word-break:break-all;}
  .s3 a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--rule);}
  .s3 a:hover{color:var(--accent);border-bottom-color:var(--accent);}
  .nil{color:var(--ink-3);font-style:italic;}
  .s4{
    font-family:var(--mono);font-size:12px;color:var(--ink-2);
    text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;
  }

  /* ---------- 页脚 ---------- */
  footer{
    display:flex;justify-content:space-between;gap:var(--s4);flex-wrap:wrap;
    margin-top:var(--s7);padding-top:var(--s3);border-top:1px solid var(--rule);
    font-size:11.5px;color:var(--ink-3);font-family:var(--mono);
  }

  @media (max-width:680px){
    header{gap:var(--s3);}
    .stamp{text-align:left;white-space:normal;}
    .tabs{gap:var(--s4);}
    .row{flex-direction:column;align-items:flex-start;gap:var(--s3);}
    .figs{width:100%;justify-content:space-between;gap:var(--s2);}
    .figs div{text-align:left;}
    .cols{display:none;}
    .site{grid-template-columns:1fr;gap:3px;padding:13px var(--s2);border-left:0;
          border-bottom:1px solid var(--rule);}
    .site:hover{border-left:0;}
    .s4{text-align:left;}
    .s1{flex-direction:row;align-items:baseline;gap:var(--s2);flex-wrap:wrap;}
    .s1 em{flex-basis:100%;}
  }
</style>
</head>
<body>
<div class="page">

  <header>
    <div>
      <div class="kicker">Sync Ledger</div>
      <h1>同步台账</h1>
      <p class="lede">对话归档、笔记镜像与两台服务器站点的运行记录。</p>
    </div>
    <div class="stamp">
      最近更新
      <b>%(NOW)s</b>
      每 60 分钟自动同步
    </div>
  </header>

  <nav class="tabs">
    <button id="tab-gitcode" class="on" onclick="sw('gitcode')">GitCode<span>%(N1)s</span></button>
    <button id="tab-github" onclick="sw('github')">GitHub<span>%(N2)s</span></button>
    <button id="tab-servers" onclick="sw('servers')">服务器<span>%(N3)s</span></button>
  </nav>

  <main>
    <section id="panel-gitcode" class="panel on">%(P1)s
    </section>
    <section id="panel-github" class="panel">%(P2)s
    </section>
    <section id="panel-servers" class="panel">%(P3)s
    </section>
  </main>

  <footer>
    <span>GitCode · GitHub 双写</span>
    <span>站点数据采集于 %(NOW)s</span>
  </footer>

</div>

<script>
var TABS = ['gitcode','github','servers'];
function sw(p){
  for (var i=0;i<TABS.length;i++){
    var k = TABS[i], on = (k === p);
    document.getElementById('panel-' + k).classList.toggle('on', on);
    document.getElementById('tab-' + k).classList.toggle('on', on);
  }
}
</script>
</body>
</html>
"""
    return (html.replace("%(NOW)s", now)
                .replace("%(P1)s", panels["gitcode"])
                .replace("%(P2)s", panels["github"])
                .replace("%(P3)s", server_panel())
                .replace("%(N1)s", str(counts["gitcode"]))
                .replace("%(N2)s", str(counts["github"]))
                .replace("%(N3)s", str(site_total)))


def main():
    items = [collect(r) for r in REPOS]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(build(items))
    print("已生成:", OUT)
    for d in items:
        print("  [%-7s] %-18s 提交%-3s 文件%-4s %s%s" %
              (PLAT_NAME[d["platform"]], d["name"], d["commits"], d["count"], d["num"], d["unit"]))
    for sv in SERVERS:
        print("  [%s] %s · %d 个站点" % (sv["host"], sv["ip"], len(sv["sites"])))


if __name__ == "__main__":
    main()
