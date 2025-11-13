# 🔑 Guia de Credenciais - Discord vs YouTube

## ⚠️ IMPORTANTE: Discord Bot Token vs Client ID/Secret

### 🤖 Para o Discord

Você precisa de **3 informações diferentes** da sua aplicação no Discord:

#### 1️⃣ Client ID (Application ID)
- **Onde encontrar**: Discord Developer Portal > Sua App > "General Information"
- **Para que serve**: Identificador público da sua aplicação
- **Formato**: Número grande (ex: `1234567890123456789`)
- **Usado para**: Links de convite, OAuth2 para usuários
- ❌ **NÃO é suficiente para o bot funcionar!**

#### 2️⃣ Client Secret
- **Onde encontrar**: Discord Developer Portal > Sua App > "OAuth2" > "Client Secret"
- **Para que serve**: OAuth2 quando usuários fazem login com Discord
- **Formato**: String alfanumérica (ex: `aBcDeF1234567890`)
- ❌ **NÃO é usado para bots de música!**

#### 3️⃣ Bot Token (BOT TOKEN) ⭐ ESTE QUE VOCÊ PRECISA!
- **Onde encontrar**: Discord Developer Portal > Sua App > **"Bot"** > "Token"
- **Para que serve**: Autenticar o BOT no Discord
- **Formato**: String longa (ex: `MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYz`)
- ✅ **ESTE é o token que vai no `.env`!**
- ⚠️ **Mostrado apenas UMA vez!** Copie e guarde com segurança

---

## 📝 Como Obter o Bot Token Passo a Passo

### Passo 1: Acesse o Developer Portal
```
1. Abra: https://discord.com/developers/applications
2. Faça login com sua conta Discord
3. Selecione sua aplicação (você já criou uma)
```

### Passo 2: Vá na Aba "Bot"
```
1. No menu lateral esquerdo, clique em "Bot"
2. Se não tiver um bot criado, clique em "Add Bot" e confirme
```

### Passo 3: Obtenha o Token
```
1. Na seção "TOKEN", você verá "Click to Reveal Token" ou um botão "Reset Token"
2. Clique em "Copy" ou "Reset Token" (se já foi revelado antes)
3. COPIE o token imediatamente - ele não será mostrado novamente!
```

### Passo 4: Configure no .env
```env
# Cole o token copiado aqui:
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYz
```

---

## 👤 Como Obter Seu OWNER_ID (Opcional)

O OWNER_ID é o seu ID de usuário do Discord. É opcional, mas recomendado para identificar o dono do bot.

### Passo a passo:
```
1. Abra o Discord
2. Vá em Configurações (⚙️)
3. Avançado > Ative "Modo Desenvolvedor"
4. Feche as configurações
5. Clique direito no SEU perfil/avatar (em qualquer lugar)
6. Clique em "Copiar ID"
7. Pronto! Este é seu OWNER_ID
```

### Formato:
- ✅ Apenas números (17-19 dígitos)
- ✅ Exemplo: `123456789012345678`
- ❌ NÃO é seu nome de usuário (ex: "Matheus#1234")
- ❌ NÃO é o Client ID do bot

### No .env:
```env
OWNER_ID=123456789012345678
```

---

## 🎯 Resumo: O que vai onde

### No arquivo `.env`:

```env
# ============================================
# DISCORD - Use o BOT TOKEN (da aba "Bot")
# ============================================
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYz

# Seu ID de usuário (opcional)
OWNER_ID=123456789012345678

# ============================================
# YOUTUBE - Escolha UMA das opções abaixo
# ============================================

# Opção 1: API Key (mais simples)
YOUTUBE_API_KEY=AIzaSyAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaA

# OU Opção 2: OAuth2 (mais funcionalidades)
YOUTUBE_CLIENT_ID=123456789012-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
```

---

## 🆚 Comparação Visual

| Item | Client ID | Client Secret | Bot Token |
|------|-----------|---------------|-----------|
| **Onde?** | General Info | OAuth2 | **Bot** ⭐ |
| **Formato** | Números | String curta | String longa |
| **Uso** | Links, OAuth2 | OAuth2 usuários | **Autenticar BOT** ⭐ |
| **Necessário?** | ❌ Não | ❌ Não | ✅ **SIM!** |
| **No .env?** | Não precisa | Não precisa | **DISCORD_TOKEN** |

---

## ❓ Perguntas Frequentes

### P: Posso usar Client ID e Client Secret no lugar do Bot Token?
**R:** ❌ **NÃO!** Eles têm propósitos diferentes:
- **Client ID/Secret**: Para OAuth2 quando USUÁRIOS fazem login
- **Bot Token**: Para o BOT se conectar ao Discord

### P: Já tenho o Client ID e Client Secret. Onde está o Bot Token?
**R:** Vá na aba **"Bot"** (não "OAuth2") e copie o token de lá.

### P: Perdi meu Bot Token, como recupero?
**R:** Vá em Discord Developer Portal > Sua App > Bot > "Reset Token".
⚠️ Isso invalida o token anterior!

### P: O bot não conecta, diz "Invalid Token"
**R:** Verifique:
1. Você copiou o **Bot Token** (não Client ID/Secret)
2. Copiou corretamente (sem espaços extras)
3. O token não foi resetado/invalidado

### P: Preciso ativar algo mais?
**R:** ✅ Sim! Na aba "Bot", ative:
- ✅ Presence Intent
- ✅ Server Members Intent
- ✅ **Message Content Intent** (MUITO IMPORTANTE!)

---

## 🔒 Segurança

### ⚠️ NUNCA compartilhe:
- ❌ Bot Token
- ❌ Client Secret (se usar)
- ❌ YouTube Client Secret (se usar OAuth2)

### ✅ Pode compartilhar:
- ✅ Client ID (Application ID) - é público
- ✅ Link de convite do bot

### 🛡️ Se o token vazar:
1. Vá IMEDIATAMENTE em Developer Portal > Bot
2. Clique em "Reset Token"
3. Atualize o `.env` com o novo token
4. Reinicie o bot

---

## 📞 Ainda com dúvidas?

Se após seguir este guia você ainda não conseguir:

1. ✅ Confirme que está na aba **"Bot"** (não "OAuth2")
2. ✅ Confirme que copiou o token COMPLETO
3. ✅ Confirme que o token está no formato correto (começa com MT...)
4. ✅ Confirme que ativou os Intents necessários
5. ✅ Tente resetar o token e copiar novamente

---

**Lembre-se**: Para o bot funcionar no Discord, você precisa do **BOT TOKEN** da aba "Bot"! 🤖
