import sys
import subprocess

def garantir_dependencias():
    for pacote in ["selenium", "openpyxl"]:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"[INFO] Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote, "-q"])

garantir_dependencias()

sys.path.insert(0, "src")
import sessao
import time
from selenium.webdriver.common.by import By

# 1. Abre e faz login
driver = sessao.abrir()
sessao.garantir_sessao(driver)
print("[OK] Sessao ativa.\n")

# 2. Lista os frames da pagina principal
print("Frames encontrados na pagina:")
frames = driver.find_elements(By.TAG_NAME, "frame")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
for f in frames:
    print(f"  <frame> name='{f.get_attribute('name')}' id='{f.get_attribute('id')}' src='{f.get_attribute('src')}'")
for f in iframes:
    print(f"  <iframe> name='{f.get_attribute('name')}' id='{f.get_attribute('id')}' src='{f.get_attribute('src')}'")

# 3. Executa o JavaScript de navegacao
print("\n[INFO] Executando navegacao para Vendedores...")
driver.execute_script('open_html("pkg_gen_consulta_padrao.prc_inicial?prc_cd_consulta=4", "462")')
time.sleep(3)

# 4. Lista frames novamente apos navegacao
print("\nFrames apos navegacao:")
frames = driver.find_elements(By.TAG_NAME, "frame")
for f in frames:
    print(f"  <frame> name='{f.get_attribute('name')}' id='{f.get_attribute('id')}' src='{f.get_attribute('src')}'")

print("\n[INFO] Verifique se a tela de busca de Vendedores abriu no browser.")
input("Pressione Enter para fechar...")
driver.quit()
