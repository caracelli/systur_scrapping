@echo off
echo Iniciando Edge com depuracao remota...

set EDGE=""
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" set EDGE="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" set EDGE="C:\Program Files\Microsoft\Edge\Application\msedge.exe"

if %EDGE%=="" (
    echo [ERRO] Edge nao encontrado. Ajuste o caminho neste arquivo.
    pause
    exit /b 1
)

start "" %EDGE% --remote-debugging-port=9222

echo [OK] Edge aberto na porta 9222.
echo Navegue ate o SYSTUR, faca login e entao execute o scraper.
pause
