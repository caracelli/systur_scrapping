import base64
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


def escrever_log(fila: dict, caminho_saida: Path, excel_entrada: Path) -> Path:
    PASTA_LOGS.mkdir(exist_ok=True)
    agora = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    caminho_log = PASTA_LOGS / f"execucao_{agora}.txt"

    linhas = [
        "=" * 60,
        f"  SYSTUR SCRAPPER — Log de Execucao",
        f"  Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        "=" * 60,
        f"Entrada : {excel_entrada.name}",
        f"Saida   : {caminho_saida.name}",
        "",
    ]

    total       = fila["total"]
    concluidos  = [i for i in fila["items"] if i["status"] == "concluido"]
    erros       = [i for i in fila["items"] if i["status"] == "erro"]
    sem_res     = [i for i in fila["items"] if i["status"] == "sem_resultado"]
    pendentes   = [i for i in fila["items"] if i["status"] == "pendente"]

    linhas += [
        "RESUMO",
        f"  Total       : {total}",
        f"  Concluidos  : {len(concluidos)}",
        f"  Sem resultado: {len(sem_res)}",
        f"  Erros       : {len(erros)}",
        f"  Pendentes   : {len(pendentes)}",
        "",
    ]

    if erros:
        linhas.append("ERROS")
        for item in erros:
            linhas.append(f"  [{item['codigo_pessoa']}] {item['nome']}")
            linhas.append(f"    Tentativas: {item['tentativas']}")
            linhas.append(f"    Erro: {item.get('erro', '')}")
        linhas.append("")

    if sem_res:
        linhas.append("SEM RESULTADO")
        for item in sem_res:
            linhas.append(f"  [{item['codigo_pessoa']}] {item['nome']}")
        linhas.append("")

    if pendentes:
        linhas.append("AINDA PENDENTES (execucao interrompida ou limite atingido)")
        for item in pendentes:
            linhas.append(f"  [{item['codigo_pessoa']}] {item['nome']}")
        linhas.append("")

    caminho_log.write_text("\n".join(linhas), encoding="utf-8")
    print(f"[LOG] Salvo em: {caminho_log.name}")
    return caminho_log


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
