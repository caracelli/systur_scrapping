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

sys.path.insert(0, "src")
import sessao

driver = sessao.abrir()       # carrega credenciais + abre Edge + navega para o SYSTUR
sessao.garantir_sessao(driver) # faz login automatico se popup aparecer

print("[OK] Sessao ativa. Pronto para scraping.")
input("\nPressione Enter para fechar o browser...")
driver.quit()
