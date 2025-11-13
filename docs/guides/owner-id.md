# 👤 Como Obter Seu OWNER_ID do Discord

## 🎯 O Que É?

O **OWNER_ID** é o seu ID de usuário no Discord. É um número único que identifica você.

**Para que serve:**
- ✅ Identificar o dono do bot
- ✅ Dar permissões especiais
- ✅ Comandos exclusivos de administração (se implementados)
- ⚠️ É **opcional**, mas **recomendado**

---

## 📋 Passo a Passo Visual

### 1️⃣ Ativar Modo Desenvolvedor

```
┌─────────────────────────────────────────────────┐
│  Discord                                        │
│  ┌───────────────────────────────────────────┐ │
│  │  ⚙️ Configurações do Usuário              │ │
│  │                                            │ │
│  │  👤 Minha Conta                            │ │
│  │  🎨 Perfis                                 │ │
│  │  🔒 Privacidade e Segurança                │ │
│  │  ...                                       │ │
│  │  ⚙️ Avançado  ← CLIQUE AQUI               │ │
│  │                                            │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

### 2️⃣ Na Página "Avançado"

```
┌─────────────────────────────────────────────────┐
│  Avançado                                       │
│                                                 │
│  ☑️ Modo Desenvolvedor  ← MARQUE ESTA CAIXA!   │
│     Habilita recursos de desenvolvedor como    │
│     copiar IDs de usuários, servidores, etc.   │
│                                                 │
│  [ ] Permitir depuração de áudio               │
│  [ ] Habilitar ferramentas de debug            │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 3️⃣ Feche as Configurações

### 4️⃣ Copie Seu ID

Você pode copiar seu ID de **3 formas diferentes**:

#### Opção A: No Chat
```
1. Envie uma mensagem em qualquer canal
2. Clique direito no seu nome acima da mensagem
3. Clique em "Copiar ID"
```

#### Opção B: Na Lista de Membros
```
1. Abra a lista de membros do servidor (→)
2. Clique direito no seu nome
3. Clique em "Copiar ID"
```

#### Opção C: No Seu Perfil
```
1. Clique na sua foto/avatar (canto inferior esquerdo)
2. Clique direito em qualquer lugar do popup
3. Clique em "Copiar ID"
```

**Visual do Menu:**
```
┌─────────────────────────────┐
│  Você#1234                  │
│  ├─ Perfil                  │
│  ├─ Mencionar               │
│  ├─ Mensagem                │
│  ├─ Chamar                  │
│  ├─ Adicionar Amigo         │
│  └─ 📋 Copiar ID  ← AQUI!   │
└─────────────────────────────┘
```

---

## ✅ Validação

Depois de copiar, verifique se está correto:

```
✅ Correto:
   - Apenas números
   - 17-19 dígitos
   - Exemplo: 123456789012345678

❌ Errado:
   - Seu nome de usuário: Matheus#1234
   - Nome do servidor
   - Client ID do bot (isso é diferente!)
```

---

## 📝 Usar no .env

Cole o ID copiado no arquivo `.env`:

```env
# Seu ID de usuário do Discord
OWNER_ID=123456789012345678
         ↑
         └─ Cole o número que você copiou (sem aspas, sem espaços)
```

---

## 🔍 Teste Rápido

Para confirmar que está correto, você pode:

1. Abrir o Discord
2. Pressionar `Ctrl + K` (busca rápida)
3. Colar seu OWNER_ID
4. Deve aparecer você mesmo!

---

## ❓ Perguntas Frequentes

### P: Meu ID muda?
**R:** ❌ Não! O ID é permanente e único.

### P: É seguro compartilhar?
**R:** ⚠️ Sim e não:
- ✅ Não é sensível como um token/senha
- ⚠️ Mas revela quem você é no Discord
- 💡 Use com moderação

### P: Posso ter vários OWNER_IDs?
**R:** Neste bot, apenas um. Mas você pode modificar o código para aceitar uma lista.

### P: O que acontece se eu não colocar?
**R:** O bot funciona normalmente! O OWNER_ID é opcional. Só é útil se você implementar comandos exclusivos do dono.

### P: É diferente do ID do bot?
**R:** ✅ SIM! São completamente diferentes:
- **OWNER_ID**: Seu ID pessoal (você como usuário)
- **Bot's Application ID**: ID do bot (aplicação)

---

## 🎨 Exemplo Completo

**Arquivo `.env` preenchido:**

```env
# ==========================================
# DISCORD
# ==========================================
# Bot Token (da aba "Bot" no Developer Portal)
DISCORD_TOKEN=MTIzNDU2Nzg5MDEyMzQ1Njc4OQ.GhIjKl.MnOpQrStUvWxYzAbCdEf

# Prefixo dos comandos
COMMAND_PREFIX=!

# Seu ID de usuário (copiado do Discord com Modo Desenvolvedor)
OWNER_ID=123456789012345678
         ↑
         ├─ 17-19 dígitos
         ├─ Apenas números
         └─ Seu ID pessoal do Discord

# ==========================================
# YOUTUBE
# ==========================================
YOUTUBE_API_KEY=AIzaSyAaAaAaAaAaAaAaAaAaAaAa...
```

---

## 🚀 Resumo Ultra Rápido

```
1. Discord > Configurações > Avançado
2. Ative "Modo Desenvolvedor"
3. Clique direito no seu nome/avatar
4. "Copiar ID"
5. Cole no .env como OWNER_ID=
```

---

**💡 Dica**: Se ainda estiver confuso, assista um vídeo no YouTube pesquisando por "como ativar modo desenvolvedor discord" ou "how to get discord user id".
