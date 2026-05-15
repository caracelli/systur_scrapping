import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FRAME_MENU = "FRM_MENU"
FRAME_PRINCIPAL = "FRM_PRINCIPAL"
JS_VENDEDORES = 'open_html("pkg_gen_consulta_padrao.prc_inicial?prc_cd_consulta=4", "462")'


def ir_para_vendedores(driver: webdriver.Edge) -> None:
    print("[INFO] Navegando para Vendedores...")
    driver.switch_to.default_content()
    driver.switch_to.frame(FRAME_MENU)
    driver.execute_script(JS_VENDEDORES)
    driver.switch_to.default_content()
    time.sleep(2)
    print("[OK] Tela de Vendedores carregada.")


def entrar_frame_principal(driver: webdriver.Edge) -> None:
    driver.switch_to.default_content()
    driver.switch_to.frame(FRAME_PRINCIPAL)


def sair_frame(driver: webdriver.Edge) -> None:
    driver.switch_to.default_content()
