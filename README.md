# 🎵 Bot de Música para Discord com YouTube

Bot de música profissional para Discord que utiliza autenticação do YouTube, desenvolvido com design patterns e arquitetura modular.

## 🚀 Guias Rápidos

> **🗺️ [ÍNDICE COMPLETO](INDICE.md)** - Navegue por toda a documentação

### Para Usuários
- **⚡ [INÍCIO RÁPIDO](INICIO_RAPIDO.md)** - Configure em 5 minutos!
- **🔑 [GUIA DE CREDENCIAIS](GUIA_CREDENCIAIS.md)** - Bot Token vs Client ID/Secret explicado
- **📸 [ONDE ENCONTRAR](ONDE_ENCONTRAR.md)** - Guia visual com screenshots explicativos
- **👤 [OWNER_ID](OWNER_ID.md)** - Como obter seu ID de usuário do Discord
- **📋 [VISUAL RESUMIDO](CREDENCIAIS_VISUAL.txt)** - Resumo em ASCII art
- **❓ [FAQ - Perguntas Frequentes](FAQ.md)** - Soluções para problemas comuns

### Para Desenvolvedores
- **🚀 [SUMÁRIO DE OTIMIZAÇÕES](SUMARIO_OTIMIZACOES.md)** - Visão executiva das melhorias (5min leitura)
- **📊 [GUIA COMPLETO DE OTIMIZAÇÕES](OTIMIZACOES_PERFORMANCE.md)** - Documentação técnica detalhada
- **🔬 28 Melhorias Identificadas** - Performance +400%, Quota -90%, Falhas -85%
- **📖 Documentação Completa** - Continue lendo abaixo

---

## ⚠️ ATENÇÃO: Sobre Client ID e Client Secret

**Se você está aqui porque tem o Client ID e Client Secret do Discord:**

```
❌ Client ID e Client Secret NÃO são usados para bots de música!
✅ Você precisa do BOT TOKEN (aba "Bot" no Developer Portal)

📖 Leia: GUIA_CREDENCIAIS.md para entender a diferença
📸 Veja: ONDE_ENCONTRAR.md para saber onde obter o Bot Token
```

---

## �📋 Características

- 🎵 Reprodução de músicas do YouTube com autenticação OAuth2 ou API Key
- 📝 Sistema de fila completo
- 🔊 Controle de volume
- 🔀 Embaralhamento de fila
- ⏯️ Controles de reprodução (play, pause, skip, stop)
- 🔍 Busca integrada no YouTube
- 📊 Interface com embeds ricos
- 🏗️ Arquitetura modular com Design Patterns

## 🏛️ Arquitetura e Design Patterns

### Patterns Implementados

1. **Singleton Pattern**
   - `Config`: Gerenciamento centralizado de configurações
   - `MusicBot`: Instância única do bot
   - `MusicService`: Gerenciador único de reprodução
   - `YouTubeService`: Serviço único de API do YouTube

2. **Factory Pattern**
   - `LoggerFactory`: Criação de loggers configurados

3. **Strategy Pattern**
   - `YouTubeAuthStrategy`: Estratégias diferentes de autenticação
     - `YouTubeOAuth2Strategy`: Autenticação OAuth2
     - `YouTubeAPIKeyStrategy`: Autenticação via API Key

4. **Command Pattern**
   - Sistema de comandos do Discord.py
   - `MusicCommands`: Implementação dos comandos

5. **Observer Pattern**
   - `MusicPlayer`: Observa e notifica mudanças no estado da reprodução

### Estrutura de Diretórios

```
bot-youtube-disc/
├── config.py              # Configurações centralizadas (Singleton)
├── main.py                # Ponto de entrada da aplicação
├── requirements.txt       # Dependências do projeto
├── .env.example          # Exemplo de configuração
├── core/                 # Núcleo do bot
│   ├── __init__.py
│   ├── bot_client.py     # Cliente do bot (Singleton)
│   └── logger.py         # Factory de loggers (Factory Pattern)
├── services/             # Serviços de negócio
│   ├── __init__.py
│   ├── youtube_service.py # Serviço YouTube (Strategy + Singleton)
│   └── music_service.py   # Serviço de música (Observer + Singleton)
├── handlers/             # Handlers de comandos
│   ├── __init__.py
│   └── music_commands.py  # Comandos de música (Command Pattern)
├── utils/                # Utilitários
└── config/               # Arquivos de configuração
    ├── credentials.json  # Credenciais OAuth2 (não incluído)
    └── token.json        # Token OAuth2 salvo (não incluído)
```

## 🚀 Instalação

### 1. Pré-requisitos

- Python 3.10 ou superior
- FFmpeg instalado no sistema
- Conta Discord Developer Portal
- Conta Google Cloud Platform (para API do YouTube)

#### Instalando FFmpeg

**Windows:**
```powershell
# Usando Chocolatey
choco install ffmpeg

# Ou baixe de: https://ffmpeg.org/download.html
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. Clonar e Configurar

```powershell
# Clone o repositório (se aplicável)
cd C:\Users\Matheus\Documents\projeto\bot-youtube-disc

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configurar Discord Bot

1. **Acesse o Developer Portal**
   - Vá para [Discord Developer Portal](https://discord.com/developers/applications)
   - Selecione sua aplicação existente (ou crie uma nova)
   - Você já tem o **Client ID** na página "General Information"

2. **Obter o Bot Token** (OBRIGATÓRIO)
   - ⚠️ **IMPORTANTE**: Client ID e Client Secret NÃO são suficientes para o bot funcionar
   - Vá na aba **"Bot"** no menu lateral
   - Se não tiver um bot criado, clique em **"Add Bot"**
   - Clique em **"Reset Token"** (ou **"Copy"** se for a primeira vez)
   - Copie o **Bot Token** (formato longo começando com MT...)
   - ⚠️ Este token é mostrado apenas UMA vez! Guarde-o com segurança

3. **Configurar Intents** (OBRIGATÓRIO)
   - Ainda na aba "Bot", role até "Privileged Gateway Intents"
   - Ative as seguintes opções:
     - ✅ **Presence Intent**
     - ✅ **Server Members Intent**
     - ✅ **Message Content Intent** (MUITO IMPORTANTE!)
   - Clique em "Save Changes"

4. **Gerar Link de Convite**
   - Vá em "OAuth2" > "URL Generator"
   - Em **SCOPES**, selecione:
     - ✅ `bot`
     - ✅ `applications.commands`
   - Em **BOT PERMISSIONS**, selecione:
     - ✅ Send Messages
     - ✅ Send Messages in Threads
     - ✅ Embed Links
     - ✅ Attach Files
     - ✅ Read Message History
     - ✅ Add Reactions
     - ✅ Connect (Voice)
     - ✅ Speak (Voice)
     - ✅ Use Voice Activity

5. **Adicionar o Bot ao Servidor**
   - Copie a URL gerada na parte inferior
   - Cole no navegador e selecione seu servidor
   - Autorize as permissões### 4. Configurar YouTube API

#### Opção A: API Key (Mais simples, limitada)

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a "YouTube Data API v3"
4. Vá em "Credenciais" > "Criar credenciais" > "Chave de API"
5. Copie a chave

#### Opção B: OAuth2 (Recomendado, mais funcionalidades)

1. No Google Cloud Console, vá em "Credenciais"
2. "Criar credenciais" > "ID do cliente OAuth 2.0"
3. Tipo: "Aplicativo para computador"
4. Baixe o arquivo JSON
5. Renomeie para `credentials.json`
6. Coloque em `config/credentials.json`

### 5. Configurar Variáveis de Ambiente

```powershell
# Copie o arquivo de exemplo
Copy-Item .env.example .env

# Edite o arquivo .env com suas credenciais
notepad .env
```

**Preencha o arquivo `.env` com suas credenciais:**

```env
# ===== DISCORD (OBRIGATÓRIO) =====
# Cole o BOT TOKEN aqui (não é o Client ID nem Client Secret!)
# Formato: MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz

# Prefixo dos comandos (opcional, padrão: !)
COMMAND_PREFIX=!

# Seu ID de usuário do Discord (opcional, mas recomendado)
# Como obter: Discord > Configurações > Avançado > Ative "Modo Desenvolvedor"
# Depois: Clique direito no seu perfil > Copiar ID
OWNER_ID=123456789012345678

# ===== YOUTUBE (OBRIGATÓRIO - Escolha uma opção) =====
# Opção 1: API Key (mais simples, mas com limites)
YOUTUBE_API_KEY=AIzaSyAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaA

# OU Opção 2: OAuth2 (recomendado, mais funcionalidades)
YOUTUBE_CLIENT_ID=123456789012-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
```

**⚠️ IMPORTANTE:**
- **Discord**: Use o **BOT TOKEN**, não o Client ID ou Client Secret
- **YouTube**: Escolha entre API Key OU OAuth2 (Client ID + Secret)
- Nunca compartilhe estes tokens publicamente!

## 🎮 Uso

### Iniciar o Bot

```powershell
python main.py
```

### Comandos Disponíveis

#### 🎵 Reprodução
- `!play <URL/busca>` ou `!p` - Toca uma música do YouTube
- `!pause` - Pausa/retoma a música atual
- `!skip` ou `!s` - Pula a música atual
- `!stop` - Para a reprodução e limpa a fila

#### 📋 Gerenciamento de Fila
- `!queue` ou `!q` - Mostra a fila de músicas
- `!clear` - Limpa toda a fila
- `!shuffle` - Embaralha a fila

#### ℹ️ Informações
- `!nowplaying` ou `!np` - Mostra a música atual
- `!search <termo>` - Busca músicas no YouTube

#### ⚙️ Configurações
- `!volume <0-100>` ou `!vol` - Ajusta o volume
- `!disconnect` ou `!dc` - Desconecta o bot do canal

#### 📚 Ajuda
- `!help` - Mostra todos os comandos disponíveis

### Exemplos de Uso

```
!play https://www.youtube.com/watch?v=dQw4w9WgXcQ
!play Rick Astley Never Gonna Give You Up
!search lofi hip hop
!volume 50
!queue
!skip
```

## 🔧 Configurações Avançadas

### Arquivo `config.py`

O arquivo `config.py` usa o Singleton Pattern e centraliza todas as configurações:

- **Discord**: Token, prefixo, owner ID
- **YouTube**: Credenciais API/OAuth2
- **Player**: Tamanho da fila, volume padrão, timeout
- **Áudio**: Formato, bitrate, opções FFmpeg
- **Logging**: Nível de log, arquivo de log
- **Cache**: Habilitação e configurações de cache
- **Features**: Flags para habilitar/desabilitar recursos

### Personalização

Edite o arquivo `.env` para personalizar:

```env
COMMAND_PREFIX=?              # Mudar prefixo dos comandos
MAX_QUEUE_SIZE=200           # Aumentar tamanho da fila
DEFAULT_VOLUME=0.7           # Volume padrão (0.0 a 1.0)
LOG_LEVEL=DEBUG              # Mais detalhes no log
ENABLE_PLAYLISTS=True        # Suporte a playlists
```

## 🐛 Troubleshooting

### Erro: "DISCORD_TOKEN não configurado"
- Verifique se o arquivo `.env` existe e contém o token
- Certifique-se de que o token está correto

### Erro: FFmpeg não encontrado
- Instale o FFmpeg e adicione ao PATH do sistema
- Reinicie o terminal após a instalação

### Erro na autenticação do YouTube
- Verifique se as credenciais estão corretas
- Para OAuth2, execute o bot e siga o fluxo de autenticação no navegador
- O token será salvo em `config/token.json`

### Bot não responde aos comandos
- Verifique se o "Message Content Intent" está ativado
- Confirme se o prefixo está correto
- Verifique os logs em `bot.log`

## 📝 Logs

Os logs são salvos em dois locais:
- **Console**: Logs coloridos com nível DEBUG
- **Arquivo**: `bot.log` com nível INFO

## 🔒 Segurança

⚠️ **IMPORTANTE**: Nunca commite arquivos sensíveis!

Adicione ao `.gitignore`:
```gitignore
.env
config/credentials.json
config/token.json
*.log
cache/
__pycache__/
```

## 📦 Dependências Principais

- `discord.py[voice]` - Framework do Discord
- `yt-dlp` - Download/extração de vídeos do YouTube
- `google-api-python-client` - API do Google/YouTube
- `google-auth-oauthlib` - Autenticação OAuth2
- `PyNaCl` - Codec de áudio
- `python-dotenv` - Gerenciamento de variáveis de ambiente
- `colorlog` - Logs coloridos

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é livre para uso pessoal e educacional.

## 👨‍💻 Autor

Desenvolvido com ❤️ usando Design Patterns e boas práticas de desenvolvimento.

## 🙏 Agradecimentos

- Discord.py por fornecer uma excelente biblioteca
- yt-dlp pela extração robusta de vídeos
- Google pela API do YouTube
- Comunidade open source

---

**⚠️ Aviso Legal**: Este bot é apenas para fins educacionais. Respeite os Termos de Serviço do YouTube e do Discord.
