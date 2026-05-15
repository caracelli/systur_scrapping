import json
import time
import openpyxl
from pathlib import Path
from datetime import datetime

FILA_PATH = Path("processamento/fila.json")
EXCEL_COLUNA_CODIGO = 0  # coluna A
EXCEL_COLUNA_NOME = 1    # coluna B
MAX_TENTATIVAS = 3
PAUSA_ENTRE_TENTATIVAS = 5  # segundos


def _salvar(fila: dict) -> None:
    FILA_PATH.write_text(json.dumps(fila, ensure_ascii=False, indent=2), encoding="utf-8")


def _build(excel_path: str) -> None:
    wb = openpyxl.load_workbook(excel_path)
    ws = wb.active
    items = []
    for row in ws.iter_rows(min_row=1, values_only=True):
        codigo = row[EXCEL_COLUNA_CODIGO]
        nome = row[EXCEL_COLUNA_NOME]
        if codigo is None:
            continue
        items.append({
            "codigo_pessoa": int(codigo),
            "nome": str(nome).strip() if nome else "",
            "status": "pendente",
            "tentativas": 0,
            "erro": None,
        })

    fila = {
        "criado_em": datetime.now().isoformat(),
        "total": len(items),
        "items": items,
    }
    FILA_PATH.parent.mkdir(parents=True, exist_ok=True)
    _salvar(fila)
    print(f"[FILA] Criada com {len(items)} itens.")


def inicializar(excel_path: str) -> dict:
    if FILA_PATH.exists():
        fila = json.loads(FILA_PATH.read_text(encoding="utf-8"))
        print(f"[FILA] Retomando. {resumo(fila)}")
    else:
        _build(excel_path)
        fila = json.loads(FILA_PATH.read_text(encoding="utf-8"))
    return fila


def proximo(fila: dict) -> dict | None:
    for item in fila["items"]:
        if item["status"] == "pendente":
            return item
    return None


def marcar_concluido(fila: dict, codigo_pessoa: int) -> None:
    for item in fila["items"]:
        if item["codigo_pessoa"] == codigo_pessoa:
            item["status"] = "concluido"
            item["erro"] = None
            break
    _salvar(fila)


def marcar_erro(fila: dict, codigo_pessoa: int, msg: str) -> None:
    for item in fila["items"]:
        if item["codigo_pessoa"] == codigo_pessoa:
            item["tentativas"] += 1
            item["erro"] = msg
            if item["tentativas"] < MAX_TENTATIVAS:
                # ainda tem tentativas — mantém pendente após pausa
                print(f"[FILA] Tentativa {item['tentativas']}/{MAX_TENTATIVAS} falhou para {codigo_pessoa}. Aguardando {PAUSA_ENTRE_TENTATIVAS}s...")
                time.sleep(PAUSA_ENTRE_TENTATIVAS)
                item["status"] = "pendente"
            else:
                item["status"] = "erro"
                print(f"[FILA] {codigo_pessoa} esgotou {MAX_TENTATIVAS} tentativas. Marcado como erro.")
            break
    _salvar(fila)


def marcar_sem_resultado(fila: dict, codigo_pessoa: int) -> None:
    for item in fila["items"]:
        if item["codigo_pessoa"] == codigo_pessoa:
            item["status"] = "sem_resultado"
            item["erro"] = None
            break
    _salvar(fila)


def recolocar_erros(fila: dict) -> int:
    """Recoloca itens com erro de volta para pendente (para nova tentativa)."""
    count = 0
    for item in fila["items"]:
        if item["status"] == "erro":
            item["status"] = "pendente"
            count += 1
    if count:
        _salvar(fila)
    return count


def resumo(fila: dict) -> str:
    total = fila["total"]
    concluidos = sum(1 for i in fila["items"] if i["status"] == "concluido")
    erros = sum(1 for i in fila["items"] if i["status"] == "erro")
    pendentes = sum(1 for i in fila["items"] if i["status"] == "pendente")
    sem_resultado = sum(1 for i in fila["items"] if i["status"] == "sem_resultado")
    return f"Total: {total} | Concluídos: {concluidos} | Pendentes: {pendentes} | Sem resultado: {sem_resultado} | Erros: {erros}"
