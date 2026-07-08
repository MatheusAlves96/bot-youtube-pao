# ============================================
# Script de Upload de Cookies para Servidor
# Envia cookies.txt via SCP para servidor Linux
# ============================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Server,

    [Parameter(Mandatory=$true)]
    [string]$Path,

    [string]$CookiesFile = "cookies.txt",

    [switch]$RestartBot
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📤 Upload de Cookies para Servidor" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se arquivo de cookies existe
if (-not (Test-Path $CookiesFile)) {
    Write-Host "❌ Arquivo não encontrado: $CookiesFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Execute primeiro:" -ForegroundColor Yellow
    Write-Host "   .\scripts\extract_cookies.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

# Informações do arquivo
$fileInfo = Get-Item $CookiesFile
$fileSize = [math]::Round($fileInfo.Length / 1024, 2)

Write-Host "📊 Informações do arquivo:" -ForegroundColor Cyan
Write-Host "   📁 Arquivo: $CookiesFile" -ForegroundColor White
Write-Host "   📦 Tamanho: $fileSize KB" -ForegroundColor White
Write-Host "   📅 Modificado: $($fileInfo.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor White
Write-Host ""

# Verifica idade do arquivo
$ageInDays = ((Get-Date) - $fileInfo.LastWriteTime).Days
if ($ageInDays -gt 90) {
    Write-Host "⚠️  AVISO: Cookies com $ageInDays dias!" -ForegroundColor Yellow
    Write-Host "   Recomendado: Re-extrair cookies (válido por 60-90 dias)" -ForegroundColor Yellow
    Write-Host ""
    $continue = Read-Host "Continuar mesmo assim? (S/N)"
    if ($continue -notmatch '^[Ss]$') {
        exit 0
    }
}

# Verifica se SCP está disponível
try {
    $scpVersion = scp 2>&1 | Out-Null
    Write-Host "✅ SCP encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ SCP não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Instale OpenSSH Client:" -ForegroundColor Yellow
    Write-Host "   1. Abra: Configurações > Aplicativos > Recursos Opcionais" -ForegroundColor White
    Write-Host "   2. Adicione: Cliente OpenSSH" -ForegroundColor White
    Write-Host ""
    Write-Host "   Ou baixe PuTTY: https://www.putty.org/" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Parsear servidor e usuário
if ($Server -notmatch '^(.+)@(.+)$') {
    Write-Host "❌ Formato de servidor inválido!" -ForegroundColor Red
    Write-Host "   Formato esperado: usuario@servidor" -ForegroundColor Yellow
    Write-Host "   Exemplo: ubuntu@192.168.1.100" -ForegroundColor Cyan
    exit 1
}

$user = $matches[1]
$host = $matches[2]
$remotePath = "$Path/$CookiesFile"

Write-Host "🌐 Servidor de destino:" -ForegroundColor Cyan
Write-Host "   👤 Usuário: $user" -ForegroundColor White
Write-Host "   🖥️  Host: $host" -ForegroundColor White
Write-Host "   📂 Caminho: $remotePath" -ForegroundColor White
Write-Host ""

# Confirmação
Write-Host "📤 Pronto para enviar cookies via SCP" -ForegroundColor Yellow
$confirm = Read-Host "Continuar? (S/N)"
if ($confirm -notmatch '^[Ss]$') {
    Write-Host "❌ Cancelado pelo usuário" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "🔄 Enviando arquivo..." -ForegroundColor Cyan

# Executar SCP
try {
    $scpCmd = "scp `"$CookiesFile`" ${Server}:$remotePath"
    Write-Host "   Comando: $scpCmd" -ForegroundColor DarkGray
    Write-Host ""

    Invoke-Expression $scpCmd

    if ($LASTEXITCODE -ne 0) {
        throw "SCP retornou erro: $LASTEXITCODE"
    }

    Write-Host ""
    Write-Host "✅ Arquivo enviado com sucesso!" -ForegroundColor Green
    Write-Host ""

} catch {
    Write-Host "❌ Erro ao enviar arquivo!" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Soluções:" -ForegroundColor Yellow
    Write-Host "   1. Verifique conexão SSH: ssh $Server" -ForegroundColor White
    Write-Host "   2. Verifique se caminho existe no servidor" -ForegroundColor White
    Write-Host "   3. Verifique permissões de escrita" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Ajustar permissões no servidor via SSH
Write-Host "🔒 Ajustando permissões no servidor..." -ForegroundColor Cyan

try {
    $sshCmd = "ssh $Server 'chmod 600 $remotePath && ls -lah $remotePath'"
    Write-Host "   Comando: $sshCmd" -ForegroundColor DarkGray
    Write-Host ""

    $result = Invoke-Expression $sshCmd
    Write-Host $result -ForegroundColor White

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Permissões ajustadas (600 - somente proprietário)" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "⚠️  Aviso: Não foi possível ajustar permissões" -ForegroundColor Yellow
        Write-Host "   Execute manualmente no servidor:" -ForegroundColor Yellow
        Write-Host "   chmod 600 $remotePath" -ForegroundColor Cyan
    }

} catch {
    Write-Host "⚠️  Aviso: Não foi possível ajustar permissões via SSH" -ForegroundColor Yellow
    Write-Host "   Execute manualmente no servidor:" -ForegroundColor Yellow
    Write-Host "   chmod 600 $remotePath" -ForegroundColor Cyan
}

Write-Host ""

# Reiniciar bot se solicitado
if ($RestartBot) {
    Write-Host "🔄 Reiniciando bot no servidor..." -ForegroundColor Cyan

    try {
        $restartCmd = "ssh $Server 'cd $Path && sudo systemctl restart bot-youtube'"
        Write-Host "   Comando: $restartCmd" -ForegroundColor DarkGray
        Write-Host ""

        Invoke-Expression $restartCmd

        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Bot reiniciado com sucesso!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Aviso: Não foi possível reiniciar bot automaticamente" -ForegroundColor Yellow
            Write-Host "   Execute manualmente no servidor:" -ForegroundColor Yellow
            Write-Host "   sudo systemctl restart bot-youtube" -ForegroundColor Cyan
        }

    } catch {
        Write-Host "⚠️  Aviso: Não foi possível reiniciar bot via SSH" -ForegroundColor Yellow
        Write-Host "   Execute manualmente no servidor:" -ForegroundColor Yellow
        Write-Host "   sudo systemctl restart bot-youtube" -ForegroundColor Cyan
    }

    Write-Host ""
}

# Resumo final
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ Upload Concluído!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Próximos passos no servidor:" -ForegroundColor Yellow
Write-Host ""

if (-not $RestartBot) {
    Write-Host "1. Reiniciar bot:" -ForegroundColor White
    Write-Host "   ssh $Server" -ForegroundColor Cyan
    Write-Host "   sudo systemctl restart bot-youtube" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "2. Verificar logs:" -ForegroundColor White
Write-Host "   ssh $Server" -ForegroundColor Cyan
Write-Host "   sudo journalctl -u bot-youtube -f" -ForegroundColor Cyan
Write-Host ""

Write-Host "3. Testar no Discord:" -ForegroundColor White
Write-Host "   !play nome da música" -ForegroundColor Cyan
Write-Host ""

Write-Host "⏰ Lembre-se:" -ForegroundColor Yellow
Write-Host "   • Cookies duram 60-90 dias" -ForegroundColor White
Write-Host "   • Re-extraia quando necessário" -ForegroundColor White
Write-Host "   • Monitore logs para erros de autenticação" -ForegroundColor White
Write-Host ""
