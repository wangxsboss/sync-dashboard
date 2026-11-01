# -*- coding: utf-8 -*-
"""生成同步看板 index.html —— 卡片流风格（白卡 / 浅灰底 / 蓝色药丸标签 / 右侧圆角按钮）
三标签：服务器 / GitCode / GitHub
"""
import os
import subprocess
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

REPOS = [
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "platform": "gitcode",
     "note": "WorkBuddy 全部对话归档", "repo": "https://gitcode.com/chaoshen59/workbuddy-archive"},
    {"path": r"D:\ObsidianMirror", "name": "obsidian-notes", "platform": "gitcode",
     "note": "Obsidian 核心笔记镜像", "repo": "https://gitcode.com/chaoshen59/obsidian-notes"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "gitcode",
     "note": "本页面的源码镜像", "repo": "https://gitcode.com/chaoshen59/sync-dashboard"},
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "platform": "github",
     "note": "海外第二份，防单点失效", "repo": "https://github.com/wangxsboss/workbuddy-archive"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "github",
     "note": "本页面托管源（GitHub Pages）", "repo": "https://github.com/wangxsboss/sync-dashboard"},
]

SERVERS = [
    {
        "host": "服务器 A", "ip": "120.220.73.186", "spec": "2 核 2G · 29G",
        "sites": [
            {"name": "闲鱼管家", "tags": "商品抓取 | 自动上下架 | 批量改价 | 订单同步",
             "url": "http://120.220.73.186:20789", "size": "177 MB", "tag": "运行中"},
            {"name": "账号切换台", "tags": "多账号切换 | 登录态管理 | Cookie 维护",
             "url": "http://120.220.73.186:28095", "size": "44 KB", "tag": "运行中"},
            {"name": "模型接口站", "tags": "账号池调度 | OpenAI 兼容转发 | 用量统计",
             "url": "http://120.220.73.186:28098", "size": "12 MB", "tag": "运行中"},
            {"name": "采集中心", "tags": "多平台抓取 | 关键词采集 | 数据落库 | 结果导出",
             "url": "http://120.220.73.186:28081", "size": "2.0 GB", "tag": "运行中"},
            {"name": "订单中枢", "tags": "订单处理 | 商品管理 | 任务调度 | 发货记录",
             "url": "http://120.220.73.186:3000", "size": "450 MB", "tag": "仅内网"},
            {"name": "网络文件柜", "tags": "文件浏览 | 在线下载 | 目录挂载",
             "url": "http://120.220.73.186:5244", "size": "150 MB", "tag": "仅内网"},
            {"name": "无头浏览器", "tags": "登录鉴权 | 页面渲染 | 自动化点击",
             "url": "", "size": "446 MB", "tag": "后台"},
        ],
    },
    {
        "host": "服务器 B", "ip": "183.146.215.78", "spec": "1 核 1G · 40G",
        "sites": [
            {"name": "免费模型网关", "tags": "模型聚合 | 请求转发 | 签到保活 | 用量统计",
             "url": "http://183.146.215.78:18901", "size": "69 MB", "tag": "运行中"},
            {"name": "自动下注器", "tags": "定时下注 | 策略触发 | 状态轮询 | 结果回写",
             "url": "http://183.146.215.78:49655/", "size": "2 MB", "tag": "运行中"},
            {"name": "服务器控制台", "tags": "站点管理 | 数据库 | 文件传输 | 证书签发",
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
        "repo": r.get("repo", ""),
        "commits": git(p, ["rev-list", "--count", "HEAD"]) or "0",
        "count": len([x for x in git(p, ["ls-files"]).splitlines() if x]),
        "num": num, "unit": unit,
        "updated": git(p, ["log", "-1", "--format=%ad", "--date=format:%m-%d %H:%M"]) or "-",
    }


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def btn(url, label="打开"):
    if url:
        return '<a class="btn" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(url), label)
    return '<span class="btn off">仅内网</span>'


def repo_card(d):
    unit = '<i>%s</i>' % d["unit"] if d["unit"] else ""
    return """
      <article class="card">
        <div class="left">
          <div class="hd">
            <h3>%s</h3>
            <span class="pill blue">%s</span>
          </div>
          <p class="desc">%s</p>
          <p class="meta">提交 %s | 文件 %s | 体积 %s%s | 最后同步 %s</p>
        </div>
        %s
      </article>""" % (esc(d["name"]), PLAT_NAME[d["platform"]], esc(d["note"]),
                       d["commits"], d["count"], d["num"], unit, esc(d["updated"]),
                       btn(d["repo"], "查看"))


def site_card(s, status=None):
    status = status or {}
    info = status.get(s["name"]) or {}
    if info.get("time"):
        meta = "更新 %s | 最近改动 %s | 占用 %s" % (info["time"], info.get("file") or "—", s["size"])
    else:
        meta = "未探测到更新记录 | 占用 %s" % s["size"]
    cls = {"运行中": "green", "仅内网": "orange", "未启动": "orange", "后台": "gray"}.get(s["tag"], "gray")
    return """
      <article class="card">
        <div class="left">
          <div class="hd">
            <h3>%s</h3>
            <span class="pill %s">%s</span>
          </div>
          <p class="desc">%s</p>
          <p class="meta">%s</p>
        </div>
        %s
      </article>""" % (esc(s["name"]), cls, esc(s["tag"]), esc(s["tags"]), meta, btn(s["url"]))


def server_panel(status=None):
    out = []
    for sv in SERVERS:
        cards = "".join(site_card(s, status) for s in sv["sites"])
        out.append("""
      <section class="block">
        <div class="ghead">
          <h2>%s</h2>
          <code>%s</code>
          <span class="spec">%s</span>
          <span class="cnt">%d 个站点</span>
        </div>
        %s
      </section>""" % (esc(sv["host"]), esc(sv["ip"]), esc(sv["spec"]), len(sv["sites"]), cards))
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
<meta name="color-scheme" content="light">
<title>同步看板 · Sync Dashboard</title>
<style>
  :root{
    --bg:#f7f8fa;
    --card:#ffffff;
    --line:#ebedf0;
    --ink:#1f2329;
    --ink-2:#5a6472;
    --ink-3:#8a919f;
    --ink-4:#a8afb8;
    --blue:#1c6eff;
    --blue-bg:#e8f1ff;
    --green:#0e9f6e;
    --green-bg:#e8f7f0;
    --orange:#d97706;
    --orange-bg:#fff4e6;
    --gray-bg:#f1f3f5;
    --sans:"PingFang SC","Microsoft YaHei",-apple-system,"Segoe UI",sans-serif;
    --mono:ui-monospace,"IBM Plex Mono",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{
    background:var(--bg);color:var(--ink);
    font-family:var(--sans);font-size:14px;line-height:1.6;
    padding:28px 18px 56px;-webkit-font-smoothing:antialiased;
  }
  .page{max-width:960px;margin:0 auto;}

  /* 顶栏 */
  .top{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;
       flex-wrap:wrap;margin-bottom:20px;padding:0 4px;}
  .top h1{font-size:22px;font-weight:600;letter-spacing:.2px;}
  .top h1 s{text-decoration:none;color:var(--blue);margin-right:6px;}
  .top p{color:var(--ink-3);font-size:13px;margin-top:4px;}
  .stamp{font-family:var(--mono);font-size:11.5px;color:var(--ink-3);text-align:right;line-height:1.7;}
  .stamp b{color:var(--ink-2);font-weight:600;}

  /* 标签 */
  .tabs{display:inline-flex;background:#eef1f5;border-radius:12px;padding:4px;gap:4px;margin-bottom:22px;}
  .tabs button{
    appearance:none;border:0;background:transparent;font-family:inherit;
    font-size:13px;font-weight:500;color:var(--ink-3);padding:7px 18px;border-radius:9px;
    cursor:pointer;transition:background .15s,color .15s;
  }
  .tabs button:hover{color:var(--ink-2);}
  .tabs button.on{background:#fff;color:var(--blue);font-weight:600;box-shadow:0 1px 3px rgba(31,35,41,.08);}
  .tabs button u{text-decoration:none;font-family:var(--mono);font-size:11px;
                 color:var(--ink-4);margin-left:6px;font-weight:500;}
  .tabs button.on u{color:var(--blue);opacity:.85;}

  /* 面板 */
  .panel{display:none;}
  .panel.on{display:block;}

  /* 分组标题 */
  .block{margin-bottom:26px;}
  .block:last-child{margin-bottom:0;}
  .ghead{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;padding:0 6px;margin-bottom:12px;}
  .ghead h2{font-size:15px;font-weight:600;}
  .ghead code{font-family:var(--mono);font-size:12.5px;color:var(--ink-2);}
  .ghead .spec{font-size:12px;color:var(--ink-3);}
  .ghead .cnt{margin-left:auto;font-family:var(--mono);font-size:11.5px;color:var(--ink-4);}

  /* 卡片 */
  .card{
    display:flex;align-items:center;gap:20px;
    background:var(--card);border:1px solid var(--line);border-radius:16px;
    padding:20px 22px;margin-bottom:14px;
    transition:border-color .15s,box-shadow .15s,transform .15s;
  }
  .card:last-child{margin-bottom:0;}
  .card:hover{border-color:#dde2ea;box-shadow:0 4px 16px rgba(31,35,41,.06);}
  .left{flex:1;min-width:0;}

  .hd{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
  .hd h3{font-size:16px;font-weight:600;letter-spacing:.1px;}

  .pill{font-size:11.5px;font-weight:500;padding:2px 10px;border-radius:999px;white-space:nowrap;}
  .pill.blue{color:var(--blue);background:var(--blue-bg);}
  .pill.green{color:var(--green);background:var(--green-bg);}
  .pill.orange{color:var(--orange);background:var(--orange-bg);}
  .pill.gray{color:var(--ink-3);background:var(--gray-bg);}
  .pill::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;
                background:currentColor;margin-right:5px;vertical-align:1.5px;opacity:.9;}

  .desc{margin-top:9px;font-size:13.5px;color:var(--ink-3);line-height:1.65;}
  .meta{margin-top:7px;font-size:12px;color:var(--ink-4);font-family:var(--mono);
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .meta i{font-style:normal;font-size:10.5px;margin-left:2px;}

  .btn{
    flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;
    min-width:84px;height:38px;padding:0 20px;border-radius:11px;
    background:var(--blue-bg);color:var(--blue);font-size:13.5px;font-weight:500;
    text-decoration:none;transition:background .15s,color .15s;
  }
  .btn:hover{background:var(--blue);color:#fff;}
  .btn.off{background:var(--gray-bg);color:var(--ink-4);cursor:default;}
  .btn.off:hover{background:var(--gray-bg);color:var(--ink-4);}

  footer{margin-top:26px;padding:0 6px;display:flex;justify-content:space-between;gap:12px;
         flex-wrap:wrap;font-size:11.5px;color:var(--ink-4);font-family:var(--mono);}

  @media (max-width:700px){
    body{padding:20px 12px 40px;}
    .card{flex-direction:column;align-items:stretch;gap:14px;padding:18px;border-radius:14px;}
    .btn{width:100%;height:40px;}
    .meta{white-space:normal;}
    .top h1{font-size:19px;}
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
    <div class="stamp">更新 <b>%(NOW)s</b><br>每 10 分钟自动刷新</div>
  </div>

  <div class="tabs">
    <button id="tab-servers" class="on" onclick="sw('servers')">服务器<u>%(N3)s</u></button>
    <button id="tab-gitcode" onclick="sw('gitcode')">GitCode<u>%(N1)s</u></button>
    <button id="tab-github" onclick="sw('github')">GitHub<u>%(N2)s</u></button>
  </div>

  <main>
    <section id="panel-servers" class="panel on">%(P3)s
    </section>
    <section id="panel-gitcode" class="panel">
%(P1)s
    </section>
    <section id="panel-github" class="panel">
%(P2)s
    </section>
  </main>

  <footer>
    <span>GitCode · GitHub 双写</span>
    <span>数据采集于 %(NOW)s</span>
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
  try { history.replaceState(null, '', '#' + p); } catch(e) {}
}
(function(){
  var h = (location.hash || '').replace('#','');
  if (TABS.indexOf(h) >= 0) sw(h);
  // 每 5 分钟自动重载并绕开缓存，保证数据始终是最新的
  var RELOAD = 5 * 60 * 1000;
  setTimeout(function(){
    var u = location.pathname + '?v=' + Date.now() + (location.hash || '');
    location.replace(u);
  }, RELOAD);
})();
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
