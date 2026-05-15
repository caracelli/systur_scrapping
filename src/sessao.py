import time
import xml.etree.ElementTree as ET
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

URL_SYSTUR = "https://systur.cvc.com.br/pls/systur/pkg_html.prc_frame?p_chama_frame=S"
URL_SYSTUR_BASE = "systur.cvc.com.br"
XPATHS_PATH = Path("assets/xpaths.xml")
CRED_PATH = Path("credenciais.xml")


def _xpath(page: str, element_id: str) -> str:
    tree = ET.parse(XPATHS_PATH)
    for page_node in tree.getroot().findall("page"):
        if page_node.get("name") == page:
            for elem in page_node.findall("element"):
                if elem.get("id") == element_id:
                    return elem.text.strip()
    raise ValueError(f"XPath não encontrado: {page}/{element_id}")


def _credenciais() -> tuple[str, str]:
    if not CRED_PATH.exists():
        raise FileNotFoundError(
            "Arquivo credenciais.xml não encontrado.\n"
            "Crie o arquivo com seu usuario e senha."
        )
    tree = ET.parse(CRED_PATH)
    root = tree.getroot()
    usuario = root.findtext("usuario", "").strip()
    senha = root.findtext("senha", "").strip()
    if not usuario or not senha:
        raise ValueError("Preencha usuario e senha no credenciais.xml.")
    return usuario, senha


def abrir() -> webdriver.Edge:
    print("[INFO] Abrindo Edge...")
    driver = webdriver.Edge()
    driver.maximize_window()
    driver.get(URL_SYSTUR)
    return driver


def _esta_na_tela_login(driver: webdriver.Edge) -> bool:
    try:
        xpath = _xpath("login", "indicador_login")
        if xpath:
            driver.find_element(By.XPATH, xpath)
            return True
    except (NoSuchElementException, ValueError):
        pass
    return False


def _esta_logado(driver: webdriver.Edge) -> bool:
    if URL_SYSTUR_BASE not in driver.current_url:
        return False
    try:
        fonte = driver.page_source
        return "ltimo Acesso" in fonte or "Finalizar" in fonte
    except Exception:
        return False


def _fazer_login(driver: webdriver.Edge) -> None:
    usuario, senha = _credenciais()
    print("[INFO] Realizando login automatico...")
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, _xpath("login", "campo_usuario")))
        )
        driver.find_element(By.XPATH, _xpath("login", "campo_usuario")).send_keys(usuario)
        driver.find_element(By.XPATH, _xpath("login", "campo_senha")).send_keys(senha)
        driver.find_element(By.XPATH, _xpath("login", "btn_entrar")).click()
        print("[OK] Login enviado. Aguardando redirecionamento...")
        WebDriverWait(driver, 15).until(lambda d: _esta_logado(d))
        print("[OK] Login realizado com sucesso.")
    except TimeoutException:
        raise RuntimeError("Falha no login: timeout aguardando redirecionamento apos login.")


def garantir_sessao(driver: webdriver.Edge) -> None:
    if _esta_logado(driver):
        return
    if _esta_na_tela_login(driver):
        _fazer_login(driver)
        return
    # Navega para o SYSTUR e tenta login
    driver.get(URL_SYSTUR)
    time.sleep(2)
    if _esta_na_tela_login(driver):
        _fazer_login(driver)
    elif not _esta_logado(driver):
        raise RuntimeError("Nao foi possivel detectar o estado da sessao. Verifique os XPaths.")
