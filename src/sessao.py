import time
import xml.etree.ElementTree as ET
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

URL_SYSTUR = "https://systur.cvc.com.br/pls/systur/pkg_html.prc_frame?p_chama_frame=S"
URL_SYSTUR_BASE = "systur.cvc.com.br"
URL_POPUP_LOGIN = "p_tipo_acao=POPUP"
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
    if not usuario or not senha or usuario == "SEU_USUARIO":
        raise ValueError(
            "Credenciais em branco ou não preenchidas.\n"
            "Edite o arquivo credenciais.xml e preencha usuario e senha."
        )
    return usuario, senha


def abrir() -> webdriver.Edge:
    print("[INFO] Abrindo Edge...")
    driver = webdriver.Edge()
    driver.maximize_window()
    driver.get(URL_SYSTUR)
    return driver


def _janela_popup(driver: webdriver.Edge) -> tuple[str | None, str]:
    handle_principal = driver.current_window_handle
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if URL_POPUP_LOGIN in driver.current_url:
            driver.switch_to.window(handle_principal)
            return handle, handle_principal
    driver.switch_to.window(handle_principal)
    return None, handle_principal


def _esta_logado(driver: webdriver.Edge) -> bool:
    janela_principal = driver.window_handles[0]
    driver.switch_to.window(janela_principal)
    if URL_SYSTUR_BASE not in driver.current_url:
        return False
    try:
        fonte = driver.page_source
        return "ltimo Acesso" in fonte or "Finalizar" in fonte
    except Exception:
        return False


def _fazer_login_popup(driver: webdriver.Edge) -> None:
    usuario, senha = _credenciais()
    print("[INFO] Popup de login detectado. Realizando login automatico...")

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='text']"))
    )
    driver.find_element(By.XPATH, "//input[@type='text']").clear()
    driver.find_element(By.XPATH, "//input[@type='text']").send_keys(usuario)
    driver.find_element(By.XPATH, "//input[@type='password']").clear()
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys(senha)
    driver.find_element(By.XPATH, "//input[@value='Login']").click()
    print("[OK] Credenciais enviadas.")


def garantir_sessao(driver: webdriver.Edge) -> None:
    time.sleep(2)

    handle_popup, handle_principal = _janela_popup(driver)
    if handle_popup:
        driver.switch_to.window(handle_popup)
        _fazer_login_popup(driver)
        WebDriverWait(driver, 15).until(
            lambda d: handle_popup not in d.window_handles
        )
        driver.switch_to.window(handle_principal)
        print("[OK] Login concluido.")
        return

    if not _esta_logado(driver):
        driver.get(URL_SYSTUR)
        time.sleep(3)
        handle_popup, handle_principal = _janela_popup(driver)
        if handle_popup:
            driver.switch_to.window(handle_popup)
            _fazer_login_popup(driver)
            WebDriverWait(driver, 15).until(
                lambda d: handle_popup not in d.window_handles
            )
            driver.switch_to.window(handle_principal)
            print("[OK] Login concluido.")
        else:
            raise RuntimeError("Sessao invalida e popup de login nao detectado.")
