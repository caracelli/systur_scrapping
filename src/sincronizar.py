import subprocess
import sys
from datetime import datetime
from pathlib import Path

PASTA_LOGS = Path("logs")


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


def sincronizar_git(caminho_log: Path) -> None:
    print("[GIT] Sincronizando log...")
    try:
        subprocess.run(["git", "add", str(caminho_log)], check=True)
        msg = f"log: execucao {caminho_log.stem}"
        subprocess.run(["git", "commit", "-m", msg], check=True)
        subprocess.run(["git", "push"], check=True)
        print("[GIT] Log sincronizado com sucesso.")
    except Exception as e:
        # Em maquina sem git/sem repositorio (ex.: execucao do exe no cliente)
        # isso e esperado. O log ja foi gravado localmente em logs/ — basta
        # enviar esse arquivo manualmente.
        print(f"[GIT] Sincronizacao ignorada ({e.__class__.__name__}): {e}")
        print(f"[GIT] O log esta salvo localmente em: {caminho_log}")
