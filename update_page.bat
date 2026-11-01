@echo off
cd /d D:\SyncDashboard
set "PY=C:\Program Files\Python\python.exe"
set "GSSH=ssh -i D:/AccountVault/.ssh/id_ed25519 -o StrictHostKeyChecking=no"
set GIT_SSH_COMMAND=%GSSH%

rem 1) pull latest commits of the 8 site repos (servers push every 10 min)
for %%d in (xianyu-system mediacrawler wb2api openlist wb-switch dsh-our-free-model shitou-bot odds server-deploy) do (
  if exist "D:\Repos\%%d\.git" git -C "D:\Repos\%%d" pull -q --ff-only >> update.log 2>&1
)

rem 2) refresh local mirrors of the two server code bundles
git -C D:\ServerMirror\server-a-code fetch --depth 1 origin main >> update.log 2>&1
git -C D:\ServerMirror\server-a-code reset --hard -q FETCH_HEAD >> update.log 2>&1
git -C D:\ServerMirror\server-b-code fetch --depth 1 origin main >> update.log 2>&1
git -C D:\ServerMirror\server-b-code reset --hard -q FETCH_HEAD >> update.log 2>&1

rem 3) probe server site status and rebuild the page
"%PY%" probe_sites.py >> update.log 2>&1
"%PY%" build.py >> update.log 2>&1

rem 4) commit and push the dashboard
git add -A
git diff --cached --quiet
if %errorlevel%==0 goto :eof
git -c user.name=wangxsboss -c user.email=281820690@qq.com commit -q -m "auto update site status"
git push -q github master:main 2>> update.log
git push -q origin master:main 2>> update.log
echo done >> update.log
