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
from selenium.common.exceptions import NoSuchElementException

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
print(f"Total: {len(todos)} frame(s)\n")

# Tenta JS em cada frame, registra qual funcionou
JS = 'open_html("pkg_gen_consulta_padrao.prc_inicial?prc_cd_consulta=4", "462")'
print("=== TENTANDO NAVEGACAO VIA JAVASCRIPT ===")

frame_js_ok = None
for i, f in enumerate(todos):
    nome = f.get_attribute('name') or f.get_attribute('id') or str(i)
    try:
        driver.switch_to.frame(f)
        # Verifica se a função existe antes de chamar
        existe = driver.execute_script("return typeof open_html !== 'undefined'")
        if existe:
            driver.execute_script(JS)
            time.sleep(3)
            print(f"  [OK] open_html executado no frame '{nome}'")
            frame_js_ok = nome
        else:
            print(f"  [INFO] open_html nao existe no frame '{nome}'")
        driver.switch_to.default_content()
    except Exception as e:
        print(f"  [ERRO] Frame '{nome}': {e}")
        driver.switch_to.default_content()

    if frame_js_ok:
        break

if frame_js_ok:
    print(f"\n[OK] Navegacao via JS concluida no frame '{frame_js_ok}'.")
else:
    print("\n[AVISO] open_html nao encontrado em nenhum frame.")
    print("        Tentando clique pelos IDs fd7 e fd62...")
    for i, f in enumerate(todos):
        nome = f.get_attribute('name') or str(i)
        try:
            driver.switch_to.frame(f)
            el = driver.find_element(By.ID, "fd7")
            print(f"  [OK] #fd7 encontrado no frame '{nome}'")
            el.click()
            time.sleep(1)
            driver.find_element(By.ID, "fd62").click()
            time.sleep(2)
            print(f"  [OK] Clicou RH > Vendedores no frame '{nome}'")
            driver.switch_to.default_content()
            break
        except NoSuchElementException:
            driver.switch_to.default_content()
        except Exception as e:
            print(f"  [ERRO] Frame '{nome}': {e}")
            driver.switch_to.default_content()

print("\n[INFO] URL atual:", driver.current_url)
time.sleep(2)
driver.quit()
print("[INFO] Browser fechado.")
