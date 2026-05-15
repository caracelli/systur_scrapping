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
URL_POPUP = "p_tipo_acao=POPUP"

print("[INFO] Abrindo Edge...")
driver = webdriver.Edge()
driver.maximize_window()
driver.get(URL_SYSTUR)

print("[INFO] Aguardando pagina carregar...")
time.sleep(3)

# Verifica se abriu popup de login
janelas = driver.window_handles
print(f"[INFO] Janelas abertas: {len(janelas)}")

if len(janelas) > 1:
    print("[INFO] Popup de login detectado.")
    print("       Faca o login no popup que abriu.")
    print("       O script continua automaticamente apos fechar o popup.\n")

    # Aguarda o popup fechar (até 5 minutos)
    for _ in range(100):
        if len(driver.window_handles) == 1:
            driver.switch_to.window(driver.window_handles[0])
            print("[OK] Login realizado! Sessao ativa.")
            print(f"     URL: {driver.current_url}")
            break
        time.sleep(3)
    else:
        print("[AVISO] Timeout aguardando login.")
else:
    # Sem popup — verifica se já está logado pela URL
    if URL_SYSTUR_BASE in driver.current_url:
        print("[OK] Sessao ja ativa, sem necessidade de login.")
        print(f"     URL: {driver.current_url}")
    else:
        print("[AVISO] Estado desconhecido. Verifique a pagina aberta.")

input("\nPressione Enter para fechar o browser...")
driver.quit()
