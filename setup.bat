@echo off
echo ========================================
echo  Setup - systur_scrapping
echo ========================================

:: Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Instale em https://python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado.

:: Cria ambiente virtual se nao existir
if not exist ".venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv .venv
)

:: Ativa o ambiente virtual
call .venv\Scripts\activate.bat

:: Instala dependencias
echo [INFO] Instalando dependencias...
pip install -r requirements.txt

echo.
echo ========================================
echo  Testando leitura da fila...
echo ========================================
python teste_fila.py

echo.
echo ========================================
echo  Setup concluido!
echo ========================================
pause
