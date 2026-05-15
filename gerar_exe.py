"""
Gera SysTur_Scrapper.exe na pasta dist/

Uso: python gerar_exe.py

Estrutura necessaria ao lado do .exe:
  config/config.xml
  config/credenciais.xml
  entrada/  (arquivo Excel)
  saida/    (criada automaticamente)
"""
import subprocess
import sys
from pathlib import Path


def garantir_pyinstaller():
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("[INFO] PyInstaller nao encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "-q"])
        print("[OK] PyInstaller instalado.")


def gerar():
    raiz = Path(__file__).resolve().parent
    main_script = raiz / "Scrapping_SysTur.py"
    src_dir = raiz / "src"
    dist_dir = raiz / "dist"
    build_dir = raiz / "_build_temp"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "SysTur_Scrapper",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--noconfirm",
        "--paths", str(src_dir),
        "--hidden-import", "sessao",
        "--hidden-import", "navegacao",
        "--hidden-import", "consulta",
        "--hidden-import", "fila",
        "--hidden-import", "saida",
        "--hidden-import", "selenium",
        "--hidden-import", "selenium.webdriver.edge.options",
        "--hidden-import", "selenium.webdriver.support.expected_conditions",
        "--hidden-import", "openpyxl",
        "--hidden-import", "openpyxl.cell._writer",
        str(main_script),
    ]

    print("=== Build SysTur Scrapper ===")
    print(f"Script: {main_script.name}")
    print(f"Saida:  {dist_dir}\n")

    resultado = subprocess.run(cmd, cwd=str(raiz))

    if resultado.returncode == 0:
        exe = dist_dir / "SysTur_Scrapper.exe"
        print(f"\n[OK] Executavel gerado: {exe}")
        print("\nLembre-se: mantenha ao lado do .exe as pastas:")
        print("  config/   entrada/   saida/   processamento/")
    else:
        print("\n[FALHA] Build falhou. Verifique os erros acima.")
        sys.exit(1)


if __name__ == "__main__":
    garantir_pyinstaller()
    gerar()
