@echo off
rem Отключает донат разработчику без пересборки XMRig.
rem Нужны права администратора.
set "H=%SystemRoot%\System32\drivers\etc\hosts"

findstr /i /c:"donate.v2.xmrig.com" "%H%" >nul
if errorlevel 1 (
  >>"%H%" echo 127.0.0.1 donate.v2.xmrig.com
  >>"%H%" echo 127.0.0.1 donate.ssl.xmrig.com
  echo Added: donate hosts -> 127.0.0.1
) else (
  echo Already disabled.
)
echo.
echo Проверка:
findstr /i "xmrig.com" "%H%"
pause
