import sys
import subprocess
import ctypes

def garantir_dependencias():
    # Em exe congelado (PyInstaller) as dependencias ja estao embutidas e
    # sys.executable e o proprio exe — chamar "pip" aqui faria o exe se
    # re-executar em loop infinito. Entao nao faz nada quando frozen.
    if getattr(sys, "frozen", False):
        return
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
import sincronizar as sync
from selenium.common.exceptions import WebDriverException

PASTA_ENTRADA = Path("entrada")

def ler_config() -> dict:
    import xml.etree.ElementTree as ET
    tree = ET.parse("config/config.xml")
    root = tree.getroot()
    return {
        "headless": root.findtext("headless", "true").strip().lower() == "true",
        "limite": int(root.findtext("limite", "0").strip()),
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


def aguardar_vpn() -> None:
    """Garante conexao com o SYSTUR antes de abrir o navegador.

    O SYSTUR so e acessivel via VPN da CVC. Se nao houver conexao,
    pede ao usuario para conectar a VPN e tenta novamente.
    """
    if sessao.verificar_conexao():
        print("[OK] Conexao com o SYSTUR confirmada.")
        return

    print("\n" + "!" * 55)
    print("  SEM CONEXAO COM O SYSTUR (systur.cvc.com.br)")
    print("  O sistema so e acessivel pela VPN da CVC.")
    print("!" * 55)
    while not sessao.verificar_conexao():
        resp = input(
            "\n[VPN] Conecte-se a VPN e pressione ENTER para tentar "
            "novamente (ou digite 'sair' para cancelar): "
        ).strip().lower()
        if resp == "sair":
            print("[VPN] Execucao cancelada pelo usuario.")
            restaurar_hibernacao()
            sys.exit(1)
        if sessao.verificar_conexao():
            break
        print("[VPN] Ainda sem conexao com o SYSTUR...")
    print("[OK] Conexao com o SYSTUR confirmada.")


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

    aguardar_vpn()

    driver = sessao.abrir(headless=CONFIG["headless"])
    sessao.garantir_sessao(driver)
    print("[OK] Sessao ativa.\n")

    navegacao.ir_para_vendedores(driver)

    # ──────────────────────────────────────────────
    # LOOP PRINCIPAL
    # ──────────────────────────────────────────────
    limite = CONFIG["limite"]
    if limite:
        print(f"[INFO] Modo teste: processando ate {limite} item(ns).\n")

    caminho_log = sync.iniciar_csv()

    processados = 0
    item = fl.proximo(fila)
    while item and (not limite or processados < limite):
        codigo = item["codigo_pessoa"]
        nome   = item["nome"]
        print(f"[FILA] {codigo} — {nome}")

        try:
            sessao.garantir_sessao(driver)
            cons.fazer_consulta(driver, codigo)
            resultados = cons.capturar_resultados(driver)

            if not resultados:
                print("  [INFO] Nao existem dados para este codigo. Seguindo...")
                fl.marcar_sem_resultado(fila, codigo)
                sync.registrar(caminho_log, codigo, nome,
                               "sem_resultado", "Não existem dados")
            else:
                sa.adicionar_linhas(ws, codigo, nome, resultados)
                sa.salvar(wb, caminho_saida)
                fl.marcar_concluido(fila, codigo)
                print(f"  [OK] {len(resultados)} linha(s) salva(s).")
                sync.registrar(caminho_log, codigo, nome, "concluido",
                               f"{len(resultados)} linha(s) salva(s)")

            cons.voltar(driver)

        except WebDriverException as e:
            fl.marcar_erro(fila, codigo, str(e)[:200])
            print(f"  [ERRO] Erro - {e.__class__.__name__}: {str(e)[:100]}")
            sync.registrar(caminho_log, codigo, nome, "erro",
                           f"Erro - {e.__class__.__name__}: {str(e)[:200]}")
            try:
                navegacao.ir_para_vendedores(driver)
            except Exception:
                pass

        processados += 1
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

    print(f"  Log CSV: {caminho_log}")

finally:
    restaurar_hibernacao()
