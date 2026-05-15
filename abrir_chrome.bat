@echo off
echo Iniciando Chrome com depuracao remota...

:: Tenta caminhos comuns do Chrome
set CHROME=""
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

if %CHROME%=="" (
    echo [ERRO] Chrome nao encontrado. Ajuste o caminho neste arquivo.
    pause
    exit /b 1
)

start "" %CHROME% --remote-debugging-port=9222

echo [OK] Chrome aberto na porta 9222.
echo Navegue ate o SYSTUR, faca login e entao execute o scraper.
pause
