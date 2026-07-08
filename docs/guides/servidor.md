# 🖥️ Rodando o Bot em Servidor (VPS/Dedicado)

Guia completo para deploy do bot em servidores Linux sem interface gráfica.

---

## ⚠️ Problemas Comuns ao Deploy

### 1. OAuth2 - "Could not locate runnable browser"
✅ **Solução**: Copiar `token.json` do local para servidor (ver Solução 1 abaixo)

### 2. yt-dlp - "Sign in to confirm you're not a bot"
✅ **Solução**: Usar cookies do YouTube → **[Ver Guia Completo](cookies-youtube.md)**

**Resumo rápido**: Exporte cookies do navegador com extensão, copie `cookies.txt` para servidor, configure `YTDL_COOKIES_PATH=cookies.txt` no `.env`

---

## ❌ Problema: Erro de Autenticação OAuth2

### Sintoma

```
ERROR - ❌ Erro na autenticação OAuth2: could not locate runnable browser
```

**Causa**: Servidores não têm navegador (ambiente headless)

---

## ✅ Solução 1: Copiar Token do PC Local (RECOMENDADO)

### Passo 1: Autenticar Localmente

No seu **computador pessoal**:

```bash
# 1. Clone o repositório
git clone https://github.com/MatheusAlves96/bot-youtube-pao.git
cd bot-youtube-pao

# 2. Configure credenciais
cp .env.example .env
# Edite .env com suas credenciais

# 3. Rode o bot uma vez (vai abrir navegador)
python main.py

# 4. Faça login no navegador
# O token será salvo em config/token.json
```

### Passo 2: Copiar Token para o Servidor

**Opção A: Via SCP (SSH)**

```bash
# Do seu PC, copie o token
scp config/token.json usuario@servidor:/caminho/bot/config/token.json

# Exemplo:
scp config/token.json root@192.168.1.100:/root/bot-youtube-pao/config/token.json
```

**Opção B: Via Painel Web (cPanel, Plesk, etc)**

1. Baixe `config/token.json` do seu PC
2. Faça upload para o servidor em `config/token.json`

**Opção C: Manualmente (cat/nano)**

```bash
# No servidor
nano config/token.json

# Cole o conteúdo do token.json do seu PC
# Salve: Ctrl+O, Enter, Ctrl+X
```

### Passo 3: Verificar Permissões

```bash
# No servidor
chmod 600 config/token.json
ls -la config/token.json
```

### Passo 4: Rodar o Bot

```bash
python3 main.py
```

✅ **Pronto!** O bot usará o token existente sem precisar de navegador.

---

## ✅ Solução 2: Autenticação Manual (Headless)

Se não conseguir copiar o token, use este método:

### Passo 1: Modificar Código (Já Feito)

O código já foi atualizado para não abrir navegador automaticamente:

```python
open_browser=False  # Não abre navegador
```

### Passo 2: Obter URL de Autenticação

```bash
# No servidor, rode o bot
python3 main.py

# Nos logs, procure por:
# 🔗 URL de Autenticação Gerada:
# https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...
```

### Passo 3: Autenticar no Navegador (PC)

1. **Copie a URL** dos logs
2. **Abra no seu PC** (navegador normal)
3. **Faça login** com sua conta Google
4. **Autorize** o acesso
5. Você será redirecionado para `http://localhost:8080/?code=...`

### Passo 4: Copiar Código de Autorização

A URL de redirecionamento terá um parâmetro `code`:

```
http://localhost:8080/?code=4/0AanRRrvxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Copie** o valor do `code` (tudo depois de `code=` até o final)

### Passo 5: Criar Token Manualmente

No servidor, crie `config/token.json` com o código:

```bash
nano config/token.json
```

Cole este template (substitua os valores):

```json
{
  "token": "COLE_O_TOKEN_AQUI",
  "refresh_token": "COLE_O_REFRESH_TOKEN_AQUI",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "SEU_CLIENT_ID",
  "client_secret": "SEU_CLIENT_SECRET",
  "scopes": ["https://www.googleapis.com/auth/youtube.readonly"],
  "universe_domain": "googleapis.com",
  "account": "",
  "expiry": "2025-12-31T23:59:59.999999Z"
}
```

**Nota**: Este método é mais complexo. Recomendo a Solução 1.

---

## ✅ Solução 3: Usar API Key (Mais Simples)

Se você não precisa de funcionalidades avançadas do OAuth2:

### Passo 1: Obter API Key

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie/selecione projeto
3. Ative "YouTube Data API v3"
4. Vá em "Credenciais" > "Criar Credenciais" > "Chave de API"
5. Copie a chave

### Passo 2: Configurar no .env

```bash
# No servidor
nano .env

# Adicione:
YOUTUBE_API_KEY=AIzaSyAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaAaA

# Comente ou remova OAuth2:
# YOUTUBE_CLIENT_ID=
# YOUTUBE_CLIENT_SECRET=
```

### Passo 3: Rodar o Bot

```bash
python3 main.py
```

✅ **Funciona!** Sem necessidade de OAuth2.

**Limitações**:
- Quota menor (10.000 unidades/dia vs 1.000.000)
- Sem acesso a playlists privadas
- Sem funcionalidades avançadas

---

## 🐳 Solução 4: Usar Docker (Avançado)

### Dockerfile

Crie `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Volume para persistir token
VOLUME /app/config

# Comando padrão
CMD ["python", "main.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  discord-bot:
    build: .
    container_name: bot-youtube-pao
    restart: unless-stopped
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./cache:/app/cache
    env_file:
      - .env
    environment:
      - TZ=America/Sao_Paulo
```

### Build e Run

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# Logs
docker-compose logs -f
```

---

## 🔧 Configuração do Servidor

### Instalar Dependências

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install -y python3 python3-pip ffmpeg git
```

**CentOS/RHEL:**

```bash
sudo yum install -y python3 python3-pip ffmpeg git
```

### Instalar Bot

```bash
# Clone
git clone https://github.com/MatheusAlves96/bot-youtube-pao.git
cd bot-youtube-pao

# Dependências Python
pip3 install -r requirements.txt

# Configurar
cp .env.example .env
nano .env  # Preencher credenciais
```

---

## 🚀 Rodar em Background

### Opção 1: Screen

```bash
# Criar sessão
screen -S discord-bot

# Rodar bot
python3 main.py

# Detach: Ctrl+A, D

# Re-attach
screen -r discord-bot

# Listar sessões
screen -ls
```

### Opção 2: tmux

```bash
# Criar sessão
tmux new -s discord-bot

# Rodar bot
python3 main.py

# Detach: Ctrl+B, D

# Re-attach
tmux attach -t discord-bot
```

### Opção 3: Systemd Service (Recomendado)

Crie `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Music Bot
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/bot-youtube-pao
ExecStart=/usr/bin/python3 /caminho/bot-youtube-pao/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Ativar:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot

# Status
sudo systemctl status discord-bot

# Logs
sudo journalctl -u discord-bot -f
```

### Opção 4: nohup

```bash
nohup python3 main.py > bot.log 2>&1 &

# Ver logs
tail -f bot.log

# Parar
pkill -f main.py
```

---

## 📊 Monitoramento

### Logs

```bash
# Logs gerais
tail -f logs/bot.log

# Logs de autoplay
tail -f logs/autoplay.log

# Seguir em tempo real
watch -n 1 'tail -n 50 logs/bot.log'
```

### Recursos do Sistema

```bash
# CPU e Memória
top
htop

# Processos Python
ps aux | grep python

# Uso de disco
df -h
du -sh cache/
```

---

## 🆘 Troubleshooting

### Bot não inicia

**Verificar:**
1. Python 3.10+ instalado: `python3 --version`
2. FFmpeg instalado: `ffmpeg -version`
3. Dependências: `pip3 install -r requirements.txt`
4. Credenciais no `.env`
5. Permissões: `chmod +x main.py`

### Token expira rapidamente

**Causa**: Token OAuth2 expira em 1h

**Solução**: O bot renova automaticamente com `refresh_token`

Se continuar expirando:
1. Verifique `config/token.json` tem `refresh_token`
2. Regenere token localmente e copie novamente

### Erro de permissão

```bash
# Dar permissões ao usuário
sudo chown -R seu_usuario:seu_usuario /caminho/bot-youtube-pao

# Permissões corretas
chmod 600 .env config/token.json config/credentials.json
chmod 755 main.py
```

### Bot desconecta após fechar SSH

**Causa**: Processo filho do terminal

**Solução**: Use screen, tmux ou systemd (veja seção acima)

### Porta 8080 em uso

**Editar** `services/youtube_service.py`:

```python
ports_to_try = [8080, 8081, 8082, 9090, 3000]
```

Ou adicione sua porta preferida.

---

## 🔒 Segurança

### Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp    # SSH
sudo ufw enable

# Bot não precisa de portas abertas (cliente Discord)
```

### Credentials

```bash
# Nunca commite credenciais
echo "config/token.json" >> .gitignore
echo "config/credentials.json" >> .gitignore
echo ".env" >> .gitignore

# Backup seguro
tar -czf bot-backup.tar.gz config/ .env
chmod 600 bot-backup.tar.gz
```

---

## 📚 Recursos Adicionais

- [Docker Documentation](https://docs.docker.com/)
- [Systemd Service](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [Google OAuth2](https://developers.google.com/identity/protocols/oauth2)

---

**Última Atualização**: 13 de novembro de 2025
**Autor**: [@MatheusAlves96](https://github.com/MatheusAlves96)
