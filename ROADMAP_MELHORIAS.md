# 🚀 Roadmap de Melhorias - Bot de Música Discord

> Documento de planejamento para implementação gradual de melhorias no bot

---

## 📋 Status das Melhorias

- 🔴 **Não Iniciado**
- 🟡 **Em Progresso**
- 🟢 **Concluído**

---

## 🔥 Alta Prioridade (Implementar Primeiro)

### 1. 🔴 Comando `.np` (Now Playing Curto)
**Dificuldade:** ⭐ Fácil
**Tempo estimado:** 5 minutos
**Descrição:** Alias curto para `nowplaying`

```python
@commands.command(name="np")
async def now_playing_short(self, ctx):
    """Alias curto para nowplaying"""
    await self.nowplaying(ctx)
```

**Benefício:** Conveniência para usuários

---

### 2. 🔴 Reações de Confirmação Automática
**Dificuldade:** ⭐ Fácil
**Tempo estimado:** 10 minutos
**Descrição:** Bot reage com ✅ quando comando é bem-sucedido, ❌ quando há erro

```python
# Após processar comando com sucesso
await ctx.message.add_reaction("✅")

# Em caso de erro
await ctx.message.add_reaction("❌")
```

**Benefício:** Feedback visual imediato

---

### 3. 🔴 Rate Limiting por Usuário
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 30 minutos
**Descrição:** Impedir spam de comandos

```python
from collections import defaultdict
from datetime import datetime, timedelta

class MusicCommands:
    def __init__(self, bot):
        self.user_cooldowns = defaultdict(lambda: datetime.now())

    def check_cooldown(self, user_id: int, cooldown: int = 3):
        """Impede spam de comandos"""
        last_use = self.user_cooldowns[user_id]
        if datetime.now() - last_use < timedelta(seconds=cooldown):
            return False
        self.user_cooldowns[user_id] = datetime.now()
        return True
```

**Benefício:** Previne abuso e sobrecarga do bot

---

### 4. 🔴 Timeout de Inatividade
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 20 minutos
**Descrição:** Desconectar bot se ninguém está ouvindo há X minutos

```python
async def check_inactivity(self, player: MusicPlayer):
    """Desconecta após 5 minutos de inatividade"""
    if not player.is_playing:
        await asyncio.sleep(300)  # 5 minutos
        if not player.is_playing and player.voice_client:
            await player.voice_client.disconnect()
            await player.text_channel.send("⏰ Desconectando por inatividade")
```

**Benefício:** Economiza recursos e evita bot "fantasma"

---

### 5. 🔴 Histórico de Músicas
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 45 minutos
**Descrição:** Comando para ver últimas músicas tocadas

```python
class MusicPlayer:
    def __init__(self):
        self.play_history: deque[Song] = deque(maxlen=50)

@commands.command(name="history", aliases=["historico"])
async def history_command(self, ctx: commands.Context, limit: int = 10):
    """Mostra as últimas músicas tocadas"""
    # Criar embed com histórico
```

**Benefício:** Útil para relembrar músicas ou tocar novamente

---

### 6. 🔴 Comando de Ping/Latência
**Dificuldade:** ⭐ Fácil
**Tempo estimado:** 5 minutos
**Descrição:** Mostra latência do bot

```python
@commands.command(name="ping")
async def ping(self, ctx):
    """Mostra latência do bot"""
    latency = round(self.bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latência: {latency}ms")
```

**Benefício:** Diagnóstico rápido de problemas de conexão

---

## 🟡 Média Prioridade

### 7. 🔴 Sistema de Favoritos
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 2 horas
**Descrição:** Usuários podem salvar músicas favoritas

**Comandos:**
- `.favorite` - Salva música atual
- `.favorites` - Lista favoritos
- `.playfav <número>` - Toca favorito

**Arquivos necessários:**
- `data/favorites.json` - Armazenamento
- Novo método `FavoritesManager`

**Benefício:** Personalização e playlist pessoal

---

### 8. 🔴 Pré-carregar Próxima Música
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 1.5 horas
**Descrição:** Reduzir latência entre músicas

```python
async def _preload_next_song(self, song: Song):
    """Pré-carrega stream da próxima música"""
    info = await self._extract_info_cached(song.url)
    song.stream_url = info.get("url")
```

**Benefício:** Transição mais suave entre músicas

---

### 9. 🔴 Notificações de Eventos
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 45 minutos
**Descrição:** Eventos de entrada/saída do canal de voz

```python
@commands.Cog.listener()
async def on_voice_state_update(self, member, before, after):
    # Pausar se todos saíram
    # Mensagem de boas-vindas se alguém entrou
    # Auto-resume se alguém voltou
```

**Benefício:** Melhor experiência social

---

### 10. 🔴 Comando de Estatísticas
**Dificuldidade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 2 horas
**Descrição:** Dashboard de estatísticas do servidor

**Informações:**
- Total de músicas tocadas
- Usuário mais ativo
- Música mais tocada
- Tempo total de reprodução
- Gêneros mais ouvidos

**Benefício:** Gamificação e engajamento

---

### 11. 🔴 Cache Persistente
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 1 hora
**Descrição:** Salvar cache em disco para persistir entre reinicializações

```python
import pickle
import gzip

def _save_cache(self):
    with gzip.open('cache/video_info.pkl.gz', 'wb') as f:
        pickle.dump(self._video_info_cache, f)

def _load_cache(self):
    if Path('cache/video_info.pkl.gz').exists():
        with gzip.open('cache/video_info.pkl.gz', 'rb') as f:
            self._video_info_cache = pickle.load(f)
```

**Benefício:** Menos requisições ao YouTube, startup mais rápido

---

### 12. 🔴 Busca Melhorada com Paginação
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 1.5 horas
**Descrição:** Melhorar comando de busca

**Features:**
- Paginação com reações ◀️ ▶️
- Mais informações (views, likes, data)
- Preview do vídeo
- Botões numéricos para selecionar

**Benefício:** Melhor UX na busca

---

## 🟢 Baixa Prioridade (Nice to Have)

### 13. 🔴 Comando de Letra (Lyrics)
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 3 horas
**Descrição:** Buscar letra da música atual

**Opções:**
- API Genius
- API Musixmatch
- Web scraping (backup)

```python
@commands.command(name="lyrics", aliases=["letra"])
async def lyrics_command(self, ctx):
    """Busca letra da música atual"""
```

**Benefício:** Feature popular em bots de música

---

### 14. 🔴 Comandos Avançados de Fila
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 1 hora

**Comandos:**
```python
# Pular para posição específica
@commands.command(name="skipto")
async def skip_to(self, ctx, position: int):
    """Pula para música na posição X"""

# Mover música
@commands.command(name="move")
async def move(self, ctx, from_pos: int, to_pos: int):
    """Move música de uma posição para outra"""

# Repetir última
@commands.command(name="replay")
async def replay(self, ctx):
    """Toca novamente a última música"""
```

**Benefício:** Mais controle sobre a fila

---

### 15. 🔴 Validação de Permissões (DJ Role)
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 45 minutos
**Descrição:** Apenas usuários com cargo "DJ" podem usar comandos avançados

```python
def has_dj_role():
    """Decorator para comandos restritos"""
    async def predicate(ctx):
        dj_role = discord.utils.get(ctx.guild.roles, name="DJ")
        if dj_role:
            return dj_role in ctx.author.roles
        return True  # Se não existe cargo DJ, todos podem usar
    return commands.check(predicate)

@commands.command(name="volume")
@has_dj_role()
async def volume(self, ctx, volume: int):
    """Apenas DJs podem alterar volume"""
```

**Benefício:** Controle de acesso e ordem no servidor

---

### 16. 🔴 Proteção contra URLs Maliciosas
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 30 minutos
**Descrição:** Blacklist de domínios maliciosos

```python
BLOCKED_DOMAINS = [
    'malicious-site.com',
    'spam.com',
    # Adicionar mais conforme necessário
]

def validate_url(url: str) -> bool:
    """Verifica se URL é segura"""
    return not any(domain in url for domain in BLOCKED_DOMAINS)
```

**Benefício:** Segurança do bot e servidor

---

### 17. 🔴 Seek (Pular para Timestamp)
**Dificuldade:** ⭐⭐⭐⭐ Muito Difícil
**Tempo estimado:** 3 horas
**Descrição:** Pular para tempo específico da música

```python
@commands.command(name="seek")
async def seek(self, ctx, timestamp: str):
    """Pula para timestamp (ex: 1:30)"""
    # Requer parar e reiniciar com -ss no FFmpeg
```

**Desafio:** Complexo com Discord streaming

---

### 18. 🔴 Velocidade de Reprodução
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 2 horas
**Descrição:** Ajustar velocidade (0.5x - 2.0x)

```python
@commands.command(name="speed")
async def speed(self, ctx, rate: float):
    """Ajusta velocidade (0.5x - 2.0x)"""
    # Adicionar filtro atempo no FFmpeg
```

**Benefício:** Útil para alguns casos de uso

---

### 19. 🔴 Equalizer Presets
**Dificuldade:** ⭐⭐⭐⭐ Muito Difícil
**Tempo estimado:** 4 horas
**Descrição:** Presets de equalização

**Presets:**
- Bass Boost
- Treble
- Pop
- Rock
- Classical
- Nightcore

```python
@commands.command(name="eq")
async def equalizer(self, ctx, preset: str):
    """Aplica preset de equalização"""
    # Filtros superequalizer do FFmpeg
```

**Benefício:** Customização de áudio

---

### 20. 🔴 Integração com Spotify
**Dificuldade:** ⭐⭐⭐⭐⭐ Muito Difícil
**Tempo estimado:** 6+ horas
**Descrição:** Converter links do Spotify para YouTube

**Features:**
- Converter track do Spotify → Buscar no YouTube
- Importar playlists do Spotify
- Buscar por artista/álbum

**Requer:**
- Spotify API credentials
- Algoritmo de matching (título + artista)

**Benefício:** Conveniência para usuários do Spotify

---

### 21. 🔴 Dashboard Web
**Dificuldade:** ⭐⭐⭐⭐⭐ Muito Difícil
**Tempo estimado:** 10+ horas
**Descrição:** Interface web para controlar bot

**Features:**
- Ver fila em tempo real
- Adicionar músicas remotamente
- Ver estatísticas
- Gerenciar configurações
- WebSocket para updates em tempo real

**Stack sugerida:**
- Backend: aiohttp
- Frontend: HTML/CSS/JS simples ou React
- WebSocket para real-time

**Benefício:** Controle remoto e melhor visualização

---

### 22. 🔴 Configurações por Servidor (Guild Settings)
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 3 horas
**Descrição:** Salvar preferências de cada servidor

```python
class GuildSettings:
    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.default_volume = 0.5
        self.dj_role_id = None
        self.music_channel_id = None
        self.announce_songs = True
        self.auto_disconnect = True
        self.command_prefix = "!"

    def save(self):
        # Salvar em JSON
        with open(f'data/guild_{self.guild_id}.json', 'w') as f:
            json.dump(self.__dict__, f)

    def load(self):
        # Carregar de JSON
```

**Benefício:** Personalização por servidor

---

### 23. 🔴 Sistema de Métricas e Analytics
**Dificuldade:** ⭐⭐⭐ Difícil
**Tempo estimado:** 2 horas
**Descrição:** Tracking detalhado de uso

**Métricas:**
- Músicas mais tocadas (global)
- Horários de pico
- Comandos mais usados
- Erros mais frequentes
- Uptime
- Servidores mais ativos

```python
class Metrics:
    def track_song_play(self, song_title: str):
        # Incrementar contador

    def track_command_usage(self, command_name: str):
        # Log de uso

    def get_top_songs(self, limit: int = 10):
        # Retornar ranking
```

**Benefício:** Insights para melhorias

---

### 24. 🔴 Alertas Automáticos ao Owner
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 45 minutos
**Descrição:** Notificar owner de problemas críticos

```python
async def send_alert_to_owner(self, message: str, severity: str = "warning"):
    """Envia DM ao owner quando há problema crítico"""
    if config.OWNER_ID:
        try:
            owner = await self.bot.fetch_user(config.OWNER_ID)

            emoji = "⚠️" if severity == "warning" else "🚨"
            embed = discord.Embed(
                title=f"{emoji} Alerta do Bot",
                description=message,
                color=discord.Color.orange() if severity == "warning" else discord.Color.red(),
                timestamp=datetime.now()
            )

            await owner.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Erro ao enviar alerta: {e}")
```

**Situações para alertar:**
- API do YouTube chegou perto do limite
- Bot foi kickado de servidor
- Erro crítico ocorreu
- Tentativa de abuso detectada

**Benefício:** Monitoramento proativo

---

### 25. 🔴 Health Check Endpoint
**Dificuldade:** ⭐⭐ Médio
**Tempo estimado:** 1 hora
**Descrição:** Endpoint HTTP para monitorar status

```python
from aiohttp import web

async def health_check(request):
    status = {
        "status": "online",
        "uptime": get_uptime(),
        "guilds": len(bot.guilds),
        "active_players": len(music_service.players),
        "latency": round(bot.latency * 1000)
    }
    return web.json_response(status)

# Iniciar servidor HTTP na porta 8080
app = web.Application()
app.router.add_get('/health', health_check)
web.run_app(app, port=8080)
```

**Benefício:** Útil para monitorar uptime com serviços externos

---

## 📊 Resumo por Dificuldade

### ⭐ Fácil (< 30 min)
- Comando `.np`
- Reações de confirmação
- Comando de ping

### ⭐⭐ Médio (30 min - 1.5h)
- Rate limiting
- Timeout de inatividade
- Histórico de músicas
- Notificações de eventos
- Cache persistente
- Comandos avançados de fila
- Validação de permissões
- Proteção de URLs
- Alertas ao owner
- Health check

### ⭐⭐⭐ Difícil (1.5h - 3h)
- Sistema de favoritos
- Pré-carregar músicas
- Busca melhorada
- Comando de lyrics
- Configurações por servidor
- Métricas e analytics
- Velocidade de reprodução
- Seek

### ⭐⭐⭐⭐ Muito Difícil (3h - 6h)
- Equalizer presets

### ⭐⭐⭐⭐⭐ Épico (6h+)
- Integração com Spotify
- Dashboard web

---

## 🎯 Sugestão de Ordem de Implementação

### Sprint 1 (1-2 horas) - Quick Wins
1. ✅ Comando `.np`
2. ✅ Reações de confirmação
3. ✅ Comando de ping
4. ✅ Timeout de inatividade

### Sprint 2 (2-3 horas) - Segurança e Robustez
5. ✅ Rate limiting por usuário
6. ✅ Proteção contra URLs maliciosas
7. ✅ Alertas ao owner
8. ✅ Validação de permissões (DJ role)

### Sprint 3 (3-4 horas) - Features Populares
9. ✅ Histórico de músicas
10. ✅ Notificações de eventos
11. ✅ Comandos avançados de fila
12. ✅ Cache persistente

### Sprint 4 (4-6 horas) - Features Avançadas
13. ✅ Sistema de favoritos
14. ✅ Comando de estatísticas
15. ✅ Busca melhorada
16. ✅ Métricas e analytics

### Sprint 5 (6-8 horas) - Otimizações
17. ✅ Pré-carregar próxima música
18. ✅ Configurações por servidor
19. ✅ Health check endpoint

### Sprint 6 (8+ horas) - Features Complexas
20. ✅ Comando de lyrics
21. ✅ Velocidade de reprodução
22. ✅ Seek (pular para timestamp)
23. ✅ Equalizer presets

### Sprint 7 (Opcional - 10+ horas) - Integrações
24. ✅ Integração com Spotify
25. ✅ Dashboard web

---

## 📝 Notas de Implementação

### Antes de Começar Qualquer Melhoria:
1. ✅ Criar branch: `git checkout -b feature/nome-da-feature`
2. ✅ Testar em ambiente local primeiro
3. ✅ Documentar mudanças no código
4. ✅ Atualizar README.md se necessário
5. ✅ Fazer commit: `git commit -m "feat: descrição"`
6. ✅ Merge na main apenas depois de testar

### Estrutura de Commits:
- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `perf:` - Melhoria de performance
- `docs:` - Apenas documentação
- `refactor:` - Refatoração de código
- `test:` - Adicionar testes

### Testes Recomendados:
- ✅ Testar comando com parâmetros válidos
- ✅ Testar comando sem parâmetros
- ✅ Testar comando com parâmetros inválidos
- ✅ Testar com usuário sem permissão
- ✅ Testar com bot desconectado
- ✅ Testar com fila vazia/cheia

---

## 🔗 Recursos Úteis

### APIs Recomendadas:
- **Genius API**: Letras de músicas - https://genius.com/api-clients
- **Spotify API**: Integração Spotify - https://developer.spotify.com/
- **Musixmatch API**: Letras alternativa - https://developer.musixmatch.com/

### Bibliotecas Úteis:
```bash
pip install spotipy           # Spotify integration
pip install lyricsgenius      # Genius lyrics
pip install aiohttp           # HTTP async
pip install aiofiles          # File I/O async
```

### Documentação:
- discord.py: https://discordpy.readthedocs.io/
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- FFmpeg filters: https://ffmpeg.org/ffmpeg-filters.html

---

## 📞 Precisa de Ajuda?

Se tiver dúvidas ao implementar alguma melhoria:
1. Consulte a documentação oficial
2. Veja exemplos de outros bots
3. Peça ajuda na comunidade discord.py
4. Abra uma issue no repositório

---

## 🎉 Conclusão

Este roadmap é um guia vivo que deve ser atualizado conforme:
- ✅ Features são implementadas (marcar como 🟢)
- ✅ Novas ideias surgem
- ✅ Prioridades mudam
- ✅ Feedback dos usuários

**Lembre-se:** Melhor implementar bem poucas features do que muitas mal feitas!

**Próximos Passos:**
1. Escolha 1-2 itens do Sprint 1
2. Implemente com calma
3. Teste bem
4. Marque como concluído 🟢
5. Repita!

Boa sorte! 🚀

---

**Última atualização:** 10 de novembro de 2025
