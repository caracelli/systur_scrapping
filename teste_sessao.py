import sys
import subprocess

def garantir_dependencias():
    for pacote in ["selenium", "openpyxl"]:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"[INFO] Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote, "-q"])
            print(f"[OK] {pacote} instalado.")

garantir_dependencias()

import time
from selenium import webdriver

URL_SYSTUR = "https://systur.cvc.com.br/pls/systur/pkg_html.prc_frame?p_chama_frame=S"
URL_SYSTUR_BASE = "systur.cvc.com.br"

print("[INFO] Abrindo Edge...")
# Selenium 4 localiza o driver automaticamente sem precisar de internet
driver = webdriver.Edge()
driver.maximize_window()
driver.get(URL_SYSTUR)

print("\n" + "=" * 52)
print("  Faça login no SYSTUR e aguarde...")
print("  O script continua automaticamente após o login.")
print("=" * 52 + "\n")

for _ in range(100):
    if URL_SYSTUR_BASE in driver.current_url:
        fonte = driver.page_source
        if "ltimo Acesso" in fonte or "Finalizar" in fonte:
            print("[OK] Login detectado! Sessão ativa.")
            print(f"     URL: {driver.current_url}")
            break
    time.sleep(3)
else:
    print("[AVISO] Timeout aguardando login.")

input("\nPressione Enter para fechar o browser...")
driver.quit()
