# 🛠️ Scripts Utilitários - Bot de Música para Discord

Scripts auxiliares para depuração, manutenção e gerenciamento do bot.

---

## 📋 Estrutura

```
scripts/
├── README.md                       # Este arquivo
├── debug_batch_processing.py       # Debug de processamento em batch
└── stop_bot.py                     # Encerramento gracioso do bot
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

**Veja também:** [Guia de Encerramento](../docs/guides/guia-encerramento.md)

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
