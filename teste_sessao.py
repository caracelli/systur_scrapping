import sys
import subprocess

def garantir_dependencias():
    pacotes = ["selenium", "webdriver-manager", "openpyxl"]
    for pacote in pacotes:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"[INFO] Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote, "-q"])
            print(f"[OK] {pacote} instalado.")

garantir_dependencias()

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException

DEBUG_PORT = 9222
URL_SYSTUR = "systur.cvc.com.br"

print("Tentando conectar ao Edge na porta 9222...")

options = Options()
options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")

try:
    driver = webdriver.Edge(options=options)
    print(f"[OK] Edge conectado. Abas abertas: {len(driver.window_handles)}")

    aba_systur = None
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        url = driver.current_url
        print(f"     Aba: {url}")
        if URL_SYSTUR in url:
            aba_systur = handle

    if aba_systur:
        driver.switch_to.window(aba_systur)
        print(f"\n[OK] SYSTUR encontrado e selecionado: {driver.current_url}")
    else:
        print("\n[AVISO] SYSTUR NÃO encontrado em nenhuma aba. Navegue até o site e faça login.")

except WebDriverException as e:
    print("[ERRO] Não foi possível conectar ao Edge.")
    print("       Execute 'abrir_edge.bat' primeiro.")
    sys.exit(1)
