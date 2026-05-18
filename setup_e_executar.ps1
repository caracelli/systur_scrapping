<#
  setup_e_executar.ps1
  Prepara e executa o SYSTUR Scrapper na maquina que roda o .py.

  Ordem:
    1. Detecta um Python utilizavel (preferindo o launcher 'py').
    2. Se nao houver, instala automaticamente:
         winget  ->  choco  ->  instalador oficial silencioso.
    3. git pull (nao fatal se falhar) para pegar o codigo mais novo.
    4. Executa: python Scrapping_SysTur.py
       (o proprio script ja faz pip install de selenium/openpyxl).

  Uso:
    powershell -ExecutionPolicy Bypass -File setup_e_executar.ps1
    powershell -ExecutionPolicy Bypass -File setup_e_executar.ps1 -SemPull
    powershell -ExecutionPolicy Bypass -File setup_e_executar.ps1 -SoSetup
#>
[CmdletBinding()]
param(
    [switch]$SemPull,
    [switch]$SoSetup
)

$ErrorActionPreference = "Stop"
$Raiz     = $PSScriptRoot
$ScriptPy = Join-Path $Raiz "Scrapping_SysTur.py"
$PyVersao = "3.12"
$PyPatch  = "3.12.10"
$WingetId = "Python.Python.$PyVersao"

function Info($m)  { Write-Host "[SETUP] $m"  -ForegroundColor Cyan }
function Ok($m)    { Write-Host "[OK] $m"     -ForegroundColor Green }
function Aviso($m) { Write-Host "[AVISO] $m"  -ForegroundColor Yellow }
function Erro($m)  { Write-Host "[ERRO] $m"   -ForegroundColor Red }

function Atualizar-Path {
    $m = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $u = [Environment]::GetEnvironmentVariable("Path", "User")
    $partes = @()
    if ($m) { $partes += $m }
    if ($u) { $partes += $u }
    $env:Path = $partes -join ";"
}

function Get-PythonCmd {
    # Retorna o comando Python como string ('py -3', 'python' ...) ou ''.
    # Ignora o stub da Microsoft Store (WindowsApps) que nao executa.
    $candidatos = @("py -3", "python", "python3")
    foreach ($c in $candidatos) {
        $exe = $c.Split(" ")[0]
        $cmd = Get-Command $exe -ErrorAction SilentlyContinue
        if ($null -eq $cmd) { continue }
        if ($cmd.Source -and $cmd.Source -like "*\WindowsApps\*") { continue }
        $teste = cmd /c "$c --version" 2>$null
        if ($LASTEXITCODE -eq 0 -and $teste) { return $c }
    }
    return ""
}

# 1/2. Garante Python
$py = Get-PythonCmd
if ($py -ne "") {
    Ok "Python encontrado: $py"
} else {
    Aviso "Python nao encontrado. Instalando automaticamente..."
    $instalou = $false

    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Info "Instalando via winget ($WingetId)..."
        winget install -e --id $WingetId --silent --accept-source-agreements --accept-package-agreements
        Atualizar-Path
        if ((Get-PythonCmd) -ne "") { $instalou = $true }
    }

    if ((-not $instalou) -and (Get-Command choco -ErrorAction SilentlyContinue)) {
        Info "Instalando via Chocolatey..."
        choco install python -y
        Atualizar-Path
        if ((Get-PythonCmd) -ne "") { $instalou = $true }
    }

    if (-not $instalou) {
        Info "Baixando o instalador oficial do Python $PyPatch..."
        $url = "https://www.python.org/ftp/python/$PyPatch/python-$PyPatch-amd64.exe"
        $tmp = Join-Path $env:TEMP "python-installer.exe"
        try {
            Invoke-WebRequest -Uri $url -OutFile $tmp -UseBasicParsing
            Info "Executando instalador silencioso (PATH + py launcher)..."
            $argInst = "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1"
            Start-Process -FilePath $tmp -Wait -ArgumentList $argInst
            Atualizar-Path
            if ((Get-PythonCmd) -ne "") { $instalou = $true }
        } catch {
            Erro ("Falha ao baixar/instalar o Python: " + $_.Exception.Message)
        } finally {
            if (Test-Path $tmp) { Remove-Item $tmp -Force -ErrorAction SilentlyContinue }
        }
    }

    if (-not $instalou) {
        Erro "Nao foi possivel instalar o Python automaticamente."
        Erro "Instale manualmente em https://www.python.org/downloads/ (marque 'Add to PATH') e rode de novo."
        exit 1
    }
    $py = Get-PythonCmd
    Ok "Python instalado: $py"
}

# 3. Atualiza o repositorio
if (-not $SemPull) {
    if (Test-Path (Join-Path $Raiz ".git")) {
        Info "git pull..."
        git -C $Raiz pull --ff-only
        if ($LASTEXITCODE -ne 0) {
            Aviso "git pull falhou. Seguindo com o codigo local atual."
        }
    } else {
        Aviso "Pasta nao e um repositorio git. Pulando git pull."
    }
}

if ($SoSetup) {
    Ok "Setup concluido (Python pronto). -SoSetup ativo: nao vou executar o scraper."
    exit 0
}

# 4. Executa o scraper
if (-not (Test-Path $ScriptPy)) {
    Erro "Script nao encontrado: $ScriptPy"
    exit 1
}
Info "Executando: $py Scrapping_SysTur.py"
Push-Location $Raiz
try {
    cmd /c "$py `"$ScriptPy`""
    $rc = $LASTEXITCODE
} finally {
    Pop-Location
}
if ($rc -eq 0) {
    Ok "Execucao finalizada."
} else {
    Erro "O scraper terminou com codigo $rc. Veja o log na pasta logs."
}
exit $rc
