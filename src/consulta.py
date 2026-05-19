import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import navegacao

# Tabela de dados é sempre a de índice 1 (índice 0 é o título)
# Linhas de dados começam no índice 2 (0=header grupo, 1=header colunas)
INDICE_TABELA_DADOS = 1
INICIO_LINHAS_DADOS = 2


def fazer_consulta(driver: webdriver.Edge, codigo_pessoa: int,
                   st_habilitacao: str = "Todos") -> None:
    navegacao.entrar_frame_principal(driver)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "prc_cd_pessoa"))
    )
    try:
        Select(driver.find_element(By.ID, "prc_st_habilitacao")) \
            .select_by_visible_text(st_habilitacao)
    except NoSuchElementException:
        print(f"  [AVISO] Opcao '{st_habilitacao}' nao encontrada em "
              f"prc_st_habilitacao. Mantendo valor padrao da pagina.")

    campo = driver.find_element(By.ID, "prc_cd_pessoa")
    campo.clear()
    campo.send_keys(str(codigo_pessoa))
    driver.find_element(By.ID, "prc_evento").click()
    time.sleep(2)


def capturar_resultados(driver: webdriver.Edge) -> list[dict]:
    tabelas = driver.find_elements(By.TAG_NAME, "table")
    if len(tabelas) <= INDICE_TABELA_DADOS:
        return []

    linhas = tabelas[INDICE_TABELA_DADOS].find_elements(By.TAG_NAME, "tr")
    resultados = []
    for linha in linhas[INICIO_LINHAS_DADOS:]:
        celulas = [c.text.strip() for c in linha.find_elements(By.TAG_NAME, "td")]
        if not any(celulas):
            continue
        resultados.append({
            "situacao":  celulas[0] if len(celulas) > 0 else "",
            "filial":    celulas[1] if len(celulas) > 1 else "",
            "codigo":    celulas[2] if len(celulas) > 2 else "",
            "pessoa":    celulas[3] if len(celulas) > 3 else "",
            "nome":      celulas[4] if len(celulas) > 4 else "",
            "cpf":       celulas[5] if len(celulas) > 5 else "",
            "telefone":  celulas[6] if len(celulas) > 6 else "",
        })
    return resultados


def voltar(driver: webdriver.Edge) -> None:
    try:
        driver.find_element(By.ID, "prc_voltar").click()
        time.sleep(1)
    except NoSuchElementException:
        pass
    navegacao.sair_frame(driver)
