# 🔧 Comandos Administrativos

Comandos para gerenciar o bot em tempo real **sem necessidade de reiniciar**.

## 📋 Índice

1. [Configuração de Variáveis](#configuração-de-variáveis)
2. [Visualização de Configurações](#visualização-de-configurações)
3. [Gerenciamento de Plugins](#gerenciamento-de-plugins)
4. [Status do Sistema](#status-do-sistema)

---

## 🔐 Permissões

**Todos os comandos administrativos são restritos ao dono do bot** (definido por `OWNER_ID` no `.env`).

---

## Configuração de Variáveis

### `!setenv` - Definir Variável

Define ou atualiza uma variável de ambiente no `.env`.

**Uso:**
```
!setenv <VARIAVEL> <valor>
```

**Aliases:** `!config`, `!env`

**Exemplos:**
```bash
# Configurar API do Groq (IA Autoplay)
!setenv GROQ_API_KEY gsk_sua_chave_aqui

# Configurar API da Riot (Plugin LoL)
!setenv RIOT_API_KEY RGAPI-sua-chave-riot

# Ativar Autoplay
!setenv AUTOPLAY_ENABLED True

# Definir tamanho da fila do Autoplay
!setenv AUTOPLAY_QUEUE_SIZE 5

# Atualizar volume padrão
!setenv DEFAULT_VOLUME 0.7

# Mudar nível de log
!setenv LOG_LEVEL DEBUG
```

#### Tipos de Variáveis

##### ✅ Dinâmicas (Aplicadas em Tempo Real)

Estas variáveis são aplicadas **imediatamente** sem reiniciar:

- `GROQ_API_KEY` - Chave da API do Groq (IA)
- `RIOT_API_KEY` - Chave da API da Riot (LoL)
- `AUTOPLAY_ENABLED` - Ativar/desativar autoplay
- `AUTOPLAY_QUEUE_SIZE` - Músicas a adicionar por vez
- `DEFAULT_VOLUME` - Volume padrão (0.0 a 1.0)
- `LOG_LEVEL` - Nível de log (DEBUG, INFO, WARNING, ERROR)
- `YTDL_COOKIES_PATH` - Caminho dos cookies do YouTube

##### 🔄 Requerem Reinício

Estas variáveis **requerem reinicialização do bot**:

- `DISCORD_TOKEN` - Token do bot Discord
- `YOUTUBE_API_KEY` - Chave da API do YouTube
- `YOUTUBE_CLIENT_ID` - ID do cliente OAuth2
- `YOUTUBE_CLIENT_SECRET` - Secret do cliente OAuth2
- `COMMAND_PREFIX` - Prefixo dos comandos

**Nota:** Ao definir variáveis que requerem reinício, o bot avisará e você precisará usar `!restart` (se implementado) ou reiniciar manualmente.

---

## Visualização de Configurações

### `!getenv` - Ver Variável

Mostra o valor atual de uma variável de ambiente.

**Uso:**
```
!getenv <VARIAVEL>
```

**Aliases:** `!showconfig`, `!viewenv`

**Exemplos:**
```bash
# Ver chave do Groq (parcialmente oculta)
!getenv GROQ_API_KEY
# Resultado: gsk_****...****xyz

# Ver status do autoplay
!getenv AUTOPLAY_ENABLED
# Resultado: True

# Ver volume padrão
!getenv DEFAULT_VOLUME
# Resultado: 0.5
```

**Segurança:** Variáveis sensíveis (contendo `TOKEN`, `KEY`, `SECRET`, `PASSWORD`) são **parcialmente ocultas** para proteger credenciais.

---

### `!listenv` - Listar Todas as Variáveis

Lista todas as variáveis configuradas no `.env`, organizadas por categoria.

**Uso:**
```
!listenv
```

**Aliases:** `!envlist`, `!configs`

**Exemplo de Saída:**

```
🔧 Configurações do Bot

🤖 Discord
✅ COMMAND_PREFIX
🔄 DISCORD_TOKEN
🔄 OWNER_ID

📺 YouTube
🔄 YOUTUBE_API_KEY
✅ YTDL_COOKIES_PATH

🤖 AI Service
✅ GROQ_API_KEY

🎵 Música
✅ AUTOPLAY_ENABLED
✅ AUTOPLAY_QUEUE_SIZE
✅ DEFAULT_VOLUME

🔌 Plugins
✅ RIOT_API_KEY

⚙️ Sistema
✅ LOG_LEVEL

✅ Dinâmica | 🔄 Requer Reinício
```

---

## Gerenciamento de Plugins

### `!reload` - Recarregar Plugins

Recarrega todos os plugins do bot, aplicando mudanças em configurações ou código.

**Uso:**
```
!reload
```

**Aliases:** `!reloadplugins`

**Quando usar:**
- Após alterar configurações de plugins (ex: `RIOT_API_KEY`)
- Após modificar código de um plugin
- Para resolver problemas de plugins travados

**Exemplo:**
```bash
# 1. Configurar chave da Riot
!setenv RIOT_API_KEY RGAPI-sua-chave

# 2. Recarregar plugins para aplicar
!reload

# Resultado:
✅ Plugins Recarregados
📤 Descarregados: 2
📥 Carregados: 2

🔌 Plugins Ativos
• Hello World v1.0.0
• League of Legends v1.0.0
```

---

## Status do Sistema

### `!status` - Informações do Bot

Mostra informações detalhadas sobre o status atual do bot.

**Uso:**
```
!status
```

**Aliases:** `!info`, `!botinfo`

**Informações Mostradas:**

1. **🤖 Bot**
   - Nome
   - ID
   - Número de servidores

2. **💻 Sistema**
   - Sistema operacional
   - Uso de CPU
   - Uso de RAM

3. **⚙️ Configurações**
   - Prefixo de comandos
   - Status do Autoplay
   - Status do Cache

4. **🔌 Plugins**
   - Plugins carregados
   - Plugins disponíveis

5. **🎵 Áudio**
   - Canais de voz conectados
   - Status do FFmpeg

**Exemplo de Saída:**

```
📊 Status do Bot

🤖 Bot
Nome: MusicBot
ID: 123456789
Servidores: 5

💻 Sistema
OS: Windows
CPU: 15.2%
RAM: 45.8%

⚙️ Configurações
Prefix: !
Autoplay: ✅
Cache: ✅

🔌 Plugins
Carregados: 2
Disponíveis: 2

🎵 Áudio
Canais de Voz: 1
FFmpeg: ✅
```

---

## 🎯 Casos de Uso Práticos

### Caso 1: Ativar Plugin League of Legends

```bash
# 1. Obter chave da Riot API em: https://developer.riotgames.com/
# 2. Configurar sem reiniciar o bot
!setenv RIOT_API_KEY RGAPI-sua-chave-aqui

# 3. Recarregar plugins
!reload

# 4. Testar comando
!lol
```

### Caso 2: Ativar IA Autoplay

```bash
# 1. Obter chave do Groq em: https://console.groq.com/
# 2. Configurar chave
!setenv GROQ_API_KEY gsk_sua_chave_groq

# 3. Ativar autoplay
!setenv AUTOPLAY_ENABLED True

# 4. Configurar tamanho da fila (opcional)
!setenv AUTOPLAY_QUEUE_SIZE 3

# 5. Testar
!play sua música favorita
# Quando a música acabar, o bot adicionará automaticamente músicas similares!
```

### Caso 3: Atualizar Cookies do YouTube

```bash
# 1. Extrair novos cookies (após 60-90 dias)
.\scripts\extract_cookies.ps1 -OpenBrowser

# 2. Mover cookies para pasta config/
Move-Item cookies.txt config/

# 3. Atualizar caminho (se diferente)
!setenv YTDL_COOKIES_PATH config/cookies.txt

# 4. Pronto! Próxima música já usará os novos cookies
```

### Caso 4: Depuração de Problemas

```bash
# 1. Ativar logs detalhados
!setenv LOG_LEVEL DEBUG

# 2. Verificar status
!status

# 3. Ver todas as configs
!listenv

# 4. Recarregar plugins se necessário
!reload

# 5. Restaurar log normal
!setenv LOG_LEVEL INFO
```

---

## 🔒 Segurança

### Proteção de Credenciais

- ✅ Apenas o **dono do bot** pode usar comandos admin
- ✅ Valores sensíveis são **parcialmente ocultos** em `!getenv`
- ✅ Arquivo `.env` **nunca** é enviado pelo bot
- ✅ Logs não registram valores de variáveis sensíveis

### Boas Práticas

1. **Nunca compartilhe** o resultado de `!getenv` com valores sensíveis
2. **Configure `OWNER_ID`** corretamente no `.env`
3. **Use canais privados** para comandos admin
4. **Revise logs** regularmente com `!status`

---

## 🐛 Troubleshooting

### "❌ Apenas o dono do bot pode usar comandos administrativos!"

**Solução:** Configure seu ID de usuário no `.env`:
```bash
# Descubra seu ID: Discord > Configurações > Avançado > Modo Desenvolvedor
# Clique com botão direito em seu nome > Copiar ID
!setenv OWNER_ID seu_id_aqui
```

### "❌ Arquivo `.env` não encontrado!"

**Solução:** Crie o arquivo `.env` na raiz do projeto:
```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

### Plugin não recarrega após `!setenv`

**Solução:** Use `!reload` para recarregar plugins:
```bash
!setenv RIOT_API_KEY sua_chave
!reload  # ← Não esqueça deste comando!
```

### Variável não aplica mudanças

**Possíveis causas:**

1. **Variável requer reinício** (marcada com 🔄)
   - Solução: Reinicie o bot manualmente

2. **Variável não é reconhecida**
   - Solução: Verifique ortografia com `!listenv`

3. **Tipo de valor incorreto**
   - Solução: `True`/`False` para booleanos, números para inteiros

---

## 📚 Documentação Relacionada

- [Configuração Inicial](INICIO_RAPIDO.md)
- [Guia de Credenciais](GUIA_CREDENCIAIS.md)
- [Sistema de Plugins](PLUGINS.md)
- [FAQ](FAQ.md)

---

## 🔗 Links Úteis

- [Discord Developer Portal](https://discord.com/developers/applications) - Token do bot
- [Google Cloud Console](https://console.cloud.google.com/) - API do YouTube
- [Groq Console](https://console.groq.com/) - API de IA (Autoplay)
- [Riot Developer Portal](https://developer.riotgames.com/) - API do League of Legends

---

**💡 Dica:** Use `!help` para ver todos os comandos disponíveis do bot, incluindo comandos de música e plugins!
