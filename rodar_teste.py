import subprocess
import sys
from pathlib import Path

LOG = Path("logs/teste_sessao.log")
LOG.parent.mkdir(exist_ok=True)

print("Executando teste_sessao.py...")
resultado = subprocess.run(
    [sys.executable, "teste_sessao.py"],
    capture_output=True,
    text=True
)

saida = resultado.stdout + resultado.stderr
LOG.write_text(saida, encoding="utf-8")

print(saida)

print("Sincronizando log com GitHub...")
subprocess.run(["git", "add", str(LOG)], check=True)
subprocess.run(["git", "commit", "-m", "log: resultado do teste_sessao"], check=True)
subprocess.run(["git", "push"], check=True)
print("Pronto! Log enviado para analise.")
