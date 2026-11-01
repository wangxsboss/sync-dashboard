# -*- coding: utf-8 -*-
"""生成同步看板 index.html —— 紧凑面板风格（红 #cc3b23 / 灰白底 / 12px 字）
三标签：GitCode / GitHub / 服务器
"""
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
            {"name": "闲鱼管家", "func": "闲鱼买卖全流程操作面板，负责商品抓取、自动上下架、批量改价与订单同步",
             "url": "http://120.220.73.186:20789", "size": "177 MB", "tag": "运行中"},
            {"name": "账号切换台", "func": "六个 WorkBuddy 账号的快速切换入口，管理登录态与 Cookie 维护",
             "url": "http://120.220.73.186:28095", "size": "44 KB", "tag": "运行中"},
            {"name": "模型接口站", "func": "把 WorkBuddy 账号池包装成标准接口，负责账号调度、OpenAI 兼容转发与用量统计",
             "url": "http://120.220.73.186:28098", "size": "12 MB", "tag": "运行中"},
            {"name": "采集中心", "func": "多平台内容采集工具，负责关键词抓取、数据落库与结果导出",
             "url": "http://120.220.73.186:28081", "size": "2.0 GB", "tag": "运行中"},
            {"name": "订单中枢", "func": "整套业务的核心后台，负责订单处理、商品管理、任务调度与发货记录",
             "url": "http://120.220.73.186:3000", "size": "450 MB", "tag": "仅内网"},
            {"name": "网络文件柜", "func": "服务器文件的网盘式管理，支持在线浏览、下载与目录挂载",
             "url": "http://120.220.73.186:5244", "size": "150 MB", "tag": "仅内网"},
            {"name": "无头浏览器", "func": "自动化抓取的运行环境，负责登录鉴权、页面渲染与模拟点击",
             "url": "", "size": "446 MB", "tag": "后台"},
        ],
    },
    {
        "host": "服务器 B", "ip": "183.146.215.78", "spec": "1 核 1G · 40G",
        "sites": [
            {"name": "免费模型网关", "func": "免费大模型的统一出口，负责模型聚合、请求转发、签到保活与用量统计",
             "url": "http://183.146.215.78:18901", "size": "69 MB", "tag": "运行中"},
            {"name": "自动下注器", "func": "石头岛平台的自动化脚本，负责定时下注、策略触发、状态轮询与结果回写",
             "url": "http://183.146.215.78:49655/", "size": "2 MB", "tag": "运行中"},
            {"name": "服务器控制台", "func": "可视化运维入口（服务未启动），涵盖站点、数据库、文件与证书管理",
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
    unit = '<i>%s</i>' % d["unit"] if d["unit"] else ""
    return """
      <article class="row">
        <div class="lead">
          <b>%s</b>
          <span>%s</span>
        </div>
        <div class="figs">
          <div><em>提交</em><strong>%s</strong></div>
          <div><em>文件</em><strong>%s</strong></div>
          <div><em>体积</em><strong>%s%s</strong></div>
          <div><em>最后同步</em><strong class="tm">%s</strong></div>
        </div>
      </article>""" % (esc(d["name"]), esc(d["note"]), d["commits"], d["count"],
                       d["num"], unit, esc(d["updated"]))


def site_row(s, status=None):
    status = status or {}
    info = status.get(s["name"]) or {}
    if info.get("time"):
        st_txt = "更新 %s · 最近改动 %s" % (info["time"], info.get("file") or "—")
    else:
        st_txt = "未探测到更新记录"
    if s["url"]:
        link = '<a href="%s" target="_blank" rel="noopener">%s</a>' % (s["url"], esc(s["url"]))
    else:
        link = '<span class="nil">仅内网</span>'
    cls = {"运行中": "ok", "仅内网": "warn", "未启动": "warn", "后台": "idle"}.get(s["tag"], "idle")
    return """
        <div class="site">
          <div class="c1"><b>%s</b><span class="st %s">%s</span><em>%s</em></div>
          <div class="c2">%s</div>
          <div class="c3">%s</div>
          <div class="c4">%s</div>
        </div>""" % (esc(s["name"]), cls, esc(s["tag"]), st_txt,
                     esc(s["func"]), link, esc(s["size"]))


def server_panel(status=None):
    out = []
    for sv in SERVERS:
        rows = "".join(site_row(s, status) for s in sv["sites"])
        out.append("""
      <section class="group">
        <div class="ghead">
          <b>%s</b>
          <code>%s</code>
          <span class="spec">%s</span>
          <span class="cnt">%d 个站点</span>
        </div>
        <div class="cols"><span>站点</span><span>功能</span><span>网址</span><span>占用</span></div>
%s
      </section>""" % (esc(sv["host"]), esc(sv["ip"]), esc(sv["spec"]),
                        len(sv["sites"]), rows))
    return "\n".join(out)


def load_status():
    import json
    fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site-status.json")
    try:
        with open(fp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def build(items):
    STATUS = load_status()
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
<title>同步看板 · Sync Dashboard</title>
<style>
  :root{
    --bg:#ebedee;
    --panel:#ffffff;
    --panel-2:#fcfdfd;
    --line:#e3e7e9;
    --line-2:#d6dbde;
    --ink:#171b1e;
    --ink-2:#444c51;
    --ink-3:#7c858a;
    --red:#cc3b23;
    --red-d:#b9331d;
    --red-bg:#fdf0ec;
    --ok:#1a7f52;
    --warn:#a4670a;
    --sans:"PingFang SC","Microsoft YaHei",-apple-system,"Segoe UI",sans-serif;
    --mono:ui-monospace,"IBM Plex Mono",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{
    background:var(--bg);color:var(--ink);
    font-family:var(--sans);font-size:12.5px;line-height:1.55;
    padding:20px 16px 40px;-webkit-font-smoothing:antialiased;
  }
  .page{max-width:1000px;margin:0 auto;}

  /* 顶栏 */
  .top{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
       flex-wrap:wrap;margin-bottom:14px;}
  .top h1{font-size:16px;font-weight:600;letter-spacing:.2px;}
  .top h1 s{text-decoration:none;color:var(--red);margin-right:6px;}
  .top p{color:var(--ink-3);font-size:11.5px;margin-top:3px;}
  .stamp{font-family:var(--mono);font-size:11px;color:var(--ink-3);text-align:right;}
  .stamp b{color:var(--ink-2);font-weight:600;}

  /* 标签 */
  .tabs{display:inline-flex;background:#e1e5e7;border-radius:7px;padding:2px;gap:2px;margin-bottom:14px;}
  .tabs button{
    appearance:none;border:0;background:transparent;font-family:inherit;
    font-size:12px;font-weight:600;color:var(--ink-3);padding:5px 14px;border-radius:5px;
    cursor:pointer;transition:background .15s,color .15s;
  }
  .tabs button:hover{color:var(--ink-2);}
  .tabs button.on{background:#fff;color:var(--red);box-shadow:0 1px 2px rgba(23,27,30,.10);}
  .tabs button u{text-decoration:none;font-family:var(--mono);font-size:10.5px;
                 color:var(--ink-3);margin-left:4px;font-weight:500;}
  .tabs button.on u{color:var(--red);opacity:.75;}

  /* 面板 */
  .panel{display:none;}
  .panel.on{display:block;}

  /* 仓库行 */
  .rows{background:var(--panel);border:1px solid var(--line);border-radius:8px;overflow:hidden;}
  .row{display:flex;align-items:center;justify-content:space-between;gap:16px;
       padding:16px 14px;border-bottom:1px solid var(--line);flex-wrap:wrap;
       transition:background .15s;}
  .row:last-child{border-bottom:0;}
  .row:hover{background:var(--red-bg);}
  .lead b{font-size:13px;font-weight:600;display:block;}
  .lead span{font-size:11.5px;color:var(--ink-3);}
  .figs{display:flex;gap:22px;}
  .figs div{text-align:right;}
  .figs em{display:block;font-style:normal;font-size:10px;color:var(--ink-3);
           letter-spacing:.04em;margin-bottom:1px;}
  .figs strong{font-family:var(--mono);font-size:13.5px;font-weight:600;
               font-variant-numeric:tabular-nums;letter-spacing:-.02em;}
  .figs strong i{font-style:normal;font-size:10px;color:var(--ink-3);margin-left:2px;font-weight:500;}
  .figs strong.tm{font-size:11.5px;font-weight:500;color:var(--ink-2);}

  /* 服务器分组 */
  .group{background:var(--panel);border:1px solid var(--line);border-radius:8px;
         overflow:hidden;margin-bottom:12px;}
  .ghead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;
         padding:9px 14px;background:var(--panel-2);border-bottom:1px solid var(--line);}
  .ghead b{font-size:12.5px;font-weight:600;}
  .ghead code{font-family:var(--mono);font-size:11.5px;color:var(--ink-2);}
  .ghead .spec{font-size:11px;color:var(--ink-3);}
  .ghead .cnt{margin-left:auto;font-family:var(--mono);font-size:11px;color:var(--ink-3);}

  .cols{display:grid;grid-template-columns:158px minmax(150px,1fr) 210px 62px;
        gap:14px;padding:6px 14px 5px;font-size:10px;color:var(--ink-3);letter-spacing:.04em;
        border-bottom:1px solid var(--line);}
  .cols span:last-child{text-align:right;}

  .site{display:grid;grid-template-columns:158px minmax(150px,1fr) 210px 62px;
        gap:14px;align-items:center;padding:15px 14px;
        border-bottom:1px solid #f0f2f3;transition:background .15s;}
  .site:last-child{border-bottom:0;}
  .site:hover{background:var(--red-bg);}

  .c1{display:flex;align-items:center;gap:6px;flex-wrap:wrap;min-width:0;}
  .c1 b{font-size:13px;font-weight:600;white-space:nowrap;}
  .c1 em{font-style:normal;font-size:10.5px;color:var(--ink-3);flex-basis:100%;
         margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .c1 em{font-style:normal;font-size:10.5px;color:var(--ink-3);flex-basis:100%;
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .st{font-size:10px;font-weight:500;white-space:nowrap;}
  .st.ok{color:var(--ok);}
  .st.warn{color:var(--warn);}
  .st.idle{color:var(--ink-3);}
  .st::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;
              margin-right:4px;vertical-align:1px;background:currentColor;}

  .c2{font-size:12px;color:var(--ink-2);min-width:0;line-height:1.6;}
  .c3{font-size:11.5px;min-width:0;word-break:break-all;}
  .c3 a{color:var(--red-d);text-decoration:none;}
  .c3 a:hover{text-decoration:underline;}
  .nil{color:var(--ink-3);}
  .c4{font-family:var(--mono);font-size:11.5px;color:var(--ink-2);
      text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;}

  footer{margin-top:18px;display:flex;justify-content:space-between;gap:12px;
         flex-wrap:wrap;font-size:11px;color:var(--ink-3);font-family:var(--mono);}

  @media (max-width:700px){
    .row{flex-direction:column;align-items:flex-start;gap:8px;}
    .figs{width:100%;justify-content:space-between;gap:8px;}
    .figs div{text-align:left;}
    .cols{display:none;}
    .site{grid-template-columns:1fr;gap:4px;padding:10px 14px;}
    .c4{text-align:left;}
    .c1 em{flex-basis:auto;}
  }
</style>
</head>
<body>
<div class="page">

  <div class="top">
    <div>
      <h1><s>/</s>同步看板</h1>
      <p>对话归档 · 笔记镜像 · 服务器站点</p>
    </div>
    <div class="stamp">更新 <b>%(NOW)s</b> · 每 60 分钟自动同步</div>
  </div>

  <div class="tabs">
    <button id="tab-servers" class="on" onclick="sw('servers')">服务器<u>%(N3)s</u></button>
    <button id="tab-gitcode" onclick="sw('gitcode')">GitCode<u>%(N1)s</u></button>
    <button id="tab-github" onclick="sw('github')">GitHub<u>%(N2)s</u></button>
  </div>

  <main>
    <section id="panel-servers" class="panel on">%(P3)s
    </section>
    <section id="panel-gitcode" class="panel"><div class="rows">%(P1)s
    </div></section>
    <section id="panel-github" class="panel"><div class="rows">%(P2)s
    </div></section>
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
                .replace("%(P3)s", server_panel(STATUS))
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
