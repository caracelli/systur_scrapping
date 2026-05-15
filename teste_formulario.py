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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

CODIGO_TESTE = "3637910"  # primeiro da fila

driver = sessao.abrir()
sessao.garantir_sessao(driver)
print("[OK] Sessao ativa.")

navegacao.ir_para_vendedores(driver)
navegacao.entrar_frame_principal(driver)

# Preenche Codigo Pessoa
print(f"\n[INFO] Consultando codigo: {CODIGO_TESTE}")
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "prc_cd_pessoa")))
campo = driver.find_element(By.ID, "prc_cd_pessoa")
campo.clear()
campo.send_keys(CODIGO_TESTE)

# Clica Consultar
driver.find_element(By.ID, "prc_evento").click()
time.sleep(3)

# Captura tabela completa como texto
print("\n=== RESULTADO DA CONSULTA ===")
tabelas = driver.find_elements(By.TAG_NAME, "table")
print(f"Tabelas encontradas: {len(tabelas)}")

dados = []
for i, tabela in enumerate(tabelas):
    linhas = tabela.find_elements(By.TAG_NAME, "tr")
    for j, linha in enumerate(linhas):
        celulas = [c.text.strip() for c in linha.find_elements(By.TAG_NAME, "td")]
        if any(celulas):
            dados.append(celulas)
            print(f"  [{i}][{j}] {celulas}")

if not dados:
    print("[INFO] Sem resultados para este codigo. Seguindo para o proximo.")
else:
    print(f"[OK] {len(dados)} linha(s) encontrada(s).")

# Clica Voltar
print("\n[INFO] Clicando Voltar...")
try:
    driver.find_element(By.ID, "prc_voltar").click()
    time.sleep(2)
    print("[OK] Voltou ao formulario.")
except Exception as e:
    print(f"[AVISO] Voltar: {e}")

driver.quit()
print("\n[INFO] Browser fechado.")

log_file.close()
sys.stdout = sys.__stdout__

print("Sincronizando log...")
subprocess.run(["git", "add", str(LOG)], check=True)
subprocess.run(["git", "commit", "-m", "log: resultado do teste_formulario"], check=True)
subprocess.run(["git", "push"], check=True)
print("Pronto!")
