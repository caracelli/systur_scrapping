@echo off
REM Duplo-clique: garante Python (instala se faltar) e executa o scraper.
REM Equivale a: powershell -ExecutionPolicy Bypass -File setup_e_executar.ps1
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_e_executar.ps1" %*
echo.
pause
