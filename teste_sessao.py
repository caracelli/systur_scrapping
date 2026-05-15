import sys
import subprocess

def garantir_dependencias():
    for pacote in ["selenium", "webdriver-manager", "openpyxl"]:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"[INFO] Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote, "-q"])
            print(f"[OK] {pacote} instalado.")

garantir_dependencias()

import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager

URL_SYSTUR = "https://systur.cvc.com.br/pls/systur/pkg_html.prc_frame?p_chama_frame=S"
URL_SYSTUR_BASE = "systur.cvc.com.br"

print("[INFO] Abrindo Edge...")
service = Service(EdgeChromiumDriverManager().install())
driver = webdriver.Edge(service=service)
driver.maximize_window()
driver.get(URL_SYSTUR)

print("\n" + "=" * 52)
print("  Faça login no SYSTUR e aguarde...")
print("  O script continua automaticamente após o login.")
print("=" * 52 + "\n")

# Aguarda até detectar que está logado (até 5 minutos)
for _ in range(100):
    if URL_SYSTUR_BASE in driver.current_url and "login" not in driver.current_url.lower():
        # Verifica se o conteúdo da página indica sessão ativa
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
