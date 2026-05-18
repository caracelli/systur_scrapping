"""
Gera SysTur_Scrapper.exe e monta o pacote de distribuicao para teste.

Uso: python gerar_exe.py

Estrutura gerada em dist/SysTur_Scrapper/  (e compactada em dist/SysTur_Scrapper.zip):

  SysTur_Scrapper/            <- pasta raiz
  ├── SysTur_Scrapper.exe     <- executavel
  ├── config/                 <- config.xml, credenciais.xml, xpaths.xml
  ├── entrada/                <- Excel com os codigos_pessoa
  └── saida/                  <- vazia (Excel de saida gerado aqui)
"""
import shutil
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


def gerar(raiz: Path, dist_dir: Path) -> Path:
    main_script = raiz / "Scrapping_SysTur.py"
    src_dir = raiz / "src"
    build_dir = raiz / "_build_temp"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "SysTur_Scrapper",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        "--noconfirm",
        "--paths", str(src_dir),
        # Modulos locais de src/ (importados via sys.path em runtime,
        # invisiveis para a analise estatica do PyInstaller)
        "--hidden-import", "sessao",
        "--hidden-import", "navegacao",
        "--hidden-import", "consulta",
        "--hidden-import", "fila",
        "--hidden-import", "saida",
        "--hidden-import", "sincronizar",
        # selenium/openpyxl: coletar TUDO (submodulos + dados + metadados).
        # collect-all garante que o exe rode em maquina sem Python/pip.
        "--collect-all", "selenium",
        "--collect-all", "openpyxl",
        "--copy-metadata", "selenium",
        "--copy-metadata", "trio",
        "--copy-metadata", "trio-websocket",
        str(main_script),
    ]

    print("=== Build SysTur Scrapper ===")
    print(f"Script: {main_script.name}")
    print(f"Saida:  {dist_dir}\n")

    resultado = subprocess.run(cmd, cwd=str(raiz))
    if resultado.returncode != 0:
        print("\n[FALHA] Build falhou. Verifique os erros acima.")
        sys.exit(1)

    exe = dist_dir / "SysTur_Scrapper.exe"
    print(f"\n[OK] Executavel gerado: {exe}")
    return exe


def empacotar(raiz: Path, dist_dir: Path, exe: Path) -> Path:
    """Monta dist/SysTur_Scrapper/ com a estrutura raiz + exe + subpastas."""
    pacote = dist_dir / "SysTur_Scrapper"
    if pacote.exists():
        shutil.rmtree(pacote)
    pacote.mkdir(parents=True)

    # Executavel na raiz do pacote
    shutil.copy2(exe, pacote / exe.name)

    # README.txt na raiz do pacote (passo a passo do usuario)
    readme = raiz / "README.txt"
    if readme.exists():
        shutil.copy2(readme, pacote / readme.name)

    # config/  -> todos os XML. credenciais.xml vai com usuario/senha
    # EM BRANCO (o usuario preenche na maquina dele).
    destino_config = pacote / "config"
    destino_config.mkdir()
    CRED_VAZIA = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<credenciais>\n"
        "  <usuario></usuario>\n"
        "  <senha></senha>\n"
        "</credenciais>\n"
    )
    for arq in (raiz / "config").glob("*.xml"):
        if arq.name.lower() == "credenciais.xml":
            (destino_config / arq.name).write_text(CRED_VAZIA, encoding="utf-8")
        else:
            shutil.copy2(arq, destino_config / arq.name)

    # entrada/ -> Excel(s) de entrada
    destino_entrada = pacote / "entrada"
    destino_entrada.mkdir()
    for arq in (raiz / "entrada").iterdir():
        if arq.suffix.lower() in (".xlsx", ".xls") and not arq.name.startswith("."):
            shutil.copy2(arq, destino_entrada / arq.name)

    # saida/ -> vazia (com aviso para nao se perder no zip)
    destino_saida = pacote / "saida"
    destino_saida.mkdir()
    (destino_saida / "LEIA-ME.txt").write_text(
        "Os arquivos vendedores_*.xlsx serao gerados automaticamente nesta pasta.\n",
        encoding="utf-8",
    )

    print(f"[OK] Pacote montado: {pacote}")
    return pacote


def zipar(dist_dir: Path, pacote: Path) -> Path:
    base = dist_dir / "SysTur_Scrapper"
    zip_path = Path(shutil.make_archive(str(base), "zip", root_dir=str(dist_dir), base_dir=pacote.name))
    print(f"[OK] Pacote compactado: {zip_path}")
    return zip_path


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parent
    dist_dir = raiz / "dist"

    garantir_pyinstaller()
    exe = gerar(raiz, dist_dir)
    pacote = empacotar(raiz, dist_dir, exe)
    zip_path = zipar(dist_dir, pacote)

    print("\n" + "=" * 55)
    print("  PRONTO PARA TESTE")
    print(f"  Pasta : {pacote}")
    print(f"  Zip   : {zip_path}")
    print("=" * 55)
    print("\nEstrutura do pacote:")
    print("  SysTur_Scrapper/")
    print("    |- SysTur_Scrapper.exe")
    print("    |- config/   (config.xml, credenciais.xml, xpaths.xml)")
    print("    |- entrada/  (Excel com os codigos)")
    print("    |- saida/    (Excel de saida gerado aqui)")
