# ============================================
# Script de Exportação de Cookies do YouTube
# Guia interativo via extensão do navegador
# ============================================
#
# NOTA: Devido a limitações do Chrome/yt-dlp com DPAPI,
# este script usa extensão do navegador (método mais confiável)

param(
    [string]$OutputFile = "cookies.txt",
    [switch]$OpenBrowser
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🍪 Exportador de Cookies do YouTube" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Detectar navegador padrão
$defaultBrowser = "Chrome"
$browserDetected = $false

if (Test-Path "$env:LOCALAPPDATA\Google\Chrome\User Data") {
    $defaultBrowser = "Chrome"
    $browserDetected = $true
}

if (Test-Path "$env:LOCALAPPDATA\Microsoft\Edge\User Data") {
    $defaultBrowser = "Edge"
    $browserDetected = $true
}

if ($browserDetected) {
    Write-Host "🌐 Navegador detectado: $defaultBrowser" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Navegador não detectado automaticamente" -ForegroundColor Yellow
    $defaultBrowser = "Chrome"
}

Write-Host ""

# URLs das extensões
$extensionUrls = @{
    "Chrome"  = "https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
    "Edge"    = "https://microsoftedge.microsoft.com/addons/detail/get-cookiestxt-locally/eoaohkdcdjimfbmiaamnmgjiigkgocla"
    "Firefox" = "https://addons.mozilla.org/firefox/addon/cookies-txt/"
}

# Alternativas para Chrome
$chromeAlternatives = @(
    "https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc",
    "https://chromewebstore.google.com/detail/cookies-txt/cclelndahbckbenkjhflpdbgdldlbecc",
    "https://chrome.google.com/webstore/search/cookies%20txt"
)

# Guia interativo
Write-Host "📋 GUIA DE EXPORTAÇÃO DE COOKIES" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Método automático via yt-dlp está com problemas no Windows." -ForegroundColor Yellow
Write-Host "   Usaremos extensão do navegador (mais confiável)." -ForegroundColor White
Write-Host ""

# Passo 1: Instalar extensão
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "PASSO 1: Instalar Extensão" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📦 Extensão: 'Get cookies.txt LOCALLY'" -ForegroundColor White
Write-Host ""

if ($defaultBrowser -eq "Chrome") {
    Write-Host "🔗 OPÇÕES DE INSTALAÇÃO PARA CHROME:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Opção 1 (Recomendada):" -ForegroundColor White
    Write-Host "   $($chromeAlternatives[0])" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Opção 2 (Se opção 1 não funcionar):" -ForegroundColor White
    Write-Host "   $($chromeAlternatives[1])" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Opção 3 (Buscar manualmente):" -ForegroundColor White
    Write-Host "   $($chromeAlternatives[2])" -ForegroundColor Green
    Write-Host "   (Busque por: 'get cookies.txt locally')" -ForegroundColor Cyan
}
else {
    Write-Host "🔗 Link: " -NoNewline -ForegroundColor White
    Write-Host "$($extensionUrls[$defaultBrowser])" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Ações:" -ForegroundColor White
Write-Host "  1. Clique em um dos links acima" -ForegroundColor Yellow
Write-Host "  2. Clique em 'Adicionar ao $defaultBrowser' (botão azul)" -ForegroundColor Yellow
Write-Host "  3. Confirme a instalação no popup" -ForegroundColor Yellow
Write-Host ""

if ($OpenBrowser) {
    Write-Host "🌐 Abrindo opção 1 automaticamente..." -ForegroundColor Cyan
    if ($defaultBrowser -eq "Chrome") {
        Start-Process $chromeAlternatives[0]
    }
    else {
        Start-Process $extensionUrls[$defaultBrowser]
    }
    Start-Sleep -Seconds 2
}

Write-Host "💡 Se a página não carregar:" -ForegroundColor Cyan
Write-Host "   • Tente as outras opções acima" -ForegroundColor White
Write-Host "   • Ou busque manualmente: 'get cookies.txt locally' na Chrome Web Store" -ForegroundColor White
Write-Host ""

$response = Read-Host "Pressione ENTER quando a extensão estiver instalada (ou '1', '2', '3' para abrir opções)"

if ($response -match '^1$') {
    Start-Process $chromeAlternatives[0]
    Read-Host "Pressione ENTER quando a extensão estiver instalada"
}
elseif ($response -match '^2$') {
    Start-Process $chromeAlternatives[1]
    Read-Host "Pressione ENTER quando a extensão estiver instalada"
}
elseif ($response -match '^3$') {
    Start-Process $chromeAlternatives[2]
    Read-Host "Pressione ENTER quando a extensão estiver instalada"
}

# Passo 2: Fazer login no YouTube
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "PASSO 2: Fazer Login no YouTube" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Ações:" -ForegroundColor White
Write-Host "  1. Abra: https://youtube.com" -ForegroundColor Yellow
Write-Host "  2. Faça LOGIN com sua conta Google" -ForegroundColor Yellow
Write-Host "  3. Acesse qualquer vídeo (garante cookies ativos)" -ForegroundColor Yellow
Write-Host ""

if ($OpenBrowser) {
    Start-Process "https://youtube.com"
}

$response = Read-Host "Pressione ENTER quando estiver logado no YouTube (ou 'B' para abrir)"
if ($response -match '^[Bb]$') {
    Start-Process "https://youtube.com"
    Read-Host "Pressione ENTER quando estiver logado no YouTube"
}

# Passo 3: Exportar cookies
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "PASSO 3: Exportar Cookies" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Ações:" -ForegroundColor White
Write-Host "  1. Clique no " -NoNewline -ForegroundColor Yellow
Write-Host "ícone da extensão " -NoNewline -ForegroundColor Cyan
Write-Host "(🧩 canto superior direito)" -ForegroundColor Yellow
Write-Host "  2. Clique em " -NoNewline -ForegroundColor Yellow
Write-Host "'Export'" -NoNewline -ForegroundColor Green
Write-Host " ou " -NoNewline -ForegroundColor Yellow
Write-Host "'Get cookies.txt'" -ForegroundColor Green
Write-Host "  3. Salve o arquivo como: " -NoNewline -ForegroundColor Yellow
Write-Host "$OutputFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  IMPORTANTE: Salve no diretório ATUAL:" -ForegroundColor Red
Write-Host "   $(Get-Location)" -ForegroundColor Cyan
Write-Host ""

Read-Host "Pressione ENTER quando tiver exportado o arquivo"

# Verificar se arquivo foi criado
Write-Host ""
Write-Host "🔍 Verificando arquivo..." -ForegroundColor Cyan

Start-Sleep -Seconds 1

if (-not (Test-Path $OutputFile)) {
    Write-Host ""
    Write-Host "❌ Arquivo não encontrado: $OutputFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Possíveis causas:" -ForegroundColor Yellow
    Write-Host "   • Salvou em outro diretório (geralmente: Downloads)" -ForegroundColor White
    Write-Host "   • Nome do arquivo diferente" -ForegroundColor White
    Write-Host "   • Não exportou ainda" -ForegroundColor White
    Write-Host ""
    Write-Host "📂 Arquivos .txt no diretório Downloads:" -ForegroundColor Cyan

    $downloadsPath = [Environment]::GetFolderPath("UserProfile") + "\Downloads"
    if (Test-Path $downloadsPath) {
        Get-ChildItem -Path $downloadsPath -Filter "*.txt" -ErrorAction SilentlyContinue |
        Select-Object -First 5 |
        ForEach-Object {
            Write-Host "   📄 $($_.Name) ($(([math]::Round($_.Length/1024, 2))) KB)" -ForegroundColor White
        }
    }

    Write-Host ""
    Write-Host "📂 Arquivos .txt no diretório atual:" -ForegroundColor Cyan
    Get-ChildItem -Filter "*.txt" -ErrorAction SilentlyContinue |
    ForEach-Object {
        Write-Host "   📄 $($_.Name) ($(([math]::Round($_.Length/1024, 2))) KB)" -ForegroundColor White
    }

    Write-Host ""
    $manualPath = Read-Host "Digite o caminho completo do arquivo (ou ENTER para sair)"

    if ([string]::IsNullOrWhiteSpace($manualPath)) {
        Write-Host "❌ Cancelado pelo usuário" -ForegroundColor Red
        exit 1
    }

    if (Test-Path $manualPath) {
        Copy-Item $manualPath $OutputFile -Force
        Write-Host "✅ Arquivo copiado para $OutputFile" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Arquivo não encontrado: $manualPath" -ForegroundColor Red
        exit 1
    }
}

# Validar arquivo
Write-Host ""
Write-Host "🔍 Validando arquivo..." -ForegroundColor Cyan

$fileSize = (Get-Item $OutputFile).Length

if ($fileSize -lt 100) {
    Write-Host "❌ Arquivo muito pequeno ($fileSize bytes)!" -ForegroundColor Red
    Write-Host "   Arquivo pode estar vazio ou corrompido" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Tente exportar novamente:" -ForegroundColor Yellow
    Write-Host "   1. Certifique-se de estar LOGADO no YouTube" -ForegroundColor White
    Write-Host "   2. Clique na extensão e escolha 'Export'" -ForegroundColor White
    Write-Host "   3. Salve como $OutputFile no diretório atual" -ForegroundColor White
    exit 1
}

# Verificar conteúdo (procurar por cookies do YouTube)
$content = Get-Content $OutputFile -Raw
$hasYouTubeCookies = $content -match "youtube\.com"

if (-not $hasYouTubeCookies) {
    Write-Host "⚠️  AVISO: Cookies do YouTube não encontrados!" -ForegroundColor Yellow
    Write-Host "   O arquivo pode não conter cookies do YouTube" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continuar mesmo assim? (S/N)"
    if ($continue -notmatch '^[Ss]$') {
        exit 1
    }
}

Write-Host "✅ Arquivo validado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Informações do arquivo:" -ForegroundColor Cyan
Write-Host "   📁 Arquivo: $OutputFile" -ForegroundColor White
Write-Host "   📦 Tamanho: $([math]::Round($fileSize/1024, 2)) KB" -ForegroundColor White
Write-Host "   📅 Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor White

# Contar número de cookies
try {
    $cookieLines = (Get-Content $OutputFile | Where-Object { $_ -match "^\." }).Count
    Write-Host "   🍪 Cookies: $cookieLines entradas" -ForegroundColor White
}
catch {
    Write-Host "   🍪 Cookies: Formato válido detectado" -ForegroundColor White
}

# Ajustar permissões (somente leitura)
try {
    Set-ItemProperty -Path $OutputFile -Name IsReadOnly -Value $true
    Write-Host "   🔒 Permissões: Somente leitura" -ForegroundColor White
}
catch {
    Write-Host "   ⚠️  Permissões: Não foi possível ajustar" -ForegroundColor Yellow
}

Write-Host ""

# Próximos passos
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "✅ Exportação Concluída!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1️⃣  Para testar localmente:" -ForegroundColor White
Write-Host "   .\scripts\start_bot.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "2️⃣  Para enviar para servidor:" -ForegroundColor White
Write-Host "   .\scripts\upload_cookies.ps1 -Server usuario@servidor -Path /caminho/bot" -ForegroundColor Cyan
Write-Host ""
Write-Host "3️⃣  Validade dos cookies:" -ForegroundColor White
Write-Host "   60-90 dias (re-exporte quando necessário)" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  SEGURANÇA:" -ForegroundColor Yellow
Write-Host "   • NUNCA compartilhe cookies.txt" -ForegroundColor Red
Write-Host "   • NUNCA faça commit no Git (já está no .gitignore)" -ForegroundColor Red
Write-Host "   • Cookies contêm suas credenciais de login!" -ForegroundColor Red
Write-Host ""
Write-Host "💡 Dica: Configure lembretes para re-exportar cookies:" -ForegroundColor Cyan
Write-Host "   • No calendário: " -NoNewline -ForegroundColor White
Write-Host "$(((Get-Date).AddDays(60)).ToString('dd/MM/yyyy'))" -ForegroundColor Yellow
Write-Host "   • Comando rápido: " -NoNewline -ForegroundColor White
Write-Host ".\scripts\extract_cookies.ps1 -OpenBrowser" -ForegroundColor Yellow
Write-Host ""
