# ============================================
# Script de Inicialização do Bot - Windows
# Inicia o bot com verificações de ambiente
# ============================================

param(
    [switch]$Dev,
    [switch]$Verbose,
    [switch]$CheckOnly
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🤖 Iniciando Bot YouTube Discord" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Detectar diretório do projeto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptPath

# Mudar para diretório do projeto
Set-Location $projectRoot
Write-Host "📁 Diretório: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# ============================================
# 1. VERIFICAR PYTHON
# ============================================

Write-Host "🔍 Verificando Python..." -ForegroundColor Cyan

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match 'Python (\d+)\.(\d+)\.(\d+)') {
        $major = [int]$matches[1]
        $minor = [int]$matches[2]

        if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 10)) {
            Write-Host "❌ Python $pythonVersion encontrado, mas é necessário Python 3.10+" -ForegroundColor Red
            Write-Host "   Baixe em: https://www.python.org/downloads/" -ForegroundColor Yellow
            exit 1
        }

        Write-Host "✅ Python $pythonVersion" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Python não encontrado!" -ForegroundColor Red
    Write-Host "   Instale Python 3.10+: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# ============================================
# 2. VERIFICAR/CRIAR AMBIENTE VIRTUAL
# ============================================

Write-Host "🔍 Verificando ambiente virtual..." -ForegroundColor Cyan

$venvPath = Join-Path $projectRoot "venv"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

if (-not (Test-Path $venvPath)) {
    Write-Host "⚠️  Ambiente virtual não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv venv

    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Falha ao criar ambiente virtual!" -ForegroundColor Red
        exit 1
    }

    Write-Host "✅ Ambiente virtual criado" -ForegroundColor Green
} else {
    Write-Host "✅ Ambiente virtual encontrado" -ForegroundColor Green
}

# Ativar ambiente virtual
Write-Host "🔄 Ativando ambiente virtual..." -ForegroundColor Cyan
& $venvActivate

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Falha ao ativar ambiente virtual!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Ambiente virtual ativado" -ForegroundColor Green

# ============================================
# 3. VERIFICAR DEPENDÊNCIAS
# ============================================

Write-Host "🔍 Verificando dependências..." -ForegroundColor Cyan

$requirementsFile = Join-Path $projectRoot "requirements.txt"

if (-not (Test-Path $requirementsFile)) {
    Write-Host "❌ requirements.txt não encontrado!" -ForegroundColor Red
    exit 1
}

# Verificar se dependências estão instaladas
try {
    $installedPackages = pip list --format=freeze 2>&1
    $requiredPackages = Get-Content $requirementsFile | Where-Object { $_ -and $_ -notmatch '^\s*#' }

    $missingPackages = @()
    foreach ($package in $requiredPackages) {
        $packageName = ($package -split '==|>=|<=|>|<')[0].Trim()
        if ($installedPackages -notmatch "^$packageName==") {
            $missingPackages += $package
        }
    }

    if ($missingPackages.Count -gt 0) {
        Write-Host "⚠️  Dependências faltando. Instalando..." -ForegroundColor Yellow
        pip install -r $requirementsFile

        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Falha ao instalar dependências!" -ForegroundColor Red
            exit 1
        }

        Write-Host "✅ Dependências instaladas" -ForegroundColor Green
    } else {
        Write-Host "✅ Todas dependências instaladas" -ForegroundColor Green
    }

} catch {
    Write-Host "⚠️  Erro ao verificar dependências. Instalando todas..." -ForegroundColor Yellow
    pip install -r $requirementsFile
}

# ============================================
# 4. VERIFICAR CONFIGURAÇÃO
# ============================================

Write-Host "🔍 Verificando configuração..." -ForegroundColor Cyan

# Verificar .env
$envFile = Join-Path $projectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠️  Arquivo .env não encontrado!" -ForegroundColor Yellow

    $envExample = Join-Path $projectRoot ".env.example"
    if (Test-Path $envExample) {
        Write-Host "   Copiando .env.example para .env..." -ForegroundColor Yellow
        Copy-Item $envExample $envFile
        Write-Host "✅ Arquivo .env criado" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANTE: Edite .env com suas credenciais!" -ForegroundColor Red
        Write-Host "   notepad .env" -ForegroundColor Cyan
        Write-Host ""
        $edit = Read-Host "Deseja editar agora? (S/N)"
        if ($edit -match '^[Ss]$') {
            notepad $envFile
            Write-Host ""
            Write-Host "Pressione qualquer tecla após salvar o .env..." -ForegroundColor Yellow
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        } else {
            Write-Host ""
            Write-Host "⚠️  Configure o .env antes de iniciar o bot!" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "❌ .env.example não encontrado!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Arquivo .env encontrado" -ForegroundColor Green
}

# Verificar token OAuth2 (opcional)
$tokenFile = Join-Path $projectRoot "config\token.json"
if (-not (Test-Path $tokenFile)) {
    Write-Host "⚠️  Token OAuth2 não encontrado (opcional)" -ForegroundColor Yellow
    Write-Host "   O bot tentará usar API Key ou cookies como fallback" -ForegroundColor Yellow
} else {
    Write-Host "✅ Token OAuth2 encontrado" -ForegroundColor Green
}

# Verificar cookies (opcional)
$cookiesFile = Join-Path $projectRoot "cookies.txt"
if (-not (Test-Path $cookiesFile)) {
    Write-Host "⚠️  Cookies não encontrados (recomendado)" -ForegroundColor Yellow
    Write-Host "   Execute: .\scripts\extract_cookies.ps1" -ForegroundColor Cyan
} else {
    $cookieAge = ((Get-Date) - (Get-Item $cookiesFile).LastWriteTime).Days
    if ($cookieAge -gt 90) {
        Write-Host "⚠️  Cookies com $cookieAge dias (re-extrair recomendado)" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Cookies encontrados ($cookieAge dias)" -ForegroundColor Green
    }
}

Write-Host ""

# ============================================
# 5. VERIFICAÇÃO FINAL
# ============================================

if ($CheckOnly) {
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "✅ Verificação Concluída!" -ForegroundColor Green
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Ambiente está pronto para rodar o bot." -ForegroundColor Green
    Write-Host "Execute sem -CheckOnly para iniciar." -ForegroundColor Yellow
    Write-Host ""
    exit 0
}

# ============================================
# 6. INICIAR BOT
# ============================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🚀 Iniciando Bot..." -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Definir variáveis de ambiente adicionais
if ($Dev) {
    $env:LOG_LEVEL = "DEBUG"
    Write-Host "🐛 Modo Desenvolvedor Ativado (LOG_LEVEL=DEBUG)" -ForegroundColor Yellow
    Write-Host ""
}

if ($Verbose) {
    $env:VERBOSE = "true"
    Write-Host "📢 Modo Verbose Ativado" -ForegroundColor Yellow
    Write-Host ""
}

# Iniciar main.py
$mainFile = Join-Path $projectRoot "main.py"

if (-not (Test-Path $mainFile)) {
    Write-Host "❌ main.py não encontrado!" -ForegroundColor Red
    exit 1
}

try {
    Write-Host "▶️  Executando: python main.py" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Para parar o bot: Ctrl+C" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host ""

    python $mainFile

} catch {
    Write-Host ""
    Write-Host "❌ Erro ao executar bot!" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Bot Encerrado" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
