@echo off
cd /d D:\SyncDashboard
set "PY=C:\Program Files\Python\python.exe"
set "GSSH=ssh -i D:/AccountVault/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
set GIT_SSH_COMMAND=%GSSH%
rem 更新两台服务器源码的本地镜像（浅克隆拉取最新提交）
git -C D:\ServerMirror\server-a-code fetch --depth 1 origin main 2>>update.log
git -C D:\ServerMirror\server-a-code reset --hard -q FETCH_HEAD 2>>update.log
git -C D:\ServerMirror\server-b-code fetch --depth 1 origin main 2>>update.log
git -C D:\ServerMirror\server-b-code reset --hard -q FETCH_HEAD 2>>update.log
"%PY%" probe_sites.py >> update.log 2>&1
"%PY%" build.py >> update.log 2>&1
git add -A
git diff --cached --quiet
if %errorlevel%==0 goto :eof
git -c user.name=wangxsboss -c user.email=281820690@qq.com commit -q -m "auto update site status"
git push -q github master:main 2>> update.log
git push -q origin master:main 2>> update.log
echo done >> update.log
