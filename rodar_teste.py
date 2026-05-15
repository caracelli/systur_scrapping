import subprocess
import sys
from pathlib import Path

TESTE = "teste_navegacao.py"
LOG = Path("logs/teste_navegacao.log")
LOG.parent.mkdir(exist_ok=True)

print(f"Executando {TESTE}...")
resultado = subprocess.run(
    [sys.executable, TESTE],
    capture_output=True,
    text=True
)

saida = resultado.stdout + resultado.stderr
LOG.write_text(saida, encoding="utf-8")

print(saida)

print("Sincronizando log com GitHub...")
subprocess.run(["git", "add", str(LOG)], check=True)
subprocess.run(["git", "commit", "-m", f"log: resultado do {TESTE}"], check=True)
subprocess.run(["git", "push"], check=True)
print("Pronto! Log enviado para analise.")
