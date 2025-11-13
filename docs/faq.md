# ❓ Perguntas Frequentes (FAQ)

## 🔑 Credenciais e Autenticação

### P: Eu tenho o Client ID e Client Secret do Discord. Onde uso isso?

**R:** ❌ **Você NÃO usa!** Client ID e Client Secret do Discord são para OAuth2 (quando usuários fazem login com Discord em sites). Para bots, você precisa do **Bot Token**.

**Como obter o Bot Token:**
1. Discord Developer Portal → Sua aplicação
2. Aba **"Bot"** (não "OAuth2"!)
3. Copie o **Token**
4. Cole no `.env` como `DISCORD_TOKEN=`

📖 **Leia mais**: [GUIA_CREDENCIAIS.md](GUIA_CREDENCIAIS.md)

---

### P: Qual é a diferença entre Client ID, Client Secret e Bot Token?

**R:**

| Item | Client ID | Client Secret | Bot Token |
|------|-----------|---------------|-----------|
| **Aba no Portal** | General Info / OAuth2 | OAuth2 | **Bot** ⭐ |
| **Para que serve** | ID público da app | Login de usuários | **Autenticar bot** |
| **Necessário?** | ❌ Não | ❌ Não | ✅ **SIM!** |
| **Formato** | Números | String curta | `MT...ponto.ponto...` |
| **Usar neste bot** | Não | Não | **DISCORD_TOKEN** |

---

### P: O bot dá erro "Invalid Token". O que fazer?

**R:** Verifique:

1. ✅ Você copiou o **Bot Token** (aba "Bot"), não Client ID/Secret?
2. ✅ O token está no formato `MT...ponto.ponto...`?
3. ✅ Copiou o token COMPLETO (sem espaços extras)?
4. ✅ O arquivo se chama `.env` (não `.env.txt`)?
5. ✅ O token não foi resetado após você copiar?

**Se o token estiver errado:** Vá em Developer Portal → Bot → Reset Token

---

### P: Como obter meu OWNER_ID?

**R:** O OWNER_ID é o seu ID de usuário do Discord (opcional, mas recomendado):

**Passo a passo:**
1. No Discord, vá em **Configurações** (⚙️)
2. **Avançado** → Ative **"Modo Desenvolvedor"**
3. Feche as configurações
4. Clique com botão direito no **SEU perfil/avatar** (em qualquer lugar)
5. Clique em **"Copiar ID"**
6. Cole no `.env` como `OWNER_ID=`

**Formato:**
- ✅ Apenas números (17-19 dígitos)
- ✅ Exemplo: `123456789012345678`
- ❌ NÃO é seu nome de usuário
- ❌ NÃO é o Client ID do bot

**Para que serve:**
- Identificar o dono do bot
- Dar permissões especiais
- Comandos exclusivos de administração (se implementados)

---

### P: Preciso de credenciais do YouTube também?

**R:** ✅ **SIM!** Escolha **UMA** das opções:

**Opção 1 - API Key (mais simples):**
- Google Cloud Console → Credenciais → Chave de API
- Cole no `.env` como `YOUTUBE_API_KEY=`

**Opção 2 - OAuth2 (recomendado):**
- Google Cloud Console → Credenciais → OAuth 2.0
- Baixe o JSON e coloque em `config/credentials.json`
- OU cole as credenciais no `.env`:
  - `YOUTUBE_CLIENT_ID=`
  - `YOUTUBE_CLIENT_SECRET=`

---

## 🎵 Funcionamento do Bot

### P: O bot não responde aos comandos. Por quê?

**R:** 99% dos casos é por causa do **Message Content Intent**!

**Solução:**
1. Discord Developer Portal → Sua App → Aba "Bot"
2. Role até "Privileged Gateway Intents"
3. ✅ Ative **"Message Content Intent"**
4. Clique em **"Save Changes"**
5. **Reinicie o bot**

Outros pontos a verificar:
- ✅ Bot tem permissão para ler/enviar mensagens?
- ✅ Prefixo está correto? (padrão: `!`)
- ✅ Bot está online no servidor?

---

### P: O bot conecta mas não toca música. O que pode ser?

**R:** Provavelmente falta o **FFmpeg**!

**Instalar FFmpeg:**

**Windows:**
```powershell
choco install ffmpeg
# OU baixe de: https://ffmpeg.org/download.html
```

**Linux:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**⚠️ Após instalar, reinicie o terminal e o bot!**

---

### P: O bot entra no canal mas não reproduz áudio

**R:** Verifique:

1. ✅ FFmpeg instalado e no PATH?
2. ✅ Bot tem permissão de "Connect" e "Speak" no canal?
3. ✅ Você está no mesmo canal que o bot?
4. ✅ O vídeo do YouTube está disponível (não privado/bloqueado)?
5. ✅ Não há erros no arquivo `bot.log`?

---

### P: O bot dá erro ao buscar vídeos do YouTube

**R:** Problema com as credenciais do YouTube:

1. ✅ API Key ou OAuth2 configurados no `.env`?
2. ✅ YouTube Data API v3 está ativada no Google Cloud?
3. ✅ A chave API não atingiu o limite de uso?
4. ✅ Para OAuth2: arquivo `config/credentials.json` existe?

**Dica:** Use OAuth2 em vez de API Key para limites maiores.

---

## ⚙️ Configuração

### P: Como mudar o prefixo dos comandos?

**R:** Edite o arquivo `.env`:

```env
COMMAND_PREFIX=?
```

Agora os comandos serão: `?play`, `?pause`, etc.

---

### P: Como adicionar o bot ao meu servidor?

**R:**

1. Discord Developer Portal → Sua App → OAuth2 → URL Generator
2. Marque: ✅ `bot` e ✅ `applications.commands`
3. Permissões necessárias:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Connect (Voice)
   - ✅ Speak (Voice)
   - ✅ Use Voice Activity
4. Copie a URL gerada
5. Cole no navegador e autorize

**Dica:** Pode marcar "Administrator" para dar todas as permissões.

---

### P: O bot funciona em vários servidores ao mesmo tempo?

**R:** ✅ **SIM!** O bot pode estar em múltiplos servidores e gerencia filas independentes para cada um.

---

### P: Como ver os logs do bot?

**R:** Os logs são salvos em:
- **Console**: Logs coloridos em tempo real
- **Arquivo**: `bot.log` (na pasta raiz do projeto)

Para ver mais detalhes, edite o `.env`:
```env
LOG_LEVEL=DEBUG
```

---

## 🐛 Problemas Comuns

### P: "ModuleNotFoundError: No module named 'discord'"

**R:** Dependências não instaladas. Execute:

```powershell
pip install -r requirements.txt
```

---

### P: "discord.errors.PrivilegedIntentsRequired"

**R:** Faltou ativar os Intents!

Discord Developer Portal → Bot → Privileged Gateway Intents:
- ✅ Presence Intent
- ✅ Server Members Intent
- ✅ Message Content Intent ⭐

Salve e reinicie o bot.

---

### P: O bot sai do canal sozinho após um tempo

**R:** Comportamento normal! O bot desconecta após `TIMEOUT_SECONDS` segundos de inatividade (padrão: 300s = 5 minutos).

Para mudar, edite o `.env`:
```env
TIMEOUT_SECONDS=600  # 10 minutos
```

---

### P: A música está cortando/com lag

**R:** Possíveis causas:

1. **Internet lenta**: Necessita boa conexão
2. **CPU sobrecarregada**: Feche outros programas
3. **Bitrate muito alto**: Reduza no `.env`:
   ```env
   BITRATE=128
   ```
4. **Discord rate limit**: Aguarde alguns segundos

---

### P: "Too many requests" ou "Rate limited"

**R:** API do YouTube atingiu o limite de requisições.

**Soluções:**
- Use OAuth2 em vez de API Key (limites maiores)
- Aguarde alguns minutos
- Crie uma nova API Key se necessário

---

## 🔧 Personalização

### P: Como mudar o volume padrão?

**R:** Edite o `.env`:

```env
DEFAULT_VOLUME=0.7  # 70% (0.0 a 1.0)
```

---

### P: Como aumentar o tamanho da fila?

**R:** Edite o `.env`:

```env
MAX_QUEUE_SIZE=200  # Permite até 200 músicas na fila
```

---

### P: Como desabilitar playlists?

**R:** Edite o `.env`:

```env
ENABLE_PLAYLISTS=False
```

---

### P: Como adicionar novos comandos?

**R:** Edite `handlers/music_commands.py` e adicione:

```python
@commands.command(name='meucomando')
async def meu_comando(self, ctx: commands.Context):
    """Descrição do comando"""
    await ctx.send("Resposta do comando!")
```

---

## 📦 Instalação e Deploy

### P: Posso hospedar o bot 24/7?

**R:** ✅ **SIM!** Opções:

**Gratuitas:**
- Render.com (com limitações)
- Railway.app (créditos gratuitos)
- Replit (com limitações)

**Pagas:**
- AWS EC2
- Google Cloud Compute
- DigitalOcean
- Heroku

**Servidor próprio:**
- PC/notebook ligado 24/7
- Raspberry Pi
- VPS

---

### P: Funciona no Linux/macOS?

**R:** ✅ **SIM!** O bot é multiplataforma.

Ajuste apenas a instalação do FFmpeg:
- **Linux**: `sudo apt install ffmpeg`
- **macOS**: `brew install ffmpeg`

---

### P: Preciso do Python instalado?

**R:** ✅ **SIM!**

- Python 3.10 ou superior
- Baixe em: https://www.python.org/downloads/

---

## 🔒 Segurança

### P: É seguro compartilhar o Client ID?

**R:** ✅ **SIM**, Client ID é público.

❌ **NÃO** compartilhe:
- Bot Token
- Client Secret
- API Keys
- Arquivo `.env`

---

### P: Meu token vazou! O que fazer?

**R:** 🚨 **AÇÃO IMEDIATA:**

1. Discord Developer Portal → Bot → **Reset Token**
2. Atualize o `.env` com o novo token
3. Reinicie o bot
4. Se postou no GitHub: delete o repositório e crie novo (ou use git history rewrite)

---

### P: Como proteger minhas credenciais?

**R:**

1. ✅ Nunca commite o arquivo `.env`
2. ✅ Use `.gitignore` (já incluído no projeto)
3. ✅ Não tire screenshots com tokens visíveis
4. ✅ Use variáveis de ambiente em produção
5. ✅ Resete tokens regularmente

---

## 📚 Outros

### P: O bot é gratuito?

**R:** ✅ **SIM!** O código é open source e gratuito.

Custos possíveis:
- Hosting (se quiser 24/7 em servidor pago)
- Limites da API do YouTube (use OAuth2 para limites maiores)

---

### P: Posso modificar o código?

**R:** ✅ **SIM!** O código é livre para modificação e uso pessoal/educacional.

---

### P: Como contribuir com o projeto?

**R:**

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/MinhaFeature`
3. Commit: `git commit -m 'Add MinhaFeature'`
4. Push: `git push origin feature/MinhaFeature`
5. Abra um Pull Request

---

### P: Onde reportar bugs?

**R:**

1. Verifique os logs em `bot.log`
2. Procure no FAQ se já tem solução
3. Abra uma issue no GitHub (se aplicável)
4. Inclua:
   - Descrição do problema
   - Logs relevantes
   - Passos para reproduzir

---

### P: Quais comandos estão disponíveis?

**R:** No Discord, digite: `!help`

Principais comandos:
- `!play <música>` - Tocar música
- `!pause` - Pausar/retomar
- `!skip` - Pular música
- `!queue` - Ver fila
- `!volume <0-100>` - Ajustar volume
- `!search <termo>` - Buscar no YouTube

📖 **Lista completa**: [README.md](README.md#comandos-disponíveis)

---

## 📞 Ainda Precisa de Ajuda?

1. 📖 Leia [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
2. 🔑 Leia [GUIA_CREDENCIAIS.md](GUIA_CREDENCIAIS.md)
3. 📸 Leia [ONDE_ENCONTRAR.md](ONDE_ENCONTRAR.md)
4. 📋 Veja [CREDENCIAIS_VISUAL.txt](CREDENCIAIS_VISUAL.txt)
5. 📖 Consulte a documentação completa no [README.md](README.md)

---

**💡 Dica:** 90% dos problemas são resolvidos com:
1. ✅ Usar o Bot Token correto (aba "Bot", não OAuth2)
2. ✅ Ativar Message Content Intent
3. ✅ Instalar FFmpeg
