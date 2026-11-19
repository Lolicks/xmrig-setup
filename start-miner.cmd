@echo off
cd /d "%~dp0"

rem Имя воркера: первый аргумент, иначе имя компьютера.
rem В разных сетях имена могут совпадать - задавай уникальное вручную:
rem   start-miner.cmd TENCENT-EPYC-1
set "RIG=%~1"
if "%RIG%"=="" set "RIG=%COMPUTERNAME%"

title XMRig - %RIG%
echo ============================================================
echo  XMRig 6.26.0  ^|  RIG: %RIG%
echo  Wallet: 49iGVTQcY3Xd64MmZAoXLtUFUFJqEGH8sbVcvWCogLm7MgkeBG2Cnug2MmtoTpxhSocb5Pai6w79aCSKVp4ab5VrPd6S9fq
echo  Pool:   xmrpool.eu:3333 (TLS) + failover supportxmr
echo  API:    http://localhost:8080/1/summary  (только внутри своей сети)
echo ============================================================
echo.
xmrig.exe --rig-id=%RIG% --api-worker-id=%RIG%
echo.
echo XMRig stopped.
pause
