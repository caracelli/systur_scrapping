import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException

DEBUG_PORT = 9222
URL_SYSTUR = "systur.cvc.com.br"

print("Tentando conectar ao Chrome na porta 9222...")

options = Options()
options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")

try:
    driver = webdriver.Chrome(options=options)
    url_atual = driver.current_url
    print(f"[OK] Chrome conectado.")
    print(f"     URL atual: {url_atual}")

    if URL_SYSTUR in url_atual:
        print("[OK] SYSTUR está aberto no Chrome.")
    else:
        print("[AVISO] SYSTUR NÃO está aberto. Navegue até o site e faça login.")

except WebDriverException as e:
    print("[ERRO] Não foi possível conectar ao Chrome.")
    print("       Execute 'abrir_chrome.bat' primeiro.")
    sys.exit(1)
