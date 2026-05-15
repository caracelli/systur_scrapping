@echo off
echo Executando teste_sessao.py...
python teste_sessao.py > logs\teste_sessao.log 2>&1

echo.
echo === RESULTADO ===
type logs\teste_sessao.log

echo.
echo Sincronizando log com GitHub...
git add logs\teste_sessao.log
git commit -m "log: resultado do teste_sessao"
git push

echo.
echo Pronto! Log enviado para analise.
pause
