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
from selenium.common.exceptions import WebDriverException, NoSuchElementException

driver = sessao.abrir()
sessao.garantir_sessao(driver)
print("[OK] Sessao ativa.\n")

# Lista frames disponíveis
print("=== FRAMES ENCONTRADOS ===")
frames = driver.find_elements(By.TAG_NAME, "frame")
iframes = driver.find_elements(By.TAG_NAME, "iframe")
todos = frames + iframes
for i, f in enumerate(todos):
    print(f"  [{i}] name='{f.get_attribute('name')}' id='{f.get_attribute('id')}'")

print(f"\nTotal: {len(todos)} frame(s)\n")

# Tenta executar o JS em cada frame
JS = 'open_html("pkg_gen_consulta_padrao.prc_inicial?prc_cd_consulta=4", "462")'
print("=== TENTANDO NAVEGACAO EM CADA FRAME ===")

navegou = False
for i, f in enumerate(todos):
    try:
        driver.switch_to.frame(f)
        driver.execute_script(JS)
        time.sleep(2)
        print(f"  [OK] JS executado no frame [{i}] name='{f.get_attribute('name')}'")
        navegou = True
        driver.switch_to.default_content()
        break
    except Exception as e:
        print(f"  [FALHA] Frame [{i}]: {e}")
        driver.switch_to.default_content()

if not navegou:
    # Tenta clique direto pelos IDs do menu
    print("\n=== TENTANDO CLIQUE PELOS IDs DO MENU ===")
    for i, f in enumerate(todos):
        try:
            driver.switch_to.frame(f)
            el = driver.find_element(By.ID, "fd7")
            print(f"  [OK] Elemento #fd7 encontrado no frame [{i}]")
            el.click()
            time.sleep(1)
            el2 = driver.find_element(By.ID, "fd62")
            el2.click()
            time.sleep(1)
            print(f"  [OK] Clicou em RH > Vendedores no frame [{i}]")
            driver.switch_to.default_content()
            navegou = True
            break
        except NoSuchElementException:
            driver.switch_to.default_content()
        except Exception as e:
            print(f"  [FALHA] Frame [{i}]: {e}")
            driver.switch_to.default_content()

if navegou:
    print("\n[OK] Navegacao concluida. Verifique se a tela de busca abriu.")
else:
    print("\n[ERRO] Nao foi possivel navegar. Verifique os frames e IDs.")

input("\nPressione Enter para fechar...")
driver.quit()
