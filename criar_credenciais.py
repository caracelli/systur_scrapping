from pathlib import Path

CRED_PATH = Path("credenciais.xml")

if CRED_PATH.exists():
    resp = input("credenciais.xml ja existe. Deseja sobrescrever? (s/n): ").strip().lower()
    if resp != "s":
        print("Cancelado.")
        exit()

usuario = input("Usuario: ").strip()
senha = input("Senha: ").strip()

CRED_PATH.write_text(
    f'<?xml version="1.0" encoding="UTF-8"?>\n'
    f'<credenciais>\n'
    f'  <usuario>{usuario}</usuario>\n'
    f'  <senha>{senha}</senha>\n'
    f'</credenciais>\n',
    encoding="utf-8"
)

print(f"[OK] credenciais.xml criado.")
