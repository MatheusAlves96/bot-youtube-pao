# 🚀 Início Rápido - 5 Minutos

## ⚡ Configuração Express

### 1️⃣ Obter Bot Token do Discord (2 min)

```
🌐 Abra: https://discord.com/developers/applications
📱 Selecione sua aplicação (você já tem uma)
🤖 Clique na aba "Bot" (menu lateral)
🔑 Clique em "Reset Token" ou "Copy"
📋 Copie o token completo
```

**⚠️ ATENÇÃO**: Você precisa do **BOT TOKEN** (da aba "Bot"), NÃO do Client ID ou Client Secret!

### 2️⃣ Ativar Intents (30 seg)

Na mesma página "Bot", role até **"Privileged Gateway Intents"**:

```
✅ Presence Intent
✅ Server Members Intent
✅ Message Content Intent ⭐ IMPORTANTE!
```

Clique em **"Save Changes"**

### 3️⃣ Obter Seu OWNER_ID (30 seg - Opcional)

```
👤 No Discord:
1. Configurações > Avançado > Ative "Modo Desenvolvedor"
2. Clique direito no SEU nome/avatar
3. Clique em "Copiar ID"
4. Pronto! Este é seu OWNER_ID
```

### 4️⃣ Configurar o Bot (1 min)

```powershell
# Copie o arquivo de exemplo
Copy-Item .env.example .env

# Abra para editar
notepad .env
```

**Cole SEU bot token e OWNER_ID:**
```env
DISCORD_TOKEN=cole_seu_bot_token_aqui
OWNER_ID=cole_seu_id_aqui

# Para YouTube, escolha uma opção:
# Opção simples (API Key):
YOUTUBE_API_KEY=sua_chave_api_aqui

# OU Opção avançada (OAuth2):
YOUTUBE_CLIENT_ID=seu_client_id_aqui
YOUTUBE_CLIENT_SECRET=seu_client_secret_aqui
```

### 5️⃣ Instalar Dependências (1 min)

```powershell
# Instalar FFmpeg (necessário para áudio)
choco install ffmpeg
# OU baixe de: https://ffmpeg.org/download.html

# Instalar pacotes Python
pip install -r requirements.txt
```

### 6️⃣ Adicionar Bot ao Servidor (30 seg)

```
🌐 Discord Developer Portal > Sua App > "OAuth2" > "URL Generator"
✅ Marque: bot, applications.commands
✅ Permissões: Administrator (ou selecione manualmente)
🔗 Copie a URL gerada
🌐 Cole no navegador e autorize
```

### 7️⃣ Executar! (10 seg)

```powershell
python main.py
```

---

## ✅ Teste Rápido

No Discord, digite:

```
!help        # Ver todos os comandos
!play lofi   # Testar reprodução
```

---

## ❌ Problemas Comuns

### "Invalid Token"
- ✅ Você copiou o **Bot Token** (aba "Bot"), não Client ID?
- ✅ Copiou o token completo (sem espaços)?
- ✅ O token não foi resetado depois?

### "Message Content Intent"
- ✅ Você ativou "Message Content Intent" na aba "Bot"?
- ✅ Salvou as alterações?
- ✅ Reiniciou o bot depois de ativar?

### "FFmpeg not found"
- ✅ FFmpeg está instalado?
- ✅ Reiniciou o terminal após instalar?
- ✅ FFmpeg está no PATH?

### Bot não responde
- ✅ Message Content Intent ativado? (PRINCIPAL)
- ✅ Bot tem permissões no servidor?
- ✅ Prefixo está correto? (padrão: `!`)
- ✅ Olhe os logs no arquivo `bot.log`

---

## 📚 Mais Informações

- **Dúvidas sobre tokens**: Leia `GUIA_CREDENCIAIS.md`
- **Documentação completa**: Leia `README.md`
- **Comandos disponíveis**: Digite `!help` no Discord

---

## 🎯 Checklist Completo

Antes de executar, confirme:

- [ ] Tenho o **Bot Token** (formato: MT...GhIjKl...MnOp...)
- [ ] Copiei para o arquivo `.env` na linha `DISCORD_TOKEN=`
- [ ] (Opcional) Tenho meu **OWNER_ID** (clique direito no perfil > Copiar ID)
- [ ] Ativei **Message Content Intent** no Developer Portal
- [ ] Tenho credenciais do YouTube (API Key OU OAuth2)
- [ ] FFmpeg está instalado
- [ ] Executei `pip install -r requirements.txt`
- [ ] Bot foi adicionado ao meu servidor
- [ ] Bot tem permissões para ver e enviar mensagens

**Tudo OK?** Execute: `python main.py` 🚀

---

**💡 Dica**: Se ainda tiver dúvidas sobre qual token usar, leia o arquivo `GUIA_CREDENCIAIS.md` - ele explica TUDO em detalhes!
