# 📸 Onde Encontrar Cada Credencial - Guia Visual

## 🎮 Discord Developer Portal

### 🔍 Passo 1: Acessar o Portal

```
URL: https://discord.com/developers/applications

Após fazer login, você verá:
┌─────────────────────────────────────────────────┐
│  My Applications                                │
│  ┌───────────────────────┐                     │
│  │  📱 Sua Aplicação      │  <-- Clique aqui   │
│  │  Application ID: 123...│                     │
│  └───────────────────────────┘                  │
└─────────────────────────────────────────────────┘
```

---

### 📍 Passo 2: Navegar até a Aba "Bot"

No menu lateral esquerdo, você verá:

```
┌────────────────────────────┐
│ 🏠 General Information     │
│ 🤖 Bot                     │  <-- ⭐ CLIQUE AQUI! ⭐
│ 🔐 OAuth2                  │
│ 📊 Analytics               │
│ ⚙️ Settings                │
└────────────────────────────┘
```

**⚠️ NÃO confunda:**
- ❌ **OAuth2** → Client ID e Client Secret (não é o que você quer!)
- ✅ **Bot** → Bot Token (ESTE que você precisa!)

---

### 🎯 Passo 3: Copiar o Bot Token

Na página "Bot", você verá:

```
┌──────────────────────────────────────────────────────────┐
│  Bot                                                      │
│                                                           │
│  [Foto do Bot]  Nome do Bot                              │
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  TOKEN                                            │   │
│  │  ┌────────────────────────────────────────────┐  │   │
│  │  │ MT...••••••••••••••••••••••••••  [Copy] 📋│  │   │
│  │  └────────────────────────────────────────────┘  │   │
│  │                                                   │   │
│  │  [Reset Token]  [Regenerate]                     │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Clique em "Copy" ou "Reset Token"** para revelar e copiar.

**Formato do token:**
```
MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEfGhIjKlMnOpQrStUvWxYz
│                           │      │
├─ Parte 1                  ├ .    ├─ Parte 3
└─ ID codificado            └ .    └─ Assinatura
                             └─ Parte 2
```

---

### ✅ Passo 4: Ativar Intents (CRÍTICO!)

Role para baixo na mesma página "Bot":

```
┌──────────────────────────────────────────────────────────┐
│  Privileged Gateway Intents                               │
│                                                           │
│  ⚠️ These intents are privileged...                       │
│                                                           │
│  ☑️ PRESENCE INTENT                                       │
│     Allows your bot to receive presence update events.   │
│                                                           │
│  ☑️ SERVER MEMBERS INTENT                                 │
│     Allows your bot to receive member update events.     │
│                                                           │
│  ☑️ MESSAGE CONTENT INTENT ⭐⭐⭐ OBRIGATÓRIO!            │
│     Allows your bot to receive message content.          │
│                                                           │
│  [Save Changes]  <-- ⚠️ NÃO ESQUEÇA DE SALVAR!           │
└──────────────────────────────────────────────────────────┘
```

**SEM Message Content Intent o bot NÃO VAI FUNCIONAR!**

---

## 🚫 O Que NÃO Usar

### ❌ Aba "General Information" (Application ID / Client ID)

```
┌──────────────────────────────────────────────────────────┐
│  General Information                                      │
│                                                           │
│  APPLICATION ID                                           │
│  1234567890123456789  [Copy]                             │
│  ↑                                                        │
│  └─ Este é o Client ID (público)                         │
│     ❌ NÃO é o Bot Token!                                │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Este número:**
- ✅ Serve para links de convite
- ✅ É público, pode compartilhar
- ❌ NÃO autentica o bot
- ❌ NÃO vai no .env

---

### ❌ Aba "OAuth2" (Client Secret)

```
┌──────────────────────────────────────────────────────────┐
│  OAuth2                                                   │
│                                                           │
│  CLIENT ID                                                │
│  1234567890123456789  [Copy]                             │
│  ↑                                                        │
│  └─ Mesmo que Application ID                             │
│                                                           │
│  CLIENT SECRET                                            │
│  aBcDeF1234567890  [Reset]                               │
│  ↑                                                        │
│  └─ Para OAuth2 de USUÁRIOS                              │
│     ❌ NÃO é usado para bots de música!                  │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

**Client ID e Client Secret** são para:
- 🔐 Login de usuários com Discord ("Login with Discord")
- 🌐 Aplicações web que precisam acessar conta de usuários
- ❌ **NÃO** são para bots!

---

## ✅ Resumo Visual: Onde Está o Que

```
Discord Developer Portal
│
├─ 🏠 General Information
│   └─ Application ID (Client ID)
│       → ❌ NÃO é o Bot Token
│       → Só serve para links
│
├─ 🤖 Bot ⭐⭐⭐ AQUI QUE VOCÊ QUER! ⭐⭐⭐
│   ├─ TOKEN
│   │   └─ ✅ BOT TOKEN (use este!)
│   │       → Formato: MT...GhIjKl...MnOp
│   │       → Cole no .env como DISCORD_TOKEN=
│   │
│   └─ Privileged Gateway Intents
│       └─ ✅ Ative Message Content Intent
│
└─ 🔐 OAuth2
    ├─ Client ID (mesmo que Application ID)
    └─ Client Secret
        → ❌ NÃO são usados neste bot
        → Só para login de usuários
```

---

## 📝 Arquivo .env Final

Depois de obter as credenciais, seu `.env` deve ficar assim:

```env
# =======================================
# DISCORD - Bot Token (da aba "Bot")
# =======================================
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEf
               ↑
               └─ Token COMPLETO copiado da aba "Bot"

COMMAND_PREFIX=!

OWNER_ID=123456789012345678
          ↑
          └─ SEU ID de usuário do Discord
             (Clique direito no seu perfil > Copiar ID)
             (Ative "Modo Desenvolvedor" nas configurações primeiro)

# =======================================
# YOUTUBE - Escolha UMA opção
# =======================================

# Opção 1: API Key (simples)
YOUTUBE_API_KEY=AIzaSyAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaA

# OU Opção 2: OAuth2 (recomendado)
YOUTUBE_CLIENT_ID=123456789012-abc...xyz.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
```

---

## � Como Obter Seu OWNER_ID (Opcional mas Recomendado)

O OWNER_ID é o seu ID de usuário do Discord. Serve para dar permissões especiais e identificar o dono do bot.

### Método 1: Modo Desenvolvedor (Mais Fácil)

```
1. Abra o Discord
2. Configurações (⚙️) > Avançado > Ative "Modo Desenvolvedor"
3. Feche as configurações
4. Clique com botão direito no SEU nome/avatar em qualquer lugar
5. Clique em "Copiar ID"
6. Você copiou seu OWNER_ID!
```

**Visual:**
```
┌─────────────────────────────────────┐
│  Discord > Configurações            │
│                                     │
│  ⚙️ Avançado                         │
│     ☑️ Modo Desenvolvedor  <-- ATIVE│
│                                     │
└─────────────────────────────────────┘

Depois, clique direito no seu perfil:
┌─────────────────────────────────────┐
│  👤 Seu Nome#1234                   │
│  ├─ Perfil                          │
│  ├─ Mencionar                       │
│  ├─ Mensagem                        │
│  └─ 📋 Copiar ID  <-- CLIQUE AQUI   │
└─────────────────────────────────────┘
```

### Método 2: Via Navegador/App

```
1. Abra o Discord (web ou desktop)
2. Vá para qualquer servidor
3. Ative "Modo Desenvolvedor" nas configurações
4. Clique direito no seu perfil/avatar
5. "Copiar ID"
```

### Formato do OWNER_ID

```
✅ OWNER_ID correto:
   - Apenas números
   - 17-19 dígitos
   - Exemplo: 123456789012345678

❌ NÃO é OWNER_ID:
   - Seu nome de usuário (ex: "Matheus#1234")
   - Client ID do bot
   - Token do bot
```

### Usar no .env

```env
OWNER_ID=123456789012345678
         ↑
         └─ Seu ID copiado (apenas números)
```

---

## �🔍 Como Identificar Se Você Tem o Token Certo

### ✅ Bot Token Correto

```
✅ Começa com "MT" ou "MU" ou "MN"
✅ Tem dois pontos (.) separando três partes
✅ É bem longo (70+ caracteres)
✅ Exemplo: MTIzNDU2Nzg5.GhIjKl.MnOpQrStUv...

Formato: XXXXX.YYYYY.ZZZZZ
         │     │     └─ Assinatura
         │     └─ Timestamp
         └─ ID do bot codificado
```

### ❌ NÃO é Bot Token

```
❌ Apenas números (Application ID / Client ID)
   Exemplo: 1234567890123456789

❌ String curta sem pontos (Client Secret)
   Exemplo: aBcDeF1234567890XyZ

❌ Formato de API Key do YouTube
   Exemplo: AIzaSyAaAaAaAaAaAa...
```

---

## 🆘 Checklist Final

Antes de executar o bot, confirme:

- [ ] Fui na aba **"Bot"** (não "OAuth2")
- [ ] Copiei o **Token** (não Client ID/Secret)
- [ ] O token tem formato `MT...ponto.ponto...`
- [ ] Colei no `.env` como `DISCORD_TOKEN=`
- [ ] Ativei **Message Content Intent**
- [ ] Salvei as alterações no Developer Portal
- [ ] Tenho credenciais do YouTube configuradas
- [ ] FFmpeg está instalado
- [ ] Executei `pip install -r requirements.txt`

**Tudo OK?** → `python main.py` 🚀

---

## 📞 Ainda Com Dúvidas?

Se você:
- ✅ Foi na aba "Bot"
- ✅ Copiou o token completo (formato MT...ponto.ponto...)
- ✅ Ativou Message Content Intent
- ✅ Salvou no .env corretamente

E mesmo assim não funciona, verifique:
1. Token não tem espaços extras no início/fim
2. Arquivo se chama `.env` (não `.env.txt`)
3. Arquivo está na pasta raiz do projeto
4. Reiniciou o bot após salvar

---

**💡 Lembre-se**: O Bot Token fica na aba "Bot", não em "OAuth2"!
