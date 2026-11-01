# -*- coding: utf-8 -*-
"""看板自动更新（无控制台版本，供 pythonw.exe 调用）

流程：拉取 9 个站点仓库 → 刷新两台服务器镜像 → 探测站点状态
      → 重新生成页面 → 提交并推送看板

计划任务：C:\\Program Files\\Python\\pythonw.exe D:\\SyncDashboard\\update_page.py
"""
import os
import subprocess
import sys
from datetime import datetime

BASE = r"D:\SyncDashboard"
LOG = os.path.join(BASE, "update.log")
PY = r"C:\Program Files\Python\python.exe"
GIT_ENV = dict(os.environ)
GIT_ENV["GIT_SSH_COMMAND"] = "ssh -i D:/AccountVault/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
GIT_ENV["GIT_TERMINAL_PROMPT"] = "0"

REPOS = [
    "xianyu-system", "mediacrawler", "wb2api", "openlist", "wb-switch",
    "dsh-our-free-model", "shitou-bot", "odds", "server-deploy",
]
MIRRORS = ["server-a-code", "server-b-code"]


def log(msg):
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n" % (stamp, msg))
    except Exception:
        pass


def sh(args, cwd=None, timeout=600):
    try:
        r = subprocess.run(args, cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace",
                           env=GIT_ENV, timeout=timeout)
        return (r.stdout or "").strip(), (r.stderr or "").strip(), r.returncode
    except Exception as e:
        return "", str(e), 1


def main():
    os.chdir(BASE)

    # 1) 拉取 9 个站点仓库最新提交
    for name in REPOS:
        p = os.path.join(r"D:\Repos", name)
        if not os.path.isdir(os.path.join(p, ".git")):
            continue
        out, err, rc = sh(["git", "pull", "-q", "--ff-only"], cwd=p, timeout=180)
        if rc != 0 and err:
            log("[pull] %s 失败：%s" % (name, err.splitlines()[0][:120]))

    # 2) 刷新两台服务器源码镜像
    for name in MIRRORS:
        p = os.path.join(r"D:\ServerMirror", name)
        if not os.path.isdir(os.path.join(p, ".git")):
            continue
        sh(["git", "fetch", "--depth", "1", "origin", "main"], cwd=p, timeout=300)
        sh(["git", "reset", "--hard", "-q", "FETCH_HEAD"], cwd=p, timeout=120)

    # 3) 探测站点状态 + 重新生成页面
    for script in ("probe_sites.py", "build.py"):
        out, err, rc = sh([PY, os.path.join(BASE, script)], cwd=BASE, timeout=900)
        if rc != 0:
            log("[%s] 失败：%s" % (script, (err or out)[:300]))

    # 4) 提交并推送
    sh(["git", "add", "-A"], cwd=BASE)
    _o, _e, rc = sh(["git", "diff", "--cached", "--quiet"], cwd=BASE)
    if rc == 0:
        return  # 无变化
    sh(["git", "-c", "user.name=wangxsboss", "-c", "user.email=281820690@qq.com",
        "commit", "-q", "-m", "auto update site status"], cwd=BASE)
    for remote in ("github", "origin"):
        sh(["git", "push", "-q", remote, "master:main"], cwd=BASE, timeout=300)
    log("done")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log("[fatal] %s" % e)
    sys.exit(0)
