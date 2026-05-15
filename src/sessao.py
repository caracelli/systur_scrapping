import time
import xml.etree.ElementTree as ET
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

URL_SYSTUR = "https://systur.cvc.com.br/pls/systur/pkg_html.prc_frame?p_chama_frame=S"
URL_SYSTUR_BASE = "systur.cvc.com.br"
XPATHS_PATH = Path("assets/xpaths.xml")


def _xpath(page: str, element_id: str) -> str:
    tree = ET.parse(XPATHS_PATH)
    for page_node in tree.getroot().findall("page"):
        if page_node.get("name") == page:
            for elem in page_node.findall("element"):
                if elem.get("id") == element_id:
                    return elem.text.strip()
    raise ValueError(f"XPath não encontrado: {page}/{element_id}")


def abrir() -> webdriver.Edge:
    print("[INFO] Abrindo Edge...")
    service = Service(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service=service)
    driver.maximize_window()
    driver.get(URL_SYSTUR)
    return driver


def _esta_logado(driver: webdriver.Edge) -> bool:
    if URL_SYSTUR_BASE not in driver.current_url:
        return False
    try:
        fonte = driver.page_source
        return "ltimo Acesso" in fonte or "Finalizar" in fonte
    except Exception:
        return False


def aguardar_login(driver: webdriver.Edge, timeout: int = 300) -> None:
    print("\n" + "=" * 52)
    print("  AÇÃO NECESSÁRIA")
    print("  Faça login no SYSTUR para continuar.")
    print(f"  Aguardando até {timeout // 60} minutos...")
    print("=" * 52 + "\n")

    inicio = time.time()
    while time.time() - inicio < timeout:
        if _esta_logado(driver):
            print("[OK] Login detectado. Continuando...\n")
            return
        time.sleep(3)

    raise TimeoutError("Tempo esgotado aguardando login. Execute novamente.")


def garantir_sessao(driver: webdriver.Edge) -> None:
    if not _esta_logado(driver):
        aguardar_login(driver)
