# 🛠️ Scripts Utilitários - Bot de Música para Discord

Scripts auxiliares para depuração, manutenção e gerenciamento do bot.

---

## 📋 Estrutura

```
scripts/
├── README.md                         # Este arquivo
├── debug_batch_processing.py         # Debug de processamento em batch
├── stop_bot.py                       # Encerramento gracioso do bot
└── copy_token_to_server.py           # Copia token para servidor remoto
```

---

## 📝 Scripts Disponíveis

### `stop_bot.py` - Encerramento Gracioso

Envia um sinal de encerramento gracioso para o bot, garantindo que:
- Todas as conexões de voz sejam desconectadas
- Fila de músicas seja salva
- Recursos sejam liberados adequadamente

**Como usar:**

```bash
# Windows (PowerShell)
python scripts/stop_bot.py

# Linux/Mac
python3 scripts/stop_bot.py
```

**Alternativa manual:**
- Pressione `Ctrl+C` no terminal do bot
- O sistema irá capturar o sinal e fazer shutdown gracioso

**O que acontece:**
1. Bot desconecta de todos os servidores de voz
2. Salva estado da fila (se habilitado)
3. Fecha conexões com APIs (YouTube, Groq)
4. Libera recursos do FFmpeg
5. Encerra o processo

**Veja também:** [Guia de Encerramento](../docs/guides/encerramento.md)

---

### `copy_token_to_server.py` - Copiar Token para Servidor

Copia o `token.json` de forma segura para um servidor remoto via SCP.

**Quando usar:**
- Deployando bot em VPS/servidor sem interface gráfica
- Servidor não tem navegador (ambiente headless)
- Quer evitar autenticação manual no servidor

**Pré-requisitos:**
- SSH configurado para o servidor
- Bot autenticado localmente (token.json existe)
- OpenSSH/SCP instalado

**Como usar:**

```bash
# Sintaxe geral
python scripts/copy_token_to_server.py usuario@servidor:/caminho/bot

# Exemplos
python scripts/copy_token_to_server.py root@192.168.1.100:/root/bot-youtube-pao
python scripts/copy_token_to_server.py ubuntu@vps.exemplo.com:/home/ubuntu/bot
python scripts/copy_token_to_server.py user@servidor.com.br:/opt/discord-bot
```

**O que faz:**
1. Verifica se `config/token.json` existe localmente
2. Confirma a operação com o usuário
3. Copia o token via SCP para o servidor
4. Exibe próximos passos (chmod, executar bot)

**Exemplo de execução:**

```
$ python scripts/copy_token_to_server.py root@192.168.1.100:/root/bot

✅ Token encontrado!
📁 Origem: /home/user/bot-youtube-pao/config/token.json
🎯 Destino: root@192.168.1.100:/root/bot

⚠️  Continuar? (s/N): s

📤 Copiando token...
✅ Token copiado com sucesso!

📝 Próximos passos:
1. Conecte ao servidor via SSH
2. Verifique permissões: chmod 600 config/token.json
3. Rode o bot: python3 main.py
```

**Troubleshooting:**

- **"Token não encontrado"**: Execute `python main.py` localmente primeiro
- **"scp não encontrado"**: Instale OpenSSH Client
- **"Permission denied"**: Verifique acesso SSH ao servidor
- **"No such file or directory"**: Crie o diretório config/ no servidor

**Veja também:** [Guia de Servidor](../docs/guides/servidor.md)

---

## 🍪 Cookies & Autenticação

### `extract_cookies.ps1` - Extrair Cookies Automaticamente (Windows)

Extrai cookies do navegador Chrome/Edge automaticamente usando yt-dlp.

**Requisitos:**
- Windows 10/11
- Python + yt-dlp instalados
- Chrome/Edge com login no YouTube

**Uso:**

```powershell
# Chrome (padrão)
.\scripts\extract_cookies.ps1

# Edge
.\scripts\extract_cookies.ps1 -Browser edge

# Firefox
.\scripts\extract_cookies.ps1 -Browser firefox

# Brave
.\scripts\extract_cookies.ps1 -Browser brave

# Arquivo de saída customizado
.\scripts\extract_cookies.ps1 -OutputFile "meus_cookies.txt"
```

**O que faz:**
1. ✅ Verifica se Python e yt-dlp estão instalados
2. ✅ Detecta navegador instalado
3. ✅ Solicita confirmação (login no YouTube)
4. ✅ Extrai cookies usando yt-dlp
5. ✅ Salva em `cookies.txt`
6. ✅ Ajusta permissões (somente leitura)
7. ✅ Mostra estatísticas (tamanho, quantidade de cookies)

**Saída esperada:**
```
============================================
🍪 Extrator Automático de Cookies
============================================

✅ Python encontrado: Python 3.11.5
✅ yt-dlp encontrado: v2024.11.04
✅ Google Chrome encontrado

🔄 Extraindo cookies...
✅ Cookies extraídos com sucesso!

📊 Informações do arquivo:
   📁 Arquivo: cookies.txt
   📦 Tamanho: 5.24 KB
   📅 Data: 2025-11-14 10:30:00
   🍪 Cookies: 42 entradas
```

**Erros comuns:**
- "Navegador não encontrado" → Instale Chrome/Edge
- "Erro ao extrair" → Feche o navegador completamente
- "Arquivo vazio" → Verifique se está logado no YouTube

---

### `upload_cookies.ps1` - Enviar Cookies para Servidor

Envia `cookies.txt` para servidor Linux via SCP.

**Requisitos:**
- Windows com OpenSSH Client
- Acesso SSH ao servidor
- `cookies.txt` já extraído

**Uso:**

```powershell
# Básico
.\scripts\upload_cookies.ps1 -Server usuario@servidor -Path /caminho/bot

# Com reinício automático do bot
.\scripts\upload_cookies.ps1 -Server ubuntu@192.168.1.100 -Path /home/ubuntu/bot -RestartBot

# Arquivo customizado
.\scripts\upload_cookies.ps1 -Server user@host -Path /opt/bot -CookiesFile meus_cookies.txt
```

**Parâmetros:**
- `-Server`: Usuário e host SSH (formato: `usuario@servidor`)
- `-Path`: Caminho do bot no servidor
- `-CookiesFile`: Arquivo de cookies (padrão: `cookies.txt`)
- `-RestartBot`: Reinicia bot automaticamente após upload

**O que faz:**
1. ✅ Verifica se `cookies.txt` existe
2. ✅ Alerta se cookies estão antigos (>90 dias)
3. ✅ Envia arquivo via SCP
4. ✅ Ajusta permissões no servidor (chmod 600)
5. ✅ (Opcional) Reinicia bot via systemd

**Saída esperada:**
```
============================================
📤 Upload de Cookies para Servidor
============================================

📊 Informações do arquivo:
   📁 Arquivo: cookies.txt
   📦 Tamanho: 5.24 KB
   📅 Modificado: 2025-11-14 10:30:00

🌐 Servidor de destino:
   👤 Usuário: ubuntu
   🖥️  Host: 192.168.1.100
   📂 Caminho: /home/ubuntu/bot/cookies.txt

🔄 Enviando arquivo...
✅ Arquivo enviado com sucesso!

🔒 Ajustando permissões no servidor...
-rw------- 1 ubuntu ubuntu 5365 Nov 14 10:30 /home/ubuntu/bot/cookies.txt
✅ Permissões ajustadas (600 - somente proprietário)
```

**Solução de problemas:**
- "SCP não encontrado" → Instale OpenSSH Client
- "Permission denied" → Verifique acesso SSH
- "No such file or directory" → Verifique caminho no servidor

**Veja também:**
- [Guia de Cookies](../docs/guides/cookies-youtube.md)
- [Deploy em Servidor](../docs/guides/servidor.md)

---

## 🚀 Inicialização

### `start_bot.ps1` - Iniciar Bot (Windows)

Script completo de inicialização com verificações automáticas de ambiente.

**Uso:**

```powershell
# Modo normal
.\scripts\start_bot.ps1

# Modo desenvolvedor (DEBUG)
.\scripts\start_bot.ps1 -Dev

# Modo verbose
.\scripts\start_bot.ps1 -Verbose

# Apenas verificar (sem iniciar)
.\scripts\start_bot.ps1 -CheckOnly

# Combinado
.\scripts\start_bot.ps1 -Dev -Verbose
```

**O que faz:**
1. ✅ Verifica Python 3.10+
2. ✅ Cria ambiente virtual se não existir
3. ✅ Ativa ambiente virtual
4. ✅ Instala dependências faltantes
5. ✅ Verifica configuração (.env, token, cookies)
6. ✅ Inicia bot com logging apropriado

**Verificações:**
- Python versão >= 3.10
- Ambiente virtual (cria se não existir)
- Dependências do `requirements.txt`
- Arquivo `.env` (cria do .env.example)
- Token OAuth2 (avisa se não existir)
- Cookies (avisa idade se >90 dias)

**Parâmetros:**
- `-Dev`: Ativa modo desenvolvedor (LOG_LEVEL=DEBUG)
- `-Verbose`: Ativa logs verbose
- `-CheckOnly`: Apenas verifica, não inicia

---

### `start_bot.sh` - Iniciar Bot (Linux)

Script completo de inicialização para Linux com verificações automáticas.

**Uso:**

```bash
# Dar permissão de execução (primeira vez)
chmod +x scripts/start_bot.sh

# Modo normal
./scripts/start_bot.sh

# Modo desenvolvedor (DEBUG)
./scripts/start_bot.sh --dev

# Modo verbose
./scripts/start_bot.sh --verbose

# Apenas verificar (sem iniciar)
./scripts/start_bot.sh --check-only

# Combinado
./scripts/start_bot.sh --dev --verbose
```

**O que faz:**
1. ✅ Verifica Python 3.10+
2. ✅ Cria ambiente virtual se não existir
3. ✅ Ativa ambiente virtual
4. ✅ Instala dependências faltantes
5. ✅ Verifica/instala FFmpeg
6. ✅ Verifica configuração (.env, token, cookies)
7. ✅ Inicia bot com logging apropriado

**Verificações adicionais (Linux):**
- FFmpeg instalado (instala automaticamente)
- Permissões de arquivo corretas
- Diretórios necessários existem

**Parâmetros:**
- `--dev`: Ativa modo desenvolvedor (LOG_LEVEL=DEBUG)
- `--verbose`: Ativa logs verbose
- `--check-only`: Apenas verifica, não inicia

**Integração com systemd:**

O script pode ser usado diretamente no serviço systemd:

```ini
[Service]
ExecStart=/caminho/bot/scripts/start_bot.sh
```

**Veja também:** [Deploy em Servidor](../docs/guides/servidor.md)

---

## 🔄 Fluxo de Trabalho Completo

### Windows → Servidor Linux

**1. Extrair cookies no Windows:**
```powershell
.\scripts\extract_cookies.ps1
```

**2. Enviar cookies para servidor:**
```powershell
.\scripts\upload_cookies.ps1 -Server ubuntu@servidor -Path /home/ubuntu/bot -RestartBot
```

**3. (Opcional) Testar localmente antes:**
```powershell
.\scripts\start_bot.ps1 -CheckOnly
.\scripts\start_bot.ps1
```

### Apenas Linux (com cookies já copiados)

**1. Verificar ambiente:**
```bash
./scripts/start_bot.sh --check-only
```

**2. Iniciar bot:**
```bash
./scripts/start_bot.sh
```

**3. Manutenção (a cada 60-90 dias):**
```bash
# No Windows, re-extrair cookies
.\scripts\extract_cookies.ps1

# Enviar para servidor
.\scripts\upload_cookies.ps1 -Server user@servidor -Path /path/bot -RestartBot
```

---

## 📅 Cronograma de Manutenção

| Frequência | Tarefa | Script |
|------------|--------|--------|
| **1x (setup)** | Extrair cookies inicial | `extract_cookies.ps1` |
| **1x (setup)** | Enviar para servidor | `upload_cookies.ps1` |
| **A cada 60-90 dias** | Re-extrair cookies | `extract_cookies.ps1` |
| **A cada 60-90 dias** | Re-enviar para servidor | `upload_cookies.ps1` |
| **Diariamente** | Bot roda automaticamente | `start_bot.sh` (systemd) |

---

**Veja também:** [Guia de Servidor](../docs/guides/servidor.md)

---

### `debug_batch_processing.py` - Debug de Batch Processing

Script de depuração para testar o sistema de processamento em batch de vídeos.

**Como usar:**

```bash
python scripts/debug_batch_processing.py
```

**O que faz:**
- Testa processamento de múltiplos vídeos simultaneamente
- Valida integração com YouTube Data API v3
- Mede performance (tempo de resposta, quota usage)
- Exibe logs detalhados de cada etapa

**Exemplo de saída:**

```
🔍 Iniciando teste de batch processing...

📦 Processando batch de 50 vídeos...
⏱️  Tempo decorrido: 0.87s
✅ 50/50 vídeos processados com sucesso

📊 Estatísticas:
   - Tempo médio por vídeo: 17ms
   - Quota usage: 1 unidade (batch)
   - Taxa de sucesso: 100%
   - Cache hits: 12 (24%)

✅ Teste concluído com sucesso!
```

**Use quando:**
- Estiver implementando novos recursos de batch
- Suspeitar de problemas com YouTube API
- Quiser validar performance
- Estiver debugando quota usage

---

## 🚀 Executando Scripts

### Pré-requisitos

```bash
# Certifique-se de ter as dependências instaladas
pip install -r requirements.txt

# Certifique-se de ter as credenciais configuradas
# Veja: docs/guides/guia-credenciais.md
```

### Execução Básica

```bash
# Navegar para o diretório raiz do projeto
cd c:\Users\Matheus\Documents\projeto\bot-youtube-pao

# Executar um script
python scripts/<nome_do_script>.py
```

### Flags Comuns

```bash
# Com verbose logging
python scripts/debug_batch_processing.py --verbose

# Com output em arquivo
python scripts/debug_batch_processing.py > debug_output.txt

# Help
python scripts/<script>.py --help
```

---

## 🆕 Criando Novos Scripts

### Template Básico

```python
#!/usr/bin/env python3
"""
Script de exemplo para o Bot de Música

Descrição breve do que o script faz.
"""

import sys
import os
import asyncio
from pathlib import Path

# Adicionar diretório raiz ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Imports do projeto
from core.logger import logger
from config import settings


async def main():
    """Função principal do script"""
    logger.info("Iniciando script...")

    try:
        # Seu código aqui
        pass

    except Exception as e:
        logger.error(f"Erro ao executar script: {e}")
        return 1

    logger.info("Script concluído com sucesso!")
    return 0


if __name__ == "__main__":
    # Executar de forma assíncrona
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

### Boas Práticas

1. **Docstring**: Sempre adicione uma descrição clara no topo
2. **Logging**: Use o sistema de logging do projeto (`core.logger`)
3. **Error Handling**: Capture exceções e retorne exit codes apropriados
4. **Path Handling**: Use `pathlib` para caminhos multiplataforma
5. **Async/Await**: Use async quando interagir com serviços do bot
6. **CLI Args**: Use `argparse` para argumentos de linha de comando

### Exemplo com Argumentos

```python
import argparse

def parse_args():
    """Parse argumentos de linha de comando"""
    parser = argparse.ArgumentParser(
        description='Script de exemplo'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Ativar modo verbose'
    )
    parser.add_argument(
        '--guild-id',
        type=int,
        help='ID do servidor Discord'
    )
    return parser.parse_args()

async def main():
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Usar args.guild_id...
```

---

## 🔧 Scripts Planejados

### Alta Prioridade

- [ ] **migrate_database.py**
  - Migrar dados de cache antigo
  - Limpar dados corrompidos
  - Compactar banco de dados

- [ ] **health_check.py**
  - Verificar conectividade com APIs (YouTube, Groq, Discord)
  - Testar credenciais
  - Verificar quota usage
  - Gerar relatório de saúde

- [ ] **clear_cache.py**
  - Limpar cache de músicas antigas
  - Remover arquivos temporários
  - Liberar espaço em disco

### Média Prioridade

- [ ] **backup.py**
  - Fazer backup de configurações
  - Fazer backup de cache
  - Fazer backup de logs importantes

- [ ] **analyze_logs.py**
  - Analisar logs de erro
  - Gerar estatísticas de uso
  - Identificar padrões de problemas

- [ ] **benchmark.py**
  - Testar performance de extração
  - Testar performance de busca
  - Comparar com versões anteriores

### Baixa Prioridade

- [ ] **generate_docs.py**
  - Gerar documentação da API
  - Gerar changelog automático
  - Gerar estatísticas do projeto

- [ ] **update_deps.py**
  - Verificar atualizações de dependências
  - Testar compatibilidade
  - Atualizar requirements.txt

---

## 🆘 Troubleshooting

### Script não encontra módulos

```bash
# Certifique-se de estar no diretório raiz
cd c:\Users\Matheus\Documents\projeto\bot-youtube-pao

# Execute com python -m
python -m scripts.debug_batch_processing
```

### Erro de permissões

```bash
# Windows: Execute PowerShell como Administrador
# Linux/Mac: Use sudo
sudo python3 scripts/stop_bot.py
```

### Script trava/não responde

```bash
# Adicione timeout
timeout 30 python scripts/debug_batch_processing.py

# Ou use Ctrl+C para cancelar
```

---

## 📊 Logs e Output

### Localização dos Logs

```
logs/
├── bot.log                  # Log geral do bot
├── music.log                # Log do sistema de música
├── errors.log               # Log de erros
└── scripts/                 # Logs de scripts (se habilitado)
    ├── debug_batch.log
    └── stop_bot.log
```

### Configurar Logging de Scripts

```python
from core.logger import setup_logger

# Criar logger específico para o script
script_logger = setup_logger(
    name="meu_script",
    log_file="logs/scripts/meu_script.log",
    level=logging.DEBUG
)

script_logger.info("Mensagem de log")
```

---

## 🤝 Contribuindo com Scripts

Ao criar um novo script útil:

1. **Adicione ao diretório `scripts/`**
2. **Documente no README** (este arquivo)
3. **Siga as boas práticas** acima
4. **Adicione testes** (se aplicável) em `tests/`
5. **Submeta um PR** seguindo [CONTRIBUTING.md](../CONTRIBUTING.md)

**Exemplo de contribuição:**

```bash
# 1. Criar branch
git checkout -b feature/script-migrate-database

# 2. Criar script
# scripts/migrate_database.py

# 3. Documentar
# Adicionar seção neste README

# 4. Commit
git commit -m "feat(scripts): add database migration script"

# 5. Push e PR
git push origin feature/script-migrate-database
```

---

## 📚 Recursos Adicionais

- [Guia de Credenciais](../docs/guides/guia-credenciais.md)
- [Guia de Encerramento](../docs/guides/guia-encerramento.md)
- [Otimizações de Performance](../docs/technical/otimizacoes.md)
- [Contribuindo](../CONTRIBUTING.md)

---

**Última Atualização**: 13 de novembro de 2025
**Mantenedor**: [@MatheusAlves96](https://github.com/MatheusAlves96)
