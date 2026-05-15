import time
import xml.etree.ElementTree as ET
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException

DEBUG_PORT = 9222
XPATHS_PATH = Path("assets/xpaths.xml")
URL_SYSTUR = "systur.cvc.com.br"


def _xpath(page: str, element_id: str) -> str:
    tree = ET.parse(XPATHS_PATH)
    for page_node in tree.getroot().findall("page"):
        if page_node.get("name") == page:
            for elem in page_node.findall("element"):
                if elem.get("id") == element_id:
                    return elem.text.strip()
    raise ValueError(f"XPath não encontrado: {page}/{element_id}")


def conectar() -> webdriver.Chrome:
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{DEBUG_PORT}")
    try:
        driver = webdriver.Edge(options=options)
        return driver
    except WebDriverException as e:
        raise RuntimeError(
            "\n[ERRO] Não foi possível conectar ao Edge.\n"
            "Execute 'abrir_edge.bat' primeiro, navegue até o SYSTUR e faça login.\n"
        ) from e


def _esta_logado(driver: webdriver.Chrome) -> bool:
    if URL_SYSTUR not in driver.current_url:
        return False
    try:
        frame_menu = driver.find_element(By.XPATH, _xpath("verificacao_sessao", "frame_menu"))
        driver.switch_to.frame(frame_menu)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, _xpath("verificacao_sessao", "indicador_logado")))
        )
        driver.switch_to.default_content()
        return True
    except Exception:
        driver.switch_to.default_content()
        return False


def aguardar_login(driver: webdriver.Chrome, timeout: int = 300) -> None:
    print("\n" + "=" * 52)
    print("  AÇÃO NECESSÁRIA")
    print("  Abra o SYSTUR no Chrome e efetue o login.")
    print(f"  Aguardando até {timeout // 60} minutos...")
    print("=" * 52 + "\n")

    inicio = time.time()
    while time.time() - inicio < timeout:
        if _esta_logado(driver):
            print("[OK] Login detectado. Continuando...\n")
            return
        time.sleep(3)

    raise TimeoutError("Tempo esgotado aguardando login. Execute novamente após fazer login.")


def garantir_sessao(driver: webdriver.Chrome) -> None:
    if not _esta_logado(driver):
        aguardar_login(driver)
