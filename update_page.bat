@echo off
cd /d D://SyncDashboard
set "PY=C://Program Files\Python\python.exe"
"%PY%" probe_sites.py >> update.log 2>&1
"%PY%" build.py >> update.log 2>&1
git add -A
git diff --cached --quiet
if %errorlevel%==0 goto :eof
git -c user.name=wangxsboss -c user.email=281820690@qq.com commit -q -m "auto update site status"
git push -q github master:main 2>> update.log
git push -q origin master:main 2>> update.log
echo done >> update.log
