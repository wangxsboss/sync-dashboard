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
     "title": "对话归档",
     "note": "WorkBuddy 全部历史对话", "group": "other", "repo": "https://gitcode.com/chaoshen59/workbuddy-archiveworkbuddy-archive"},
    {"path": r"D:\ObsidianMirror", "name": "obsidian-notes", "platform": "gitcode",
     "title": "笔记镜像",
     "note": "Obsidian 核心笔记备份", "group": "other", "repo": "https://gitcode.com/chaoshen59/obsidian-notes"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "gitcode",
     "title": "看板源码",
     "note": "本页面自身的源码", "group": "other", "repo": "https://gitcode.com/chaoshen59/sync-dashboard"},
    {"path": r"D:\ServerMirror\server-a-code", "name": "server-a-code", "platform": "gitcode",
     "title": "A 机整体备份",
     "note": "旧版：服务器 A 全部站点打包", "group": "other",
     "repo": "https://gitcode.com/chaoshen59/server-a-code"},
    {"path": r"D:\ServerMirror\server-b-code", "name": "server-b-code", "platform": "gitcode",
     "title": "B 机整体备份",
     "note": "旧版：服务器 B 全部站点打包", "group": "other",
     "repo": "https://gitcode.com/chaoshen59/server-b-code"},
    {"path": r"D:\Repos\server-deploy", "name": "server-deploy", "platform": "gitcode",
     "title": "一键部署总控",
     "note": "一条命令拉起全部 8 个站点", "group": "other",
     "repo": "https://gitcode.com/chaoshen59/server-deploy"},
    {"path": r"D:\Repos\xianyu-system", "name": "xianyu-system", "platform": "gitcode",
     "title": "闲鱼自动回复系统",
     "note": "订单中枢 + 闲鱼管家 · 73 张表数据库",
     "repo": "https://gitcode.com/chaoshen59/xianyu-system"},
    {"path": r"D:\Repos\mediacrawler", "name": "mediacrawler", "platform": "gitcode",
     "title": "采集中心",
     "note": "多平台内容采集 + WebUI",
     "repo": "https://gitcode.com/chaoshen59/mediacrawler"},
    {"path": r"D:\Repos\wb2api", "name": "wb2api", "platform": "gitcode",
     "title": "模型接口站",
     "note": "账号池调度 + OpenAI 兼容网关",
     "repo": "https://gitcode.com/chaoshen59/wb2api"},
    {"path": r"D:\Repos\openlist", "name": "openlist", "platform": "gitcode",
     "title": "网络文件柜",
     "note": "配置 + SQLite 数据",
     "repo": "https://gitcode.com/chaoshen59/openlist"},
    {"path": r"D:\Repos\wb-switch", "name": "wb-switch", "platform": "gitcode",
     "title": "账号切换台",
     "note": "多账号切换 WebUI",
     "repo": "https://gitcode.com/chaoshen59/wb-switch"},
    {"path": r"D:\Repos\dsh-our-free-model", "name": "dsh-our-free-model", "platform": "gitcode",
     "title": "免费模型网关",
     "note": "模型聚合与请求转发",
     "repo": "https://gitcode.com/chaoshen59/dsh-our-free-model"},
    {"path": r"D:\Repos\shitou-bot", "name": "shitou-bot", "platform": "gitcode",
     "title": "自动下注器",
     "note": "石头岛下注脚本 · 无网页", "group": "other",
     "repo": "https://gitcode.com/chaoshen59/shitou-bot"},
    {"path": r"D:\Repos\odds", "name": "odds", "platform": "gitcode",
     "title": "赔率统计",
     "note": "文件误删后从进程内存完整还原", "group": "other",
     "repo": "https://gitcode.com/chaoshen59/odds"},
    {"path": r"D:\WorkBuddyArchive", "name": "workbuddy-archive", "platform": "github",
     "title": "对话归档",
     "note": "WorkBuddy 全部历史对话", "group": "other", "repo": "https://github.com/wangxsboss/workbuddy-archive"},
    {"path": r"D:\ObsidianMirror", "name": "obsidian-notes", "platform": "github",
     "title": "笔记镜像",
     "note": "Obsidian 核心笔记备份", "group": "other", "live": False, "repo": "https://github.com/wangxsboss/obsidian-notes"},
    {"path": r"D:\SyncDashboard", "name": "sync-dashboard", "platform": "github",
     "title": "看板源码",
     "note": "本页面自身的源码", "group": "other", "repo": "https://github.com/wangxsboss/sync-dashboard"},
    {"path": r"D:\ServerMirror\server-a-code", "name": "server-a-code", "platform": "github",
     "title": "A 机整体备份",
     "note": "旧版：服务器 A 全部站点打包", "group": "other", "live": False,
     "repo": "https://github.com/wangxsboss/server-a-code"},
    {"path": r"D:\ServerMirror\server-b-code", "name": "server-b-code", "platform": "github",
     "title": "B 机整体备份",
     "note": "旧版：服务器 B 全部站点打包", "group": "other", "live": False,
     "repo": "https://github.com/wangxsboss/server-b-code"},
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
             "url": "http://183.146.215.78:27976/5f6413e9", "size": "—", "tag": "打不开"},
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
        "repo": r.get("repo", ""), "live": r.get("live", True),
        "group": r.get("group", "site"), "title": r.get("title", r["name"]),
        "commits": git(p, ["rev-list", "--count", "HEAD"]) or "0",
        "count": len([x for x in git(p, ["ls-files"]).splitlines() if x]),
        "num": num, "unit": unit,
        "updated": git(p, ["log", "-1", "--format=%ad", "--date=format:%m-%d %H:%M"]) or "-",
    }


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def btn(url, label="打开", note="", enabled=True):
    if url and enabled:
        a = '<a class="btn" href="%s" target="_blank" rel="noopener">%s</a>' % (esc(url), label)
    elif url:
        a = '<span class="btn off">%s</span>' % note
    else:
        a = '<span class="btn off">%s</span>' % (note or "仅内网")
    u = '<span class="url">%s</span>' % esc(url) if url else ""
    return '<div class="act">%s%s</div>' % (a, u)


def repo_card(d):
    unit = '<i>%s</i>' % d["unit"] if d["unit"] else ""
    live = d.get("live", True)
    if live:
        pill = '<span class="pill blue">%s</span>' % PLAT_NAME[d["platform"]]
        act = btn(d["repo"], "打开仓库")
    else:
        pill = ('<span class="pill gray">%s</span>'
                '<span class="pill orange">未推送</span>') % PLAT_NAME[d["platform"]]
        act = ('<div class="act"><span class="btn off">待补推</span>'
               '<span class="url">%s</span></div>') % esc(d["repo"])
    if live:
        meta = "提交 %s | 文件 %s | 体积 %s%s | 最后同步 %s" % (
            d["commits"], d["count"], d["num"], unit, esc(d["updated"]))
    else:
        meta = "本地副本就绪 · 提交 %s | 文件 %s | 体积 %s%s" % (
            d["commits"], d["count"], d["num"], unit)
    return """
      <article class="card">
        <div class="left">
          <div class="hd">
            <h3>%s</h3>
            %s
          </div>
          <p class="desc"><b class="rn">%s</b> · %s</p>
          <p class="meta">%s</p>
        </div>
        %s
      </article>""" % (esc(d["title"]), pill, esc(d["name"]), esc(d["note"]), meta, act)


def addr(u):
    """从网址里取出纯 IP:端口，去掉 http:// 和后面的路径"""
    if not u:
        return ""
    a = u.replace("https://", "").replace("http://", "").strip()
    return a.split("/")[0]


def site_card(s, status=None):
    status = status or {}
    info = status.get(s["name"]) or {}
    ip_port = addr(s["url"]) or "仅内网"
    if info.get("time"):
        meta = "更新 %s | %s | 占用 %s" % (info["time"], ip_port, s["size"])
    else:
        meta = "未探测到更新记录 | %s | 占用 %s" % (ip_port, s["size"])
    cls = {"运行中": "green", "仅内网": "orange", "打不开": "red", "未启动": "orange", "后台": "gray"}.get(s["tag"], "gray")
    if s["tag"] == "运行中":
        act = btn(s["url"], "打开")
    elif not s["url"]:
        act = btn("", note="仅内网")
    else:
        act = btn(s["url"], note=s["tag"], enabled=False)
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
      </article>""" % (esc(s["name"]), cls, esc(s["tag"]), esc(s["tags"]), meta, act)


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


GROUPS = [
    ("site", "网站", "有网页访问入口的站点"),
    ("other", "其他", "后台脚本 · 总控工具 · 备份仓库"),
]


def group_block(title, hint, cards):
    return """
      <section class="block">
        <div class="ghead">
          <h2>%s</h2>
          <span class="spec">%s</span>
          <span class="cnt">%d 个</span>
        </div>
        %s
      </section>""" % (esc(title), esc(hint), len(cards), "".join(cards))


def render_grouped(sub):
    out = []
    for key, title, hint in GROUPS:
        grp = [x for x in sub if x.get("group", "site") == key]
        if grp:
            out.append(group_block(title, hint, [repo_card(x) for x in grp]))
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
        panels[plat] = render_grouped(sub)
        counts[plat] = len(sub)

    site_total = sum(len(sv["sites"]) for sv in SERVERS)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    g_all = [x for x in items if x["platform"] == "github"]
    g_live = [x for x in g_all if x.get("live", True)]
    if len(g_live) < len(g_all):
        hint = ("服务器 = 站点运行情况 · GitCode = %d 个源码仓库 · "
                "GitHub = %d 个已推送，另有 %d 个待补推"
                % (counts["gitcode"], len(g_live), len(g_all) - len(g_live)))
    else:
        hint = "服务器 = 站点运行情况 · GitCode / GitHub = 源码仓库，两边不混"

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
    --bg:#e6eaf1;
    --card:#ffffff;
    --line:#d7dee8;
    --ink:#101419;
    --ink-2:#3f4855;
    --ink-3:#5c6675;
    --ink-4:#838c9b;
    --blue:#0a4fc4;
    --blue-bg:#dde9fb;
    --green:#077a55;
    --green-bg:#d9f2e7;
    --orange:#b25c05;
    --orange-bg:#fcead2;
    --red:#b62f27;
    --red-bg:#fadfdc;
    --gray-bg:#e8ecf2;
    --sans:"PingFang SC","Microsoft YaHei",-apple-system,"Segoe UI",sans-serif;
    --mono:ui-monospace,"IBM Plex Mono",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box;margin:0;padding:0;}
  body{
    background:var(--bg);
    background-image:linear-gradient(180deg,#dfe5ef 0%,#e9edf3 360px,#eef1f6 100%);
    background-attachment:fixed;
    color:var(--ink);
    font-family:var(--sans);font-size:14px;line-height:1.6;
    padding:12px 18px 48px;-webkit-font-smoothing:antialiased;
  }
  .page{max-width:960px;margin:0 auto;}

  /* 顶栏：标签 + 时间 */
  .top{display:flex;align-items:center;justify-content:space-between;gap:16px;
       flex-wrap:wrap;margin-bottom:10px;}
  .stamp{font-family:var(--mono);font-size:11.5px;color:var(--ink-3);text-align:right;line-height:1.7;}
  .stamp b{color:var(--ink-2);font-weight:600;}

  /* 标签 */
  .tabs{display:inline-flex;background:#dce2eb;border-radius:12px;padding:4px;gap:4px;
        box-shadow:inset 0 1px 2px rgba(16,24,40,.05);}
  .tabs button{
    appearance:none;border:0;background:transparent;font-family:inherit;
    font-size:13px;font-weight:500;color:var(--ink-3);padding:7px 18px;border-radius:9px;
    cursor:pointer;transition:background .15s,color .15s;
  }
  .tabs button:hover{color:var(--ink-2);}
  .tabs button.on{background:#fff;color:var(--blue);font-weight:600;box-shadow:0 1px 3px rgba(16,24,40,.14);}
  .tabs button u{text-decoration:none;font-family:var(--mono);font-size:11px;
                 color:var(--ink-4);margin-left:6px;font-weight:500;}
  .tabs button.on u{color:var(--blue);opacity:.85;}
  .hint{margin:0 0 16px 6px;font-size:12px;color:var(--ink-4);}
  .gh-note{margin:0 0 16px;padding:10px 14px;background:#fdf3e3;border:1px solid #f0dfc0;
           border-radius:10px;font-size:12.5px;color:#7a5a1e;line-height:1.6;}

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
    padding:19px 22px;margin-bottom:13px;
    box-shadow:0 1px 2px rgba(16,24,40,.05);
    transition:border-color .15s,box-shadow .15s,transform .15s;
  }
  .card:last-child{margin-bottom:0;}
  .card:hover{border-color:#c2ccda;box-shadow:0 4px 16px rgba(16,24,40,.09);}
  .left{flex:1;min-width:0;}

  .hd{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
  .hd h3{font-size:16px;font-weight:600;letter-spacing:.1px;}

  .pill{font-size:11.5px;font-weight:500;padding:2px 10px;border-radius:999px;white-space:nowrap;}
  .pill.blue{color:var(--blue);background:var(--blue-bg);}
  .pill.green{color:var(--green);background:var(--green-bg);}
  .pill.orange{color:var(--orange);background:var(--orange-bg);}
  .pill.red{color:var(--red);background:var(--red-bg);}
  .pill.gray{color:var(--ink-3);background:var(--gray-bg);}
  .pill::before{content:"";display:inline-block;width:5px;height:5px;border-radius:50%;
                background:currentColor;margin-right:5px;vertical-align:1.5px;opacity:.9;}

  .desc{margin-top:9px;font-size:13.5px;color:var(--ink-3);line-height:1.65;}
  .rn{font-family:var(--mono);font-weight:600;font-size:12.5px;color:var(--ink-2);
      letter-spacing:-.1px;}
  .meta{margin-top:7px;font-size:12px;color:var(--ink-4);font-family:var(--mono);
        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .meta i{font-style:normal;font-size:10.5px;margin-left:2px;}

  .act{flex:0 0 auto;display:flex;flex-direction:column;align-items:flex-end;gap:6px;
       max-width:250px;}
  .url{font-family:var(--mono);font-size:10px;color:var(--ink-4);line-height:1.45;
       text-align:right;word-break:break-all;max-width:250px;letter-spacing:-.1px;}

  .btn{
    flex:0 0 auto;display:inline-flex;align-items:center;justify-content:center;
    min-width:66px;height:30px;padding:0 14px;border-radius:9px;
    background:var(--blue-bg);color:var(--blue);font-size:12.5px;font-weight:500;
    text-decoration:none;border:1px solid #c6d8f6;
    transition:background .15s,color .15s,border-color .15s;
  }
  .btn:hover{background:var(--blue);color:#fff;border-color:var(--blue);}
  .btn.off{background:var(--gray-bg);color:var(--ink-4);cursor:default;border-color:#dbe1ea;}
  .btn.off:hover{background:var(--gray-bg);color:var(--ink-4);border-color:#dbe1ea;}

  footer{margin-top:26px;padding:0 6px;display:flex;justify-content:space-between;gap:12px;
         flex-wrap:wrap;font-size:11.5px;color:var(--ink-4);font-family:var(--mono);}

  @media (max-width:700px){
    body{padding:20px 12px 40px;}
    .card{flex-direction:column;align-items:stretch;gap:12px;padding:17px;border-radius:14px;}
    .act{max-width:100%;align-items:flex-start;}
    .url{text-align:left;max-width:100%;}
    .meta{white-space:normal;}
    .top h1{font-size:19px;}
  }
</style>
</head>
<body>
<div class="page">

  <div class="top">
    <div class="tabs">
      <button id="tab-servers" class="on" onclick="sw('servers')">服务器<u>%(N3)s</u></button>
      <button id="tab-gitcode" onclick="sw('gitcode')">GitCode<u>%(N1)s</u></button>
      <button id="tab-github" onclick="sw('github')">GitHub<u>%(N2)s</u></button>
    </div>
    <div class="stamp">更新 <b>%(NOW)s</b> · 每 10 分钟刷新</div>
  </div>
  <p class="hint">%(HINT)s</p>

  <main>
    <section id="panel-servers" class="panel on">%(P3)s
    </section>
    <section id="panel-gitcode" class="panel">
%(P1)s
    </section>
    <section id="panel-github" class="panel">
      <p class="gh-note">GitHub 侧目前只有备份类仓库。站点源码全部在 GitCode——因为 github.com 网页访问受限，新仓库无法创建。</p>
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
                .replace("%(HINT)s", hint)
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
