#!/bin/bash

# ============================================
# Script de Inicialização do Bot - Linux
# Inicia o bot com verificações de ambiente
# ============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Variáveis
DEV_MODE=false
VERBOSE=false
CHECK_ONLY=false

# Parse argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            DEV_MODE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        *)
            echo -e "${RED}❌ Argumento desconhecido: $1${NC}"
            echo "Uso: $0 [--dev] [--verbose] [--check-only]"
            exit 1
            ;;
    esac
done

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}🤖 Iniciando Bot YouTube Discord${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Detectar diretório do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Mudar para diretório do projeto
cd "$PROJECT_ROOT"
echo -e "${CYAN}📁 Diretório: $PROJECT_ROOT${NC}"
echo ""

# ============================================
# 1. VERIFICAR PYTHON
# ============================================

echo -e "${CYAN}🔍 Verificando Python...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado!${NC}"
    echo -e "${YELLOW}   Instale Python 3.10+:${NC}"
    echo "   sudo apt update"
    echo "   sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || [ "$PYTHON_MAJOR" -eq 3 -a "$PYTHON_MINOR" -lt 10 ]; then
    echo -e "${RED}❌ Python $PYTHON_VERSION encontrado, mas é necessário Python 3.10+${NC}"
    echo -e "${YELLOW}   Atualize Python:${NC}"
    echo "   sudo apt update"
    echo "   sudo apt install python3.10"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION${NC}"

# ============================================
# 2. VERIFICAR/CRIAR AMBIENTE VIRTUAL
# ============================================

echo -e "${CYAN}🔍 Verificando ambiente virtual...${NC}"

VENV_PATH="$PROJECT_ROOT/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}⚠️  Ambiente virtual não encontrado. Criando...${NC}"
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Falha ao criar ambiente virtual!${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Ambiente virtual criado${NC}"
else
    echo -e "${GREEN}✅ Ambiente virtual encontrado${NC}"
fi

# Ativar ambiente virtual
echo -e "${CYAN}🔄 Ativando ambiente virtual...${NC}"
source "$VENV_PATH/bin/activate"

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Falha ao ativar ambiente virtual!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Ambiente virtual ativado${NC}"

# ============================================
# 3. VERIFICAR DEPENDÊNCIAS
# ============================================

echo -e "${CYAN}🔍 Verificando dependências...${NC}"

REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"

if [ ! -f "$REQUIREMENTS_FILE" ]; then
    echo -e "${RED}❌ requirements.txt não encontrado!${NC}"
    exit 1
fi

# Verificar se dependências estão instaladas
MISSING_PACKAGES=$(comm -23 \
    <(cat "$REQUIREMENTS_FILE" | grep -v '^#' | cut -d'=' -f1 | sort) \
    <(pip freeze | cut -d'=' -f1 | sort) 2>/dev/null)

if [ ! -z "$MISSING_PACKAGES" ]; then
    echo -e "${YELLOW}⚠️  Dependências faltando. Instalando...${NC}"
    pip install -r "$REQUIREMENTS_FILE"

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ Falha ao instalar dependências!${NC}"
        exit 1
    fi

    echo -e "${GREEN}✅ Dependências instaladas${NC}"
else
    echo -e "${GREEN}✅ Todas dependências instaladas${NC}"
fi

# ============================================
# 4. VERIFICAR FFmpeg
# ============================================

echo -e "${CYAN}🔍 Verificando FFmpeg...${NC}"

if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️  FFmpeg não encontrado!${NC}"
    echo -e "${YELLOW}   Instalando FFmpeg...${NC}"

    if [ -f /etc/debian_version ]; then
        # Debian/Ubuntu
        sudo apt update
        sudo apt install -y ffmpeg
    elif [ -f /etc/redhat-release ]; then
        # RedHat/CentOS
        sudo yum install -y ffmpeg
    else
        echo -e "${RED}❌ Sistema não suportado. Instale FFmpeg manualmente.${NC}"
        exit 1
    fi

    if command -v ffmpeg &> /dev/null; then
        echo -e "${GREEN}✅ FFmpeg instalado${NC}"
    else
        echo -e "${RED}❌ Falha ao instalar FFmpeg!${NC}"
        exit 1
    fi
else
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n1 | awk '{print $3}')
    echo -e "${GREEN}✅ FFmpeg $FFMPEG_VERSION${NC}"
fi

# ============================================
# 5. VERIFICAR CONFIGURAÇÃO
# ============================================

echo -e "${CYAN}🔍 Verificando configuração...${NC}"

# Verificar .env
ENV_FILE="$PROJECT_ROOT/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  Arquivo .env não encontrado!${NC}"

    ENV_EXAMPLE="$PROJECT_ROOT/.env.example"
    if [ -f "$ENV_EXAMPLE" ]; then
        echo -e "${YELLOW}   Copiando .env.example para .env...${NC}"
        cp "$ENV_EXAMPLE" "$ENV_FILE"
        echo -e "${GREEN}✅ Arquivo .env criado${NC}"
        echo ""
        echo -e "${RED}⚠️  IMPORTANTE: Edite .env com suas credenciais!${NC}"
        echo -e "${CYAN}   nano .env${NC}"
        echo ""
        exit 1
    else
        echo -e "${RED}❌ .env.example não encontrado!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Arquivo .env encontrado${NC}"
fi

# Verificar token OAuth2 (opcional)
TOKEN_FILE="$PROJECT_ROOT/config/token.json"
if [ ! -f "$TOKEN_FILE" ]; then
    echo -e "${YELLOW}⚠️  Token OAuth2 não encontrado (opcional)${NC}"
    echo -e "${YELLOW}   O bot tentará usar API Key ou cookies como fallback${NC}"
else
    echo -e "${GREEN}✅ Token OAuth2 encontrado${NC}"
fi

# Verificar cookies (opcional)
COOKIES_FILE="$PROJECT_ROOT/cookies.txt"
if [ ! -f "$COOKIES_FILE" ]; then
    echo -e "${YELLOW}⚠️  Cookies não encontrados (recomendado)${NC}"
    echo -e "${CYAN}   Copie do Windows: scp cookies.txt user@servidor:$PROJECT_ROOT/${NC}"
else
    COOKIE_AGE=$(( ($(date +%s) - $(stat -c %Y "$COOKIES_FILE")) / 86400 ))
    if [ $COOKIE_AGE -gt 90 ]; then
        echo -e "${YELLOW}⚠️  Cookies com $COOKIE_AGE dias (re-extrair recomendado)${NC}"
    else
        echo -e "${GREEN}✅ Cookies encontrados ($COOKIE_AGE dias)${NC}"
    fi
fi

echo ""

# ============================================
# 6. VERIFICAÇÃO FINAL
# ============================================

if [ "$CHECK_ONLY" = true ]; then
    echo -e "${CYAN}============================================${NC}"
    echo -e "${GREEN}✅ Verificação Concluída!${NC}"
    echo -e "${CYAN}============================================${NC}"
    echo ""
    echo -e "${GREEN}Ambiente está pronto para rodar o bot.${NC}"
    echo -e "${YELLOW}Execute sem --check-only para iniciar.${NC}"
    echo ""
    exit 0
fi

# ============================================
# 7. INICIAR BOT
# ============================================

echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}🚀 Iniciando Bot...${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Definir variáveis de ambiente adicionais
if [ "$DEV_MODE" = true ]; then
    export LOG_LEVEL="DEBUG"
    echo -e "${YELLOW}🐛 Modo Desenvolvedor Ativado (LOG_LEVEL=DEBUG)${NC}"
    echo ""
fi

if [ "$VERBOSE" = true ]; then
    export VERBOSE="true"
    echo -e "${YELLOW}📢 Modo Verbose Ativado${NC}"
    echo ""
fi

# Iniciar main.py
MAIN_FILE="$PROJECT_ROOT/main.py"

if [ ! -f "$MAIN_FILE" ]; then
    echo -e "${RED}❌ main.py não encontrado!${NC}"
    exit 1
fi

echo -e "${CYAN}▶️  Executando: python3 main.py${NC}"
echo ""
echo -e "${YELLOW}💡 Para parar o bot: Ctrl+C${NC}"
echo ""
echo -e "${CYAN}============================================${NC}"
echo ""

# Trap Ctrl+C para cleanup
trap 'echo ""; echo -e "${CYAN}============================================${NC}"; echo -e "${GREEN}✅ Bot Encerrado${NC}"; echo -e "${CYAN}============================================${NC}"; echo ""; exit 0' INT

python3 "$MAIN_FILE"

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${GREEN}✅ Bot Encerrado${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""
