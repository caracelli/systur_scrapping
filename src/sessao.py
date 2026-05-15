import time
import xml.etree.ElementTree as ET
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

URL_SYSTUR = "https://systur.cvc.com.br/pls/systur/pkg_html.prc_frame?p_chama_frame=S"
URL_SYSTUR_BASE = "systur.cvc.com.br"
URL_POPUP_LOGIN = "p_tipo_acao=POPUP"
CRED_PATH = Path("credenciais.xml")

# Credenciais carregadas uma vez e mantidas em memória durante toda a execução
_usuario: str = ""
_senha: str = ""


def carregar_credenciais() -> None:
    global _usuario, _senha
    if not CRED_PATH.exists():
        raise FileNotFoundError(
            "Arquivo credenciais.xml não encontrado.\n"
            "Crie o arquivo com seu usuario e senha."
        )
    tree = ET.parse(CRED_PATH)
    root = tree.getroot()
    _usuario = root.findtext("usuario", "").strip()
    _senha = root.findtext("senha", "").strip()
    if not _usuario or not _senha or _usuario == "SEU_USUARIO":
        raise ValueError(
            "Credenciais em branco ou não preenchidas.\n"
            "Edite o arquivo credenciais.xml e preencha usuario e senha."
        )
    print("[OK] Credenciais carregadas.")


def abrir() -> webdriver.Edge:
    carregar_credenciais()
    print("[INFO] Abrindo Edge...")
    driver = webdriver.Edge()
    driver.maximize_window()
    driver.get(URL_SYSTUR)
    return driver


def _janela_popup(driver: webdriver.Edge) -> tuple[str | None, str]:
    """Retorna (handle_popup, handle_atual). handle_popup é None se não houver popup."""
    handle_atual = driver.current_window_handle
    for handle in driver.window_handles:
        try:
            driver.switch_to.window(handle)
            if URL_POPUP_LOGIN in driver.current_url:
                driver.switch_to.window(handle_atual)
                return handle, handle_atual
        except WebDriverException:
            continue
    driver.switch_to.window(handle_atual)
    return None, handle_atual


def _fazer_login_popup(driver: webdriver.Edge) -> None:
    if not _usuario or not _senha:
        raise RuntimeError("Credenciais não carregadas. Chame carregar_credenciais() antes de abrir o browser.")
    print("[INFO] Efetuando login automatico no popup...")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "p_usuario"))
    )
    driver.find_element(By.NAME, "p_usuario").clear()
    driver.find_element(By.NAME, "p_usuario").send_keys(_usuario)
    driver.find_element(By.NAME, "p_senha").clear()
    driver.find_element(By.NAME, "p_senha").send_keys(_senha)
    driver.find_element(By.XPATH, "//input[@value='Login']").click()
    print("[OK] Credenciais enviadas.")


def _resolver_popup(driver: webdriver.Edge, tentativas: int = 2) -> bool:
    """Verifica se há popup de login, tenta fazer login até `tentativas` vezes.
    Fecha o browser e encerra o processo se todas as tentativas falharem."""
    handle_popup, handle_atual = _janela_popup(driver)
    if not handle_popup:
        return False

    for tentativa in range(1, tentativas + 1):
        try:
            print(f"[INFO] Tentativa de login {tentativa}/{tentativas}...")
            driver.switch_to.window(handle_popup)
            _fazer_login_popup(driver)
            WebDriverWait(driver, 15).until(
                lambda d: handle_popup not in d.window_handles
            )
            driver.switch_to.window(handle_atual)
            print("[OK] Sessao renovada.")
            return True
        except Exception as e:
            print(f"[ERRO] Tentativa {tentativa} falhou: {e}")
            if tentativa < tentativas:
                time.sleep(3)

    print("[ERRO] Login falhou apos todas as tentativas. Encerrando...")
    try:
        driver.quit()
    except Exception:
        pass
    import sys
    sys.exit(1)


def garantir_sessao(driver: webdriver.Edge) -> None:
    """Chame antes de cada operação crítica. Faz login automático se necessário."""
    time.sleep(1)

    if _resolver_popup(driver):
        return

    # Sem popup — verifica se está no domínio correto
    if URL_SYSTUR_BASE not in driver.current_url:
        print("[INFO] Fora do SYSTUR. Navegando de volta...")
        driver.get(URL_SYSTUR)
        time.sleep(3)
        if _resolver_popup(driver):
            return

    # Se ainda não resolveu, assume que está logado (página com frames)


def executar_com_sessao(driver: webdriver.Edge, acao, *args, **kwargs):
    """
    Executa uma ação garantindo sessão ativa.
    Se falhar por popup de login, renova a sessão e retenta uma vez.
    """
    try:
        return acao(*args, **kwargs)
    except WebDriverException:
        if _resolver_popup(driver):
            return acao(*args, **kwargs)
        raise
