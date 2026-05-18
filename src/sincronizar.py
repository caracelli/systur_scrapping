import csv
from datetime import datetime
from pathlib import Path

PASTA_LOGS = Path("logs")

CSV_HEADER = ["Data Processamento", "codigo_pessoa", "nome", "status", "detalhe"]


def iniciar_csv() -> Path:
    """Cria o CSV de processamento (logs/processamento_<ts>.csv) com cabecalho.

    Uma linha e gravada por item durante o loop (igual ao terminal).
    Separador ';' e BOM utf-8 -> abre certo no Excel pt-BR com acentos.
    O BOM e escrito so na criacao; os appends usam utf-8 puro para nao
    inserir BOM no meio do arquivo.
    """
    PASTA_LOGS.mkdir(exist_ok=True)
    agora = datetime.now().strftime("%d%m%Y_%H%M%S")
    caminho = PASTA_LOGS / f"processamento_{agora}.csv"
    with caminho.open("w", encoding="utf-8-sig", newline="") as f:
        csv.writer(f, delimiter=";").writerow(CSV_HEADER)
    print(f"[LOG] CSV de processamento: {caminho.name}")
    return caminho


def registrar(caminho_csv: Path, codigo, nome: str,
              status: str, detalhe: str) -> None:
    """Acrescenta uma linha ao CSV e fecha o arquivo (sobrevive a queda)."""
    linha = [
        datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        codigo, nome, status, detalhe,
    ]
    with caminho_csv.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f, delimiter=";").writerow(linha)
