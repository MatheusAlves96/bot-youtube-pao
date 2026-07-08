# 🍪 Guia de Cookies do YouTube

## Problema

O YouTube bloqueia o yt-dlp com a mensagem:
```
ERROR: Sign in to confirm you're not a bot
```

Isso acontece porque o YouTube detecta que é um bot fazendo download. A solução é usar cookies do seu navegador (autenticado).

---

## 🎯 Solução Rápida (5 minutos)

### 1️⃣ Instalar extensão para extrair cookies

#### Google Chrome/Edge/Brave
1. Instalar extensão: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)

#### Firefox
1. Instalar extensão: [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)

### 2️⃣ Fazer login no YouTube
1. Abra o YouTube no navegador: https://youtube.com
2. Faça login com sua conta Google
3. Acesse qualquer vídeo (para garantir que os cookies estão ativos)

### 3️⃣ Exportar cookies
1. Clique no ícone da extensão (canto superior direito)
2. Clique em "Export" ou "Get cookies.txt"
3. Salve o arquivo como `cookies.txt`

### 4️⃣ Copiar cookies para o servidor

#### Windows (local) → Linux (servidor)
```powershell
scp cookies.txt seu_usuario@seu_servidor:/caminho/bot/cookies.txt
```

#### Ou copiar manualmente via SSH
```bash
# No servidor
cd ~/bot-discord-youtube
nano cookies.txt
# Cole o conteúdo completo do arquivo
# Ctrl+X, Y, Enter para salvar
```

### 5️⃣ Ajustar permissões no servidor
```bash
chmod 600 cookies.txt  # Somente você pode ler/escrever
```

---

## ⚙️ Configurar Bot para Usar Cookies

### Opção 1: Variável de ambiente (Recomendado)

Edite o arquivo `.env` no servidor:
```bash
nano .env
```

Adicione:
```env
# Cookies do YouTube (evita bloqueio de bot)
YTDL_COOKIES_PATH=cookies.txt
```

Salve (Ctrl+X, Y, Enter) e reinicie o bot:
```bash
python3 main.py
```

### Opção 2: Editar config.py diretamente

Se preferir não usar `.env`:

```bash
nano config.py
```

Encontre a função `get_ytdl_options()` e adicione `'cookiefile'`:

```python
def get_ytdl_options():
    """Configurações do yt-dlp"""
    return {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'cookiefile': 'cookies.txt',  # ← ADICIONAR ESTA LINHA
        # ... resto das configurações ...
    }
```

---

## ✅ Testar

Após configurar, execute o bot:
```bash
python3 main.py
```

E teste no Discord:
```
!play nome da música
```

Se funcionou, você verá:
```
✅ Música extraída sem erros
🎵 Tocando agora: [nome da música]
```

---

## 🔄 Manutenção

### Atualizar cookies (a cada 30-90 dias)

Os cookies do YouTube expiram periodicamente. Se o erro voltar:

1. Refaça os passos 2️⃣ e 3️⃣ (fazer login e exportar cookies)
2. Copie o novo `cookies.txt` para o servidor
3. Reinicie o bot

### Monitorar expiração

O bot continuará funcionando até os cookies expirarem. Quando isso acontecer, você verá o erro original novamente:
```
ERROR: Sign in to confirm you're not a bot
```

Solução: Repetir o processo de exportação de cookies.

---

## 🛡️ Segurança

### ⚠️ IMPORTANTE: Não compartilhe cookies.txt

O arquivo `cookies.txt` contém suas credenciais de autenticação do YouTube. **NUNCA**:
- ❌ Commite no Git
- ❌ Compartilhe publicamente
- ❌ Envie para outras pessoas

### Adicionar ao .gitignore

Se usar Git, adicione ao `.gitignore`:
```bash
echo "cookies.txt" >> .gitignore
```

### Proteger permissões

No servidor:
```bash
chmod 600 cookies.txt  # Somente seu usuário pode ler
```

---

## 🆘 Problemas Comuns

### 1. "FileNotFoundError: cookies.txt not found"

**Causa**: Arquivo não está no diretório correto

**Solução**:
```bash
# Verificar se arquivo existe
ls -la cookies.txt

# Se não existe, copiar novamente
scp cookies.txt seu_usuario@servidor:/caminho/bot/
```

### 2. "ERROR: Unsupported URL"

**Causa**: Cookies inválidos ou expirados

**Solução**: Exportar cookies novamente (passos 2️⃣ e 3️⃣)

### 3. Bot continua dando erro

**Causa**: Permissões incorretas ou caminho errado

**Solução**:
```bash
# Verificar permissões
ls -la cookies.txt

# Corrigir se necessário
chmod 600 cookies.txt

# Verificar se está no diretório raiz do bot
pwd  # Deve estar em /home/seu_usuario/bot-discord-youtube
```

---

## 📊 Alternativas

Se não quiser usar cookies, há 3 alternativas (menos recomendadas):

### Alternativa 1: YouTube Data API (sem yt-dlp)
- ✅ Não precisa de cookies
- ❌ Não faz download de áudio (só busca e metadados)
- ℹ️ Já está configurado no bot (OAuth2)

### Alternativa 2: API Key (limitado)
- ✅ Sem cookies
- ❌ Não funciona para todos os vídeos
- ℹ️ Ver `docs/guides/servidor.md` - Solução 3

### Alternativa 3: Spotify + YouTube híbrido
- ✅ Busca no Spotify, toca do YouTube
- ❌ Mais complexo de configurar
- ℹ️ Planejado para v2.0

---

## 📚 Referências

- [yt-dlp FAQ - Cookies](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
- [Exportar cookies do YouTube](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies)
- [Documentação yt-dlp](https://github.com/yt-dlp/yt-dlp)

---

## ✅ Checklist

- [ ] Instalar extensão de cookies no navegador
- [ ] Fazer login no YouTube
- [ ] Exportar cookies.txt
- [ ] Copiar cookies.txt para servidor
- [ ] Ajustar permissões (chmod 600)
- [ ] Adicionar YTDL_COOKIES_PATH ao .env
- [ ] Reiniciar bot
- [ ] Testar !play no Discord
- [ ] Adicionar cookies.txt ao .gitignore
- [ ] Marcar data de exportação (para renovar em 30-90 dias)

---

**🎉 Pronto!** Agora seu bot conseguirá baixar músicas do YouTube sem ser bloqueado.
