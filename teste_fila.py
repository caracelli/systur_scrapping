import sys
sys.path.insert(0, "src")

import fila

EXCEL = "entrada/Email Franqueadosver.xlsx"

fila_atual = fila.inicializar(EXCEL)
print(fila.resumo(fila_atual))
print()

# Mostra os 5 primeiros itens
print("Primeiros 5 itens da fila:")
for item in fila_atual["items"][:5]:
    print(f"  {item['codigo_pessoa']} — {item['nome']} [{item['status']}]")
