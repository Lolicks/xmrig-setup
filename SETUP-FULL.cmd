@echo off
cd /d "%~dp0"

rem ============================================================
rem  ОДНОКРАТНАЯ настройка. Без вложенных вызовов и без /Run.
rem  Запуск: SETUP-FULL.cmd   (или с именем файла аргументом)
rem ============================================================

rem Защита от повторного входа
if "%XM_SETUP_RUNNING%"=="1" exit /b 0
set "XM_SETUP_RUNNING=1"

set "RUNFILE=start-miner.cmd"
if not "%~1"=="" if exist "%~1" set "RUNFILE=%~1"

echo [0/4] Cleanup...
taskkill /IM xmrig.exe /F >nul 2>&1
schtasks /Delete /TN "XMRig-Miner" /F >nul 2>&1

echo [1/4] Power settings...
powercfg /change standby-timeout-ac 0    >nul 2>&1
powercfg /change standby-timeout-dc 0    >nul 2>&1
powercfg /change hibernate-timeout-ac 0  >nul 2>&1
powercfg /change hibernate-timeout-dc 0  >nul 2>&1
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c >nul 2>&1

echo [2/4] Отключаем донат разработчику...
set "H=%SystemRoot%\System32\drivers\etc\hosts"
findstr /i /c:"donate.v2.xmrig.com" "%H%" >nul 2>&1
if errorlevel 1 (
  >>"%H%" echo 127.0.0.1 donate.v2.xmrig.com
  >>"%H%" echo 127.0.0.1 donate.ssl.xmrig.com
  echo       OK
) else (
  echo       уже отключён
)

echo [3/4] Creating task "XMRig-Miner" for %RUNFILE% ...
schtasks /Create /TN "XMRig-Miner" /TR "\"%CD%\%RUNFILE%\"" /SC ONSTART /RU SYSTEM /RL HIGHEST /F >nul 2>&1

schtasks /Query /TN "XMRig-Miner" >nul 2>&1
if errorlevel 1 goto :error

echo [4/4] Starting miner once...
start "" "%~dp0%RUNFILE%"

echo.
echo ============================================================
echo  ALL DONE - один раз, без цикла.
echo  Задача создана, майнер запущен однократно.
echo  Check: https://xmrpool.eu/ + wallet
echo ============================================================
echo %DATE% %TIME% OK >> "%~dp0setup.log"
exit /b 0

:error
echo.
echo ERROR: задача не создана. Нужны права локального администратора.
echo %DATE% %TIME% FAILED >> "%~dp0setup.log"
exit /b 1
