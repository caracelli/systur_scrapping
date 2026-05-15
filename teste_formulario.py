import sys
import subprocess
from pathlib import Path

def garantir_dependencias():
    for pacote in ["selenium", "openpyxl"]:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"[INFO] Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote, "-q"])

garantir_dependencias()

# Redireciona saida para arquivo e console ao mesmo tempo
LOG = Path("logs/teste_formulario.log")
LOG.parent.mkdir(exist_ok=True)

class Tee:
    def __init__(self, *streams):
        self.streams = streams
    def write(self, data):
        for s in self.streams:
            s.write(data)
            s.flush()
    def flush(self):
        for s in self.streams:
            s.flush()

log_file = open(LOG, "w", encoding="utf-8")
sys.stdout = Tee(sys.__stdout__, log_file)

sys.path.insert(0, "src")
import sessao
import navegacao
import time
from selenium.webdriver.common.by import By

driver = sessao.abrir()
sessao.garantir_sessao(driver)
print("[OK] Sessao ativa.")

navegacao.ir_para_vendedores(driver)
navegacao.entrar_frame_principal(driver)

# Lista inputs e links do formulario
print("\n=== ELEMENTOS DO FORMULARIO ===")
for el in driver.find_elements(By.TAG_NAME, "input"):
    print(f"  <input> name='{el.get_attribute('name')}' type='{el.get_attribute('type')}' value='{el.get_attribute('value')}'")
for el in driver.find_elements(By.TAG_NAME, "a"):
    if el.text.strip():
        print(f"  <a> text='{el.text.strip()}' href='{el.get_attribute('href')}'")

sys.stdout = sys.__stdout__
print("\n[PAUSA] Inspecione a tela no browser e preencha o xpaths.xml.")
codigo = input("Digite um Codigo Pessoa para teste e pressione Enter: ").strip()
sys.stdout = Tee(sys.__stdout__, log_file)

print(f"\n[INFO] Consultando Codigo Pessoa: {codigo}")
navegacao.sair_frame(driver)
navegacao.entrar_frame_principal(driver)

# Preenche campo e clica Consultar
for el in driver.find_elements(By.TAG_NAME, "input"):
    if el.get_attribute('type') not in ('submit', 'button', 'hidden', 'image', 'reset'):
        el.clear()
        el.send_keys(codigo)
        print(f"  [OK] Preencheu name='{el.get_attribute('name')}'")
        break

for el in driver.find_elements(By.TAG_NAME, "a"):
    if "consultar" in el.text.strip().lower():
        el.click()
        print(f"  [OK] Clicou Consultar")
        break

time.sleep(3)

# Captura tabela inteira como texto
print("\n=== RESULTADO DA CONSULTA ===")
tabelas = driver.find_elements(By.TAG_NAME, "table")
for i, tabela in enumerate(tabelas):
    linhas = tabela.find_elements(By.TAG_NAME, "tr")
    for linha in linhas:
        celulas = [c.text.strip() for c in linha.find_elements(By.TAG_NAME, "td")]
        if any(celulas):
            print(f"  {celulas}")

driver.quit()
print("\n[INFO] Browser fechado.")

log_file.close()
sys.stdout = sys.__stdout__

# Commita log
print("Sincronizando log...")
subprocess.run(["git", "add", str(LOG)], check=True)
subprocess.run(["git", "commit", "-m", "log: resultado do teste_formulario"], check=True)
subprocess.run(["git", "push"], check=True)
print("Pronto!")
