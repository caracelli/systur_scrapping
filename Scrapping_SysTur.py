import sys
import subprocess
import ctypes

def garantir_dependencias():
    for pacote in ["selenium", "openpyxl"]:
        try:
            __import__(pacote.replace("-", "_"))
        except ImportError:
            print(f"[INFO] Instalando {pacote}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pacote, "-q"])

garantir_dependencias()

# ── Anti-hibernação (Windows) ──────────────────────────────────
ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000001

def impedir_hibernacao():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    print("[INFO] Hibernacao desativada durante a execucao.")

def restaurar_hibernacao():
    ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
    print("[INFO] Configuracao de hibernacao restaurada.")

# ──────────────────────────────────────────────────────────────
import sys
from pathlib import Path
import openpyxl

sys.path.insert(0, "src")
import sessao
import navegacao
import consulta as cons
import fila as fl
import saida as sa
from selenium.common.exceptions import WebDriverException

PASTA_ENTRADA = Path("entrada")

def ler_config() -> dict:
    import xml.etree.ElementTree as ET
    tree = ET.parse("config/config.xml")
    root = tree.getroot()
    return {
        "headless": root.findtext("headless", "true").strip().lower() == "true",
    }

CONFIG = ler_config()


def encontrar_excel() -> Path:
    arquivos = [
        f for f in PASTA_ENTRADA.iterdir()
        if f.suffix.lower() in (".xlsx", ".xls") and not f.name.startswith(".")
    ]
    if not arquivos:
        raise FileNotFoundError("Nenhum arquivo Excel encontrado na pasta entrada/")
    if len(arquivos) > 1:
        print(f"[AVISO] {len(arquivos)} arquivos encontrados. Usando: {arquivos[0].name}")
    return arquivos[0]


def validar_excel(path: Path) -> None:
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    for row in ws.iter_rows(min_row=1, max_row=3, values_only=True):
        if row[0] is not None and not isinstance(row[0], (int, float)):
            raise ValueError(
                f"Coluna A deve conter codigo_pessoa numerico.\n"
                f"Encontrado: '{row[0]}' em {path.name}"
            )


# ──────────────────────────────────────────────
# INICIO
# ──────────────────────────────────────────────
print("=" * 55)
print("  SYSTUR SCRAPPER — Consulta de Vendedores")
print("=" * 55)

impedir_hibernacao()

try:
    excel_entrada = encontrar_excel()
    print(f"[INFO] Arquivo de entrada: {excel_entrada.name}")
    validar_excel(excel_entrada)

    fila = fl.inicializar(str(excel_entrada))
    print(fl.resumo(fila))

    wb, ws, caminho_saida = sa.criar_arquivo()

    driver = sessao.abrir(headless=CONFIG["headless"])
    sessao.garantir_sessao(driver)
    print("[OK] Sessao ativa.\n")

    navegacao.ir_para_vendedores(driver)

    # ──────────────────────────────────────────────
    # LOOP PRINCIPAL
    # ──────────────────────────────────────────────
    item = fl.proximo(fila)
    while item:
        codigo = item["codigo_pessoa"]
        nome   = item["nome"]
        print(f"[FILA] {codigo} — {nome}")

        try:
            sessao.garantir_sessao(driver)
            cons.fazer_consulta(driver, codigo)
            resultados = cons.capturar_resultados(driver)

            if not resultados:
                print(f"  [INFO] Sem resultado. Seguindo...")
                fl.marcar_sem_resultado(fila, codigo)
            else:
                sa.adicionar_linhas(ws, codigo, nome, resultados)
                sa.salvar(wb, caminho_saida)
                fl.marcar_concluido(fila, codigo)
                print(f"  [OK] {len(resultados)} linha(s) salva(s).")

            cons.voltar(driver)

        except WebDriverException as e:
            fl.marcar_erro(fila, codigo, str(e)[:200])
            print(f"  [ERRO] {e.__class__.__name__}: {str(e)[:100]}")
            try:
                navegacao.ir_para_vendedores(driver)
            except Exception:
                pass

        print(f"  {fl.resumo(fila)}")
        item = fl.proximo(fila)

    # ──────────────────────────────────────────────
    # FINALIZACAO
    # ──────────────────────────────────────────────
    driver.quit()
    sa.salvar(wb, caminho_saida)

    print("\n" + "=" * 55)
    print("  CONCLUIDO")
    print(f"  Saida: {caminho_saida.name}")
    print(f"  {fl.resumo(fila)}")
    print("=" * 55)

finally:
    restaurar_hibernacao()
