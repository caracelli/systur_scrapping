import base64
import csv
import json
import subprocess
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

PASTA_LOGS = Path("logs")

# Repositorio fixo onde os logs sao publicados quando a maquina nao e um repo git
GITHUB_OWNER  = "caracelli"
GITHUB_REPO   = "systur_scrapping"
GITHUB_BRANCH = "master"
CONFIG_PATH   = Path("config/config.xml")


CSV_HEADER = ["data_hora", "codigo_pessoa", "nome", "status", "detalhe"]


def iniciar_csv() -> Path:
    """Cria o CSV de processamento (logs/processamento_<ts>.csv) com cabecalho.

    Uma linha e gravada por item durante o loop (igual ao terminal).
    Separador ';' e BOM utf-8 -> abre certo no Excel pt-BR com acentos.
    O BOM e escrito so na criacao; os appends usam utf-8 puro para nao
    inserir BOM no meio do arquivo.
    """
    PASTA_LOGS.mkdir(exist_ok=True)
    agora = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
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


def _ler_github_token() -> str:
    try:
        root = ET.parse(CONFIG_PATH).getroot()
        return (root.findtext("github_token", "") or "").strip()
    except Exception:
        return ""


def enviar_via_api(caminho_log: Path) -> bool:
    """Publica o log no repositorio via API do GitHub (sem precisar de git).

    Usado quando a maquina que roda o exe nao e um repositorio git.
    Cada log tem nome unico (timestamp), entao nunca sobrescreve — nao
    precisa buscar o sha de um arquivo existente.
    """
    token = _ler_github_token()
    if not token:
        print("[API] github_token vazio no config.xml — envio automatico desativado.")
        print(f"[API] Envie manualmente o arquivo: {caminho_log}")
        return False

    repo_path = f"logs/{caminho_log.name}"
    url = (
        f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"
        f"/contents/{repo_path}"
    )
    conteudo_b64 = base64.b64encode(caminho_log.read_bytes()).decode("ascii")
    corpo = json.dumps({
        "message": f"log: execucao {caminho_log.stem} (via exe cliente)",
        "content": conteudo_b64,
        "branch": GITHUB_BRANCH,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=corpo, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "systur-scrapper")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status in (200, 201):
                print(f"[API] Log publicado no GitHub: {repo_path}")
                return True
            print(f"[API] Resposta inesperada: HTTP {resp.status}")
            return False
    except urllib.error.HTTPError as e:
        detalhe = e.read().decode("utf-8", "replace")[:300]
        print(f"[API] Falha HTTP {e.code} ao publicar log: {detalhe}")
    except Exception as e:
        print(f"[API] Falha ao publicar log ({e.__class__.__name__}): {e}")
    print(f"[API] Envie manualmente o arquivo: {caminho_log}")
    return False


def sincronizar_git(caminho_log: Path) -> None:
    print("[GIT] Sincronizando log...")
    try:
        subprocess.run(["git", "add", str(caminho_log)], check=True)
        msg = f"log: execucao {caminho_log.stem}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[GIT] Log sincronizado com sucesso (git push).")
        return
    except Exception as e:
        # Maquina sem git/sem repositorio (ex.: exe no cliente).
        # Cai para o envio via API do GitHub.
        print(f"[GIT] git push indisponivel ({e.__class__.__name__}). "
              f"Tentando via API do GitHub...")

    enviar_via_api(caminho_log)
