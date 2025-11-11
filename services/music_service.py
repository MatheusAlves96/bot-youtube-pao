"""
Music Service - Observer Pattern
Gerencia reprodução de música, fila e estado
"""

import asyncio
import discord
import yt_dlp
import aiohttp
from typing import Optional, List, Dict, Any, Callable
from collections import deque, OrderedDict
from datetime import datetime
import time

from core.logger import LoggerFactory, autoplay_logger
from config import config


# Decorator para retry com backoff exponencial
async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: tuple = (aiohttp.ClientError, asyncio.TimeoutError, ConnectionError)
):
    """
    Executa função com retry exponencial em caso de falha de rede

    Args:
        func: Função async a ser executada
        max_retries: Número máximo de tentativas (padrão: 3)
        base_delay: Delay inicial em segundos (padrão: 1s)
        exceptions: Tupla de exceções que acionam retry

    Returns:
        Resultado da função ou None em caso de falha total
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except exceptions as e:
            if attempt == max_retries - 1:  # Última tentativa
                raise

            delay = base_delay * (2 ** attempt)  # Exponencial: 1s, 2s, 4s
            logger = LoggerFactory.create_logger(__name__)
            logger.debug(f"⚠️ Tentativa {attempt + 1}/{max_retries} falhou: {type(e).__name__}. Retry em {delay}s...")
            await asyncio.sleep(delay)

    return None


class Song:
    """Representa uma música na fila"""

    def __init__(self, data: Dict[str, Any], requester: discord.Member):
        self.url = data.get("url", "")
        self.title = data.get("title", "Unknown")
        self.duration = data.get("duration", 0)
        self.thumbnail = data.get("thumbnail", "")
        self.uploader = data.get("uploader", "Unknown")
        self.stream_url = data.get("stream_url", "")
        self.requester = requester
        self.requested_at = datetime.now()

        # TTL para stream URL (URLs do YouTube expiram em ~6h, usar 5h de segurança)
        import time

        self.stream_url_expires = time.time() + (5 * 3600)  # 5 horas

    def __str__(self):
        return f"{self.title} - {self.uploader}"

    def to_embed(self) -> discord.Embed:
        """Cria um embed com informações da música"""
        embed = discord.Embed(
            title="🎵 Tocando Agora",
            description=f"**{self.title}**",
            color=discord.Color.blue(),
        )

        embed.add_field(name="Canal", value=self.uploader, inline=True)

        duration_str = f"{self.duration // 60}:{self.duration % 60:02d}"
        embed.add_field(name="Duração", value=duration_str, inline=True)

        embed.add_field(
            name="Solicitado por", value=self.requester.mention, inline=True
        )

        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)

        embed.set_footer(text=f"URL: {self.url}")

        return embed


class MusicPlayer:
    """
    Player de música para um servidor específico
    Usa Observer Pattern para notificar mudanças de estado
    """

    def __init__(self, guild_id: int):
        self.guild_id = guild_id
        self.queue: deque[Song] = deque()
        self.current_song: Optional[Song] = None
        self.voice_client: Optional[discord.VoiceClient] = None
        self.text_channel: Optional[discord.TextChannel] = (
            None  # Canal para enviar mensagens
        )
        self.volume = config.DEFAULT_VOLUME
        self.loop_mode = False  # False, 'single', 'queue'
        self.is_playing = False
        self.is_paused = False
        self.cancel_playlist_processing = False  # Flag para cancelar processamento

        # Autoplay configuration
        self.autoplay_enabled = config.AUTOPLAY_ENABLED
        self.autoplay_history: deque[str] = deque(maxlen=config.AUTOPLAY_HISTORY_SIZE)
        self.last_video_id: Optional[str] = None
        self.last_video_title: Optional[str] = None
        self.last_video_channel: Optional[str] = None
        self.last_requester: Optional[discord.Member] = (
            None  # Último usuário que solicitou música
        )
        self.is_fetching_autoplay = False  # Previne múltiplas buscas simultâneas
        self.autoplay_lock = asyncio.Lock()  # Lock assíncrono para prevenir race conditions
        self.stopped_manually = False  # Flag para indicar se usuário parou manualmente

        # Loop detection
        self.autoplay_failures = 0  # Contador de falhas consecutivas ao buscar autoplay
        self.current_search_strategy = 0  # Estratégia de busca atual (0-3)

        # Crossfade configuration
        self.crossfade_enabled = config.CROSSFADE_ENABLED
        self.crossfade_duration = config.CROSSFADE_DURATION
        self.fade_task: Optional[asyncio.Task] = None  # Task do fade em andamento

        # 🎛️ Control Panel - Painel visual interativo
        self.control_panel_message: Optional[discord.Message] = None
        self.panel_update_task: Optional[asyncio.Task] = None
        self.panel_debounce_task: Optional[asyncio.Task] = None  # Task de debounce (2s)
        self.song_start_time: Optional[float] = None  # Timestamp do início da música

        # 🚀 Pré-carregamento - Reduz latência entre músicas
        self.preloaded_song: Optional[Song] = None  # Próxima música pré-carregada
        self.preload_task: Optional[asyncio.Task] = None  # Task de pré-carregamento

        self.logger = LoggerFactory.create_logger(__name__)

    def add_song(self, song: Song) -> None:
        """Adiciona uma música à fila"""
        if len(self.queue) >= config.MAX_QUEUE_SIZE:
            raise ValueError(f"Fila cheia! Máximo: {config.MAX_QUEUE_SIZE}")

        self.queue.append(song)
        self.logger.info(f"Música adicionada à fila: {song.title}")

    def get_queue(self) -> List[Song]:
        """Retorna a fila atual"""
        return list(self.queue)

    def clear_queue(self) -> None:
        """Limpa a fila e para autoplay temporariamente"""
        self.queue.clear()
        self.cancel_playlist_processing = True  # Cancelar processamento de playlist
        self.is_fetching_autoplay = False  # Cancelar busca de autoplay em andamento
        self.stopped_manually = True  # Marcar que foi parado manualmente

        # �️ Cancelar fade task se existir
        if self.fade_task and not self.fade_task.done():
            self.fade_task.cancel()
            self.fade_task = None

        # �🚀 Cancelar pré-carregamento se existir
        if self.preload_task and not self.preload_task.done():
            self.preload_task.cancel()
        self.preloaded_song = None

        self.logger.info("Fila limpa e processamento cancelado")

    def shuffle(self) -> None:
        """Embaralha a fila"""
        import random

        queue_list = list(self.queue)
        random.shuffle(queue_list)
        self.queue = deque(queue_list)
        self.logger.info("Fila embaralhada")

    def skip(self) -> Optional[Song]:
        """Pula a música atual"""
        # 🛡️ Cancelar fade task se estiver rodando
        if self.fade_task and not self.fade_task.done():
            self.fade_task.cancel()
            self.fade_task = None

        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
        return self.current_song

    def toggle_pause(self) -> bool:
        """Pausa/Resume a reprodução"""
        if not self.voice_client:
            return False

        if self.voice_client.is_paused():
            self.voice_client.resume()
            self.is_paused = False
            self.logger.info("Reprodução retomada")
            return False
        elif self.voice_client.is_playing():
            self.voice_client.pause()
            self.is_paused = True
            self.logger.info("Reprodução pausada")
            return True

        return False

    async def fade_out(self, duration: float):
        """
        Reduz o volume gradualmente (fade out) com transição suave

        Args:
            duration: Duração do fade em segundos

        Melhorias (Otimização #17):
            - 50 steps para transição imperceptível (antes: 20)
            - Cancelamento suave sem "click"
            - Curva de volume não-linear para naturalidade
        """
        if not self.voice_client or not self.voice_client.source:
            return

        original_volume = self.volume
        steps = config.CROSSFADE_STEPS  # 🆕 Configurável via .env (default: 50)
        step_duration = duration / steps

        try:
            for i in range(steps):
                # Verificar se ainda está tocando
                if not self.voice_client or not self.voice_client.is_playing():
                    # Cancelado - fade out suave para evitar click
                    if self.voice_client and self.voice_client.source:
                        # Volume atual → 0 em 50ms (suave, não abrupto)
                        current_volume = self.voice_client.source.volume
                        for j in range(5):
                            self.voice_client.source.volume = current_volume * (1 - j/5)
                            await asyncio.sleep(0.01)  # 10ms x 5 = 50ms
                        self.voice_client.source.volume = 0.0
                    break

                # 🆕 CURVA NÃO-LINEAR (mais natural)
                # Reduz mais rápido no início, mais devagar no final
                progress = (i + 1) / steps
                # Curva quadrática: y = x²
                curve_factor = progress ** 2
                new_volume = original_volume * (1 - curve_factor)
                new_volume = max(0.0, new_volume)

                self.voice_client.source.volume = new_volume

                await asyncio.sleep(step_duration)

        except asyncio.CancelledError:
            # Fade cancelado - mute suave
            if self.voice_client and self.voice_client.source:
                current_volume = self.voice_client.source.volume
                for j in range(5):
                    self.voice_client.source.volume = current_volume * (1 - j/5)
                    await asyncio.sleep(0.01)
                self.voice_client.source.volume = 0.0
            raise
        except Exception as e:
            self.logger.debug(f"Fade out interrompido: {e}")

    async def fade_in(self, duration: float):
        """
        Aumenta o volume gradualmente (fade in) com transição suave

        Args:
            duration: Duração do fade em segundos

        Melhorias (Otimização #17):
            - 50 steps para transição imperceptível (antes: 20)
            - Curva não-linear inversa do fade out
        """
        if not self.voice_client or not self.voice_client.source:
            return

        target_volume = self.volume
        steps = config.CROSSFADE_STEPS  # 🆕 Configurável via .env (default: 50)
        step_duration = duration / steps

        # Começar do silêncio
        self.voice_client.source.volume = 0.0

        try:
            for i in range(steps):
                if not self.voice_client or not self.voice_client.is_playing():
                    break

                # 🆕 CURVA NÃO-LINEAR (inversa do fade out)
                progress = (i + 1) / steps
                # Curva raiz quadrada: y = √x (aumenta rápido no início)
                curve_factor = progress ** 0.5
                new_volume = target_volume * curve_factor
                new_volume = min(target_volume, new_volume)

                self.voice_client.source.volume = new_volume

                await asyncio.sleep(step_duration)

        except asyncio.CancelledError:
            # Fade cancelado - definir volume final
            if self.voice_client and self.voice_client.source:
                self.voice_client.source.volume = target_volume
            raise
        except Exception as e:
            self.logger.debug(f"Fade in interrompido: {e}")

    def set_volume(self, volume: float) -> None:
        """Define o volume (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.voice_client and self.voice_client.source:
            self.voice_client.source.volume = self.volume
        self.logger.info(f"Volume definido para {self.volume * 100:.0f}%")

    def _format_duration(self, seconds: int) -> str:
        """Formata duração em MM:SS ou HH:MM:SS"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def _get_progress_bar(self, current: int, total: int, length: int = 15) -> str:
        """Cria barra de progresso visual"""
        if total == 0:
            return "─" * length

        filled = int((current / total) * length)
        filled = max(0, min(length, filled))

        bar = "━" * filled + "─" * (length - filled)
        return f"[{bar}]"

    async def create_control_panel_embed(self) -> discord.Embed:
        """Cria embed do painel de controle com status atual"""
        embed = discord.Embed(
            title="🎛️ Painel de Controle - Music Bot",
            color=discord.Color.blue() if self.is_playing else discord.Color.greyple(),
            timestamp=datetime.now(),
        )

        # 🎵 Música Atual
        if self.current_song:
            elapsed = 0
            if self.song_start_time and not self.is_paused:
                import time

                elapsed = int(time.time() - self.song_start_time)
                elapsed = min(elapsed, self.current_song.duration)

            progress_bar = self._get_progress_bar(elapsed, self.current_song.duration)
            elapsed_str = self._format_duration(elapsed)
            total_str = self._format_duration(self.current_song.duration)

            status_icon = "⏸️" if self.is_paused else "▶️"

            current_info = (
                f"{status_icon} **{self.current_song.title}**\n"
                f"🎤 {self.current_song.uploader}\n"
                f"👤 Pedido por: {self.current_song.requester.mention}\n"
                f"⏱️ {elapsed_str} {progress_bar} {total_str}"
            )
            embed.add_field(name="🎵 Tocando Agora", value=current_info, inline=False)

            if self.current_song.thumbnail:
                embed.set_thumbnail(url=self.current_song.thumbnail)
        else:
            embed.add_field(
                name="🎵 Tocando Agora", value="*Nenhuma música tocando*", inline=False
            )

        # 📋 Fila
        if self.queue:
            queue_text = ""
            for i, song in enumerate(list(self.queue)[:5], 1):
                duration = self._format_duration(song.duration)
                queue_text += f"`{i}.` **{song.title}** [{duration}]\n"

            if len(self.queue) > 5:
                queue_text += f"\n*...e mais {len(self.queue) - 5} música(s)*"

            embed.add_field(
                name=f"📋 Fila ({len(self.queue)} música(s))",
                value=queue_text,
                inline=False,
            )
        else:
            embed.add_field(name="📋 Fila", value="*Fila vazia*", inline=False)

        # ⚙️ Configurações
        loop_status = (
            "🔁 Ativado"
            if self.loop_mode == "single"
            else "🔁🔁 Fila" if self.loop_mode == "queue" else "❌ Desativado"
        )
        autoplay_status = "✅ Ativado" if self.autoplay_enabled else "❌ Desativado"
        volume_bars = int(self.volume * 10)
        volume_display = "🔊" + "█" * volume_bars + "░" * (10 - volume_bars)

        config_text = (
            f"🔁 Loop: {loop_status}\n"
            f"🎲 Autoplay: {autoplay_status}\n"
            f"🔊 Volume: {volume_display} {int(self.volume * 100)}%"
        )
        embed.add_field(name="⚙️ Configurações", value=config_text, inline=False)

        # 🎮 Controles
        controls_text = (
            "⏯️ Play/Pause | ⏭️ Pular | ⏹️ Parar\n"
            "🔊 Vol+ | 🔉 Vol- | 🔁 Loop | 🎲 Autoplay"
        )
        embed.add_field(
            name="🎮 Controles (Reações)", value=controls_text, inline=False
        )

        embed.set_footer(text="Use as reações para controlar o bot")

        return embed


class MusicService:
    """
    Serviço de música - Singleton
    Gerencia players de música para diferentes servidores
    """

    _instance: Optional["MusicService"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.logger = LoggerFactory.create_logger(__name__)
        self.players: Dict[int, MusicPlayer] = {}

        # 🚀 Cache LRU para informações de vídeos (evita reprocessamento)
        self._video_info_cache: OrderedDict[str, Dict] = OrderedDict()
        self._cache_max_size = config.VIDEO_CACHE_SIZE
        self._cache_hits = 0
        self._cache_misses = 0

        # Configurar yt-dlp para músicas individuais
        self.ytdl = yt_dlp.YoutubeDL(config.get_ytdl_options())

        # Configurar yt-dlp para playlists (ignora erros e continua)
        playlist_options = config.get_ytdl_options().copy()
        playlist_options["ignoreerrors"] = "only_download"  # Ignora erros mas continua
        playlist_options["no_warnings"] = True
        playlist_options["quiet"] = False  # Mostrar progresso
        self.ytdl_playlist = yt_dlp.YoutubeDL(playlist_options)

        # 🧹 Iniciar task de cleanup de players inativos
        asyncio.create_task(self.cleanup_inactive_players())

    def get_player(self, guild_id: int) -> MusicPlayer:
        """Obtém ou cria um player para o servidor"""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(guild_id)
            self.logger.info(f"Player criado para servidor {guild_id}")

        return self.players[guild_id]

    async def extract_info(self, url: str, requester: discord.Member) -> Song:
        """
        Extrai informações de uma música do YouTube

        Args:
            url: URL ou termo de busca
            requester: Membro que solicitou

        Returns:
            Objeto Song com as informações
        """
        try:
            # Executar em thread separada com retry (3 tentativas, backoff 1s→2s→4s)
            loop = asyncio.get_event_loop()

            async def extract_with_retry():
                return await loop.run_in_executor(
                    None, lambda: self.ytdl.extract_info(url, download=False)
                )

            data = await retry_with_backoff(
                extract_with_retry,
                max_retries=3,
                base_delay=1.0,
                exceptions=(Exception,)  # yt-dlp lança Exception genérica para erros de rede
            )

            # Verificar se data não é None
            if data is None:
                raise ValueError(
                    "Não foi possível extrair informações do vídeo. Verifique se a URL está correta ou se o vídeo está disponível."
                )

            # Se for playlist, pegar primeiro vídeo
            if "entries" in data:
                if not data["entries"]:
                    raise ValueError("Playlist vazia ou sem vídeos disponíveis.")
                data = data["entries"][0]

                # Verificar se o primeiro vídeo da playlist também não é None
                if data is None:
                    raise ValueError(
                        "O primeiro vídeo da playlist não está disponível."
                    )

            # Obter URL de stream
            formats = data.get("formats", [])
            stream_url = data.get("url")

            # Procurar melhor formato de áudio
            for fmt in formats:
                if fmt.get("acodec") != "none":
                    stream_url = fmt.get("url")
                    break

            # Verificar se conseguimos obter uma URL de stream válida
            if not stream_url:
                # Tentar usar a URL original como fallback
                stream_url = data.get("webpage_url", url)
                self.logger.warning(
                    f"Usando URL original como fallback para stream: {stream_url}"
                )

            # Validar dados essenciais
            title = data.get("title")
            if not title or title.strip() == "":
                raise ValueError("Título do vídeo não disponível.")

            song_data = {
                "url": data.get("webpage_url", url),
                "title": title,
                "duration": data.get("duration", 0) or 0,  # Garantir que não seja None
                "thumbnail": data.get("thumbnail", ""),
                "uploader": data.get("uploader", "Unknown"),
                "stream_url": stream_url,
            }

            song = Song(song_data, requester)
            self.logger.info(f"Informações extraídas: {song.title}")

            return song

        except Exception as e:
            self.logger.error(f"Erro ao extrair informações: {e}", exc_info=True)
            raise

    async def extract_playlist(
        self,
        url: str,
        requester: discord.Member,
        player: "MusicPlayer" = None,
        progress_callback=None,
    ) -> Dict[str, Any]:
        """
        Extrai informações de uma playlist do YouTube

        Args:
            url: URL da playlist
            requester: Membro que solicitou
            player: Player para verificar cancelamento
            progress_callback: Função async para atualizar progresso (opcional)

        Returns:
            Dicionário com estatísticas e lista de músicas
        """
        try:
            # Resetar flag de cancelamento (caso tenha ficado de operação anterior)
            if player:
                player.cancel_playlist_processing = False

            # Calcular limite para não baixar páginas desnecessárias
            max_items = config.MAX_QUEUE_SIZE + 10

            self.logger.info(f"🔍 Extraindo playlist com limite de {max_items} itens")

            # FASE 1: Extração RÁPIDA com extract_flat para pegar apenas URLs
            flat_options = config.get_ytdl_options().copy()
            flat_options.update(
                {
                    "extract_flat": "in_playlist",  # Extrai apenas metadados básicos (RÁPIDO!)
                    "playlistend": max_items,
                    "quiet": True,
                    "no_warnings": True,
                }
            )

            ytdl_flat = yt_dlp.YoutubeDL(flat_options)
            loop = asyncio.get_event_loop()

            self.logger.info(f"📥 Fase 1: Extraindo lista de URLs (rápido)")

            data = await loop.run_in_executor(
                None, lambda: ytdl_flat.extract_info(url, download=False)
            )

            self.logger.info(f"✅ Lista extraída: {data is not None}")

            if data is None:
                self.logger.error("❌ Data retornado é None")
                raise ValueError("Não foi possível extrair informações da playlist.")

            # Verificar se é realmente uma playlist
            if "entries" not in data:
                # É apenas um vídeo, não uma playlist
                song = await self.extract_info(url, requester)
                return {
                    "is_playlist": False,
                    "songs": [song],
                    "total": 1,
                    "added": 1,
                    "failed": 0,
                    "errors": [],
                }

            entries = data["entries"]
            playlist_title = data.get("title", "Playlist")

            # Nota: yt-dlp já limitou com playlistend, então len(entries) <= max_items
            total_in_playlist = data.get("playlist_count") or len(entries)

            songs = []
            errors = []

            self.logger.info(
                f"📋 Fase 2: Processando {len(entries)} de {total_in_playlist} itens"
            )

            # FASE 2: Extrair detalhes de cada vídeo individualmente (com cancelamento)
            # Criar ytdl para extrair detalhes individuais
            detail_options = config.get_ytdl_options().copy()
            detail_options.update(
                {
                    "quiet": True,
                    "no_warnings": True,
                    "ignoreerrors": True,
                }
            )
            ytdl_detail = yt_dlp.YoutubeDL(detail_options)

            # OTIMIZAÇÃO #1: Processar em batches paralelos (5 vídeos por vez)
            BATCH_SIZE = 5
            total_processed = 0

            for batch_start in range(0, len(entries), BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, len(entries))
                batch = entries[batch_start:batch_end]

                # Verificar cancelamento antes de cada batch
                if player and player.cancel_playlist_processing:
                    self.logger.info(
                        f"🛑 Processamento cancelado após {total_processed}/{len(entries)} itens"
                    )
                    break

                # Processar batch em paralelo
                batch_tasks = []
                for idx_in_batch, entry in enumerate(batch):
                    idx = batch_start + idx_in_batch + 1

                    async def process_entry(entry=entry, idx=idx):
                        if entry is None:
                            return {"error": f"Item {idx}: Vídeo indisponível"}

                        try:
                            # Pegar URL do vídeo
                            video_url = entry.get("url") or entry.get("webpage_url")
                            if not video_url:
                                video_id = entry.get("id")
                                if video_id:
                                    video_url = f"https://www.youtube.com/watch?v={video_id}"
                                else:
                                    return {"error": f"Item {idx}: URL não encontrada"}

                            # Extrair detalhes (em paralelo)
                            video_data = await loop.run_in_executor(
                                None,
                                lambda: ytdl_detail.extract_info(video_url, download=False),
                            )

                            if not video_data:
                                return {"error": f"Item {idx}: Não foi possível extrair"}

                            title = video_data.get("title", entry.get("title", "Unknown"))

                            return {
                                "idx": idx,
                                "song_data": {
                                    "url": video_url,
                                    "title": title,
                                    "duration": video_data.get("duration", 0) or 0,
                                    "thumbnail": video_data.get("thumbnail", ""),
                                    "uploader": video_data.get("uploader", "Unknown"),
                                    "stream_url": video_data.get("url", video_url),
                                },
                                "title": title
                            }
                        except Exception as e:
                            error_msg = str(e)
                            if "copyright" in error_msg.lower() or "blocked" in error_msg.lower():
                                return {"error": f"Item {idx}: Bloqueado por direitos autorais"}
                            elif "unavailable" in error_msg.lower():
                                return {"error": f"Item {idx}: Vídeo indisponível"}
                            else:
                                return {"error": f"Item {idx}: {error_msg[:50]}"}

                    batch_tasks.append(process_entry())

                # Aguardar batch completo
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

                # Processar resultados do batch
                for result in batch_results:
                    if isinstance(result, Exception):
                        errors.append(f"Erro: {str(result)[:50]}")
                        continue

                    if "error" in result:
                        errors.append(result["error"])
                        self.logger.warning(f"❌ {result['error']}")
                        continue

                    # Sucesso - criar música
                    song = Song(result["song_data"], requester)
                    songs.append(song)
                    total_processed += 1
                    self.logger.info(f"✅ {result['idx']}/{len(entries)}: {result['title']}")

                    # Callback para adicionar em tempo real
                    if progress_callback:
                        await progress_callback(
                            current=result['idx'],
                            total=len(entries),
                            processed=len(songs),
                            failed=len(errors),
                            current_title=result['title'],
                            song=song,
                        )



            # Calcular itens não processados
            fetched_items = len(entries)
            not_fetched = max(0, total_in_playlist - fetched_items)

            # Verificar se foi cancelado
            was_cancelled = player and player.cancel_playlist_processing

            # Resetar flag de cancelamento
            if player:
                player.cancel_playlist_processing = False

            return {
                "is_playlist": True,
                "playlist_title": playlist_title,
                "songs": songs,
                "total": total_in_playlist,
                "processed": fetched_items,
                "not_processed": not_fetched,
                "added": len(songs),
                "failed": len(errors),
                "errors": errors[:10],  # Limitar a 10 erros para não flodar
                "cancelled": was_cancelled,
            }

        except ValueError as e:
            # Erros de validação já têm mensagem clara
            self.logger.error(f"Erro de validação: {e}")
            raise
        except Exception as e:
            # Outros erros mais técnicos
            self.logger.error(f"Erro ao extrair playlist: {e}", exc_info=True)
            self.logger.error(f"URL problemática: {url}")
            self.logger.error(f"Tipo de erro: {type(e).__name__}")
            raise ValueError(f"Erro ao processar playlist: {str(e)[:100]}")

    async def _preload_next_song(self, player: MusicPlayer):
        """
        Pré-carrega a próxima música da fila para reduzir latência

        Args:
            player: Player do servidor
        """
        try:
            # 🛡️ PROTEÇÃO: Prevenir múltiplos pré-carregamentos simultâneos
            if player.preload_task and not player.preload_task.done():
                # Já existe um pré-carregamento em andamento
                return

            # Se não tem próxima música na fila, não pré-carregar
            if not player.queue or len(player.queue) == 0:
                return

            # Pegar próxima música sem remover da fila
            next_song = player.queue[0]

            # Se já foi pré-carregada, não fazer novamente
            if player.preloaded_song and player.preloaded_song.url == next_song.url:
                self.logger.debug(f"🚀 Música já pré-carregada: {next_song.title}")
                return

            self.logger.info(f"🚀 Pré-carregando próxima música: {next_song.title}")

            # Extrair video_id
            video_id = self._extract_video_id(next_song.url)

            # Verificar cache primeiro (LRU)
            if video_id and video_id in self._video_info_cache:
                # Move para o final (marca como recentemente usado)
                info = self._video_info_cache.pop(video_id)
                self._video_info_cache[video_id] = info
                self._cache_hits += 1
                self.logger.debug(f"✅ Cache hit no pré-carregamento: {video_id}")
            else:
                self._cache_misses += 1
                # Extrair informações do vídeo com timeout de 10s
                loop = asyncio.get_event_loop()
                try:
                    info = await asyncio.wait_for(
                        loop.run_in_executor(
                            None,
                            lambda: self.ytdl.extract_info(
                                next_song.url, download=False
                            ),
                        ),
                        timeout=10.0,  # 10 segundos de timeout (reduzido de 30s)
                    )
                except asyncio.TimeoutError:
                    self.logger.warning(
                        f"⏱️ Timeout ao pré-carregar música: {next_song.title} (carregará sob demanda)"
                    )
                    return

                # Adicionar ao cache (LRU - remove mais antigo se cheio)
                if video_id and info:
                    if len(self._video_info_cache) >= self._cache_max_size:
                        # Remove primeiro item (mais antigo)
                        self._video_info_cache.popitem(last=False)
                    self._video_info_cache[video_id] = info

            # Atualizar stream_url da próxima música
            if info:
                next_song.stream_url = info.get("url", next_song.stream_url)
                player.preloaded_song = next_song
                self.logger.info(
                    f"✅ Música pré-carregada com sucesso: {next_song.title}"
                )

        except asyncio.CancelledError:
            self.logger.debug("🚫 Pré-carregamento cancelado")
            # Esperado quando fila é limpa ou skip
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao pré-carregar música: {e}")
            # Não é crítico, apenas log

    async def _ensure_valid_stream_url(self, song: Song):
        """
        Garante que a URL do stream é válida e não expirou

        Args:
            song: Música a validar
        """
        import time

        # Verificar se a URL expirou
        if time.time() > song.stream_url_expires:
            self.logger.info(f"🔄 Stream URL expirada, re-extraindo: {song.title}")

            try:
                # Re-extrair informações do vídeo
                loop = asyncio.get_event_loop()
                data = await loop.run_in_executor(
                    None, lambda: self.ytdl.extract_info(song.url, download=False)
                )

                if data:
                    # Atualizar stream URL
                    song.stream_url = data.get("url", song.stream_url)
                    # Renovar TTL
                    song.stream_url_expires = time.time() + (5 * 3600)
                    self.logger.info(f"✅ Stream URL renovada: {song.title}")

            except Exception as e:
                self.logger.error(f"❌ Erro ao renovar stream URL: {e}")
                # Manter URL antiga e tentar tocar mesmo assim

    async def play_song(
        self, player: MusicPlayer, voice_client: discord.VoiceClient, song: Song
    ):
        """
        Reproduz uma música

        Args:
            player: Player do servidor
            voice_client: Cliente de voz do Discord
            song: Música a ser reproduzida
        """
        player.voice_client = voice_client
        player.current_song = song
        player.is_playing = True
        player.stopped_manually = False  # Resetar flag ao começar a tocar

        # 🎛️ Definir timestamp do início da música para tracking de progresso
        import time

        player.song_start_time = time.time()

        # 🎛️ Iniciar/atualizar painel de controle
        await self.update_control_panel(player)
        await self.start_panel_updates(player)

        # 🔄 Validar e renovar stream URL se necessário
        await self._ensure_valid_stream_url(song)

        # Criar fonte de áudio
        audio_source = discord.FFmpegPCMAudio(song.stream_url, **config.FFMPEG_OPTIONS)

        # Aplicar volume
        audio_source = discord.PCMVolumeTransformer(audio_source, volume=player.volume)

        def after_playing(error):
            """Callback após terminar de tocar"""
            if error:
                self.logger.error(f"Erro na reprodução: {error}")

            # 🛡️ PROTEÇÃO: Cancelar fade task se ainda estiver rodando
            if player.fade_task and not player.fade_task.done():
                player.fade_task.cancel()
                player.fade_task = None

            player.is_playing = False

            # Salvar ID e informações do vídeo que acabou de tocar
            if player.current_song:
                video_id = self._extract_video_id(player.current_song.url)
                if video_id:
                    player.last_video_id = video_id
                    player.last_video_title = player.current_song.title
                    player.last_video_channel = player.current_song.uploader
                    player.autoplay_history.append(video_id)
                    self.logger.debug(
                        f"📝 Música adicionada ao histórico: {player.current_song.title} | Histórico: {len(player.autoplay_history)} vídeos"
                    )

                # Salvar último requester válido
                if player.current_song.requester:
                    player.last_requester = player.current_song.requester

            player.current_song = None

            # Verificar se foi parado manualmente
            if player.stopped_manually:
                self.logger.info("⏹️ Reprodução parada manualmente pelo usuário")
                player.stopped_manually = False  # Resetar flag
                return

            # Verificar se ainda está conectado (pode ter sido desconectado por .stop)
            if not voice_client.is_connected():
                self.logger.info("Bot desconectado, não tocar próxima música")
                return

            # 🛡️ PROTEÇÃO: Prevenir múltiplas chamadas simultâneas
            if player.is_playing:
                self.logger.warning(
                    "⚠️ Tentativa de tocar música enquanto outra já está tocando - ignorando"
                )
                return

            # Tocar próxima música da fila
            if player.queue:
                next_song = player.queue.popleft()

                # 🚀 Usar stream pré-carregado se disponível
                if (
                    player.preloaded_song
                    and player.preloaded_song.url == next_song.url
                    and player.preloaded_song.stream_url
                ):
                    self.logger.info(
                        f"⚡ Usando stream pré-carregado para: {next_song.title}"
                    )
                    next_song.stream_url = player.preloaded_song.stream_url
                    player.preloaded_song = None  # Limpar cache

                asyncio.run_coroutine_threadsafe(
                    self.play_song(player, voice_client, next_song),
                    voice_client.client.loop,
                )
            # Se fila vazia e autoplay ativo, buscar músicas relacionadas
            elif (
                player.autoplay_enabled
                and player.last_video_id
                and not player.is_fetching_autoplay
            ):
                self.logger.info(
                    "🎵 Autoplay: Fila vazia, buscando músicas relacionadas..."
                )
                asyncio.run_coroutine_threadsafe(
                    self._fetch_autoplay_songs(player, voice_client),
                    voice_client.client.loop,
                )

        voice_client.play(audio_source, after=after_playing)
        self.logger.info(f"Reproduzindo: {song.title}")

        # � CROSSFADE: Fade in no início da música
        if player.crossfade_enabled:
            self.logger.debug(f"🔊 Iniciando fade in ({player.crossfade_duration}s)")
            asyncio.run_coroutine_threadsafe(
                player.fade_in(player.crossfade_duration),
                voice_client.client.loop,
            )

            # 🔉 Agendar fade out para os últimos X segundos
            if (
                song.duration > player.crossfade_duration * 2
            ):  # Só faz fade se música for longa o suficiente
                fade_out_delay = song.duration - player.crossfade_duration
                self.logger.debug(f"🔉 Fade out agendado para {fade_out_delay}s")

                async def schedule_fade_out():
                    await asyncio.sleep(fade_out_delay)
                    if player.is_playing and voice_client.is_playing():
                        self.logger.debug(
                            f"🔉 Iniciando fade out ({player.crossfade_duration}s)"
                        )
                        await player.fade_out(player.crossfade_duration)

                player.fade_task = asyncio.run_coroutine_threadsafe(
                    schedule_fade_out(),
                    voice_client.client.loop,
                )

        # 🚀 PRÉ-CARREGAMENTO: Iniciar pré-carregamento da próxima música
        if player.queue and len(player.queue) > 0:
            # Iniciar novo pré-carregamento em background (proteção está dentro do método)
            try:
                player.preload_task = asyncio.create_task(
                    self._preload_next_song(player)
                )
                self.logger.debug("🚀 Pré-carregamento da próxima música iniciado")
            except Exception as e:
                self.logger.warning(f"⚠️ Erro ao iniciar pré-carregamento: {e}")

        # 🆕 AUTOPLAY PROATIVO: Se fila VAZIA e autoplay ativo, buscar mais músicas
        # IMPORTANTE: Só busca quando fila está REALMENTE vazia (0 músicas)
        if (
            player.autoplay_enabled
            and len(player.queue) == 0  # ← CORRIGIDO: Apenas quando fila VAZIA
            and not player.is_fetching_autoplay
        ):
            # Extrair info da música ATUAL (que está tocando agora)
            current_video_id = self._extract_video_id(song.url)
            if current_video_id:
                self.logger.info(
                    f"🎵 Autoplay proativo: Fila vazia, buscando músicas baseadas em '{song.title}'"
                )
                asyncio.run_coroutine_threadsafe(
                    self._fetch_autoplay_songs(
                        player,
                        voice_client,
                        proactive=True,
                        reference_video_id=current_video_id,
                        reference_title=song.title,
                        reference_channel=song.uploader,
                    ),
                    voice_client.client.loop,
                )

    async def _send_autoplay_notification(
        self, channel: discord.TextChannel, song: Song, position: int
    ):
        """
        Envia notificação de música adicionada pelo autoplay (em background)

        Args:
            channel: Canal de texto para enviar
            song: Música adicionada
            position: Posição na fila
        """
        try:
            # Formatar duração
            duration_str = (
                f"{song.duration // 60}:{song.duration % 60:02d}"
                if song.duration
                else "N/A"
            )

            embed = discord.Embed(
                title="🎵 Autoplay adicionou",
                description=f"**[{song.title}]({song.url})**",
                color=discord.Color.blue(),
            )
            embed.add_field(
                name="Canal",
                value=song.uploader or "Desconhecido",
                inline=True,
            )
            embed.add_field(
                name="Duração",
                value=duration_str,
                inline=True,
            )
            embed.add_field(
                name="Posição na fila",
                value=f"#{position}",
                inline=True,
            )
            if song.thumbnail:
                embed.set_thumbnail(url=song.thumbnail)
            embed.set_footer(
                text=f"💡 Use {config.COMMAND_PREFIX}remove {position} para remover"
            )
            await channel.send(embed=embed)
        except Exception as e:
            self.logger.debug(f"Erro ao enviar notificação de autoplay: {e}")

    async def update_control_panel(self, player: MusicPlayer, debounce: bool = True):
        """
        Atualiza ou cria o painel de controle com debounce opcional

        Args:
            player: Player do servidor
            debounce: Se True, aguarda 2s antes de atualizar (evita spam)
        """
        if debounce:
            # Cancelar debounce anterior se existir
            if player.panel_debounce_task and not player.panel_debounce_task.done():
                player.panel_debounce_task.cancel()

            # Criar nova task de debounce
            async def debounced_update():
                await asyncio.sleep(2.0)  # Aguardar 2 segundos
                await self.update_control_panel(player, debounce=False)

            player.panel_debounce_task = asyncio.create_task(debounced_update())
            return

        try:
            if not player.text_channel:
                return

            embed = await player.create_control_panel_embed()

            # Se já existe painel, atualizar
            if player.control_panel_message:
                try:
                    await player.control_panel_message.edit(embed=embed)
                except discord.NotFound:
                    # Mensagem foi deletada, criar nova
                    player.control_panel_message = None
                except discord.HTTPException as e:
                    self.logger.debug(f"Erro ao atualizar painel: {e}")
                    return

            # Se não existe, criar novo painel
            if not player.control_panel_message:
                player.control_panel_message = await player.text_channel.send(
                    embed=embed
                )

                # Adicionar reações de controle
                control_reactions = ["⏯️", "⏭️", "⏹️", "🔊", "🔉", "🔁", "🎲"]
                for emoji in control_reactions:
                    try:
                        await player.control_panel_message.add_reaction(emoji)
                    except discord.HTTPException:
                        pass

        except asyncio.CancelledError:
            # Esperado quando debounce é cancelado
            pass
        except Exception as e:
            self.logger.error(f"Erro ao atualizar painel de controle: {e}")

    async def start_panel_updates(self, player: MusicPlayer):
        """
        Inicia atualização automática do painel a cada 5 segundos

        Args:
            player: Player do servidor
        """

        async def update_loop():
            try:
                while player.is_playing or player.is_paused or len(player.queue) > 0:
                    try:
                        await self.update_control_panel(player)
                    except Exception as e:
                        self.logger.error(f"Erro ao atualizar painel no loop: {e}")

                    await asyncio.sleep(5)  # Atualizar a cada 5 segundos

                # Atualização final quando parar
                try:
                    await self.update_control_panel(player)
                except Exception as e:
                    self.logger.error(f"Erro na atualização final do painel: {e}")

            except asyncio.CancelledError:
                self.logger.debug("Loop de atualização do painel cancelado")
            except Exception as e:
                self.logger.error(f"Erro crítico no loop do painel: {e}")

        # Cancelar task anterior se existir
        if player.panel_update_task and not player.panel_update_task.done():
            player.panel_update_task.cancel()

        # Iniciar nova task
        player.panel_update_task = asyncio.create_task(update_loop())

    async def handle_panel_reaction(
        self,
        player: MusicPlayer,
        voice_client: discord.VoiceClient,
        reaction: discord.Reaction,
        user: discord.User,
    ):
        """
        Processa reação no painel de controle

        Args:
            player: Player do servidor
            voice_client: Cliente de voz
            reaction: Reação adicionada
            user: Usuário que reagiu
        """
        if user.bot:
            return

        emoji = str(reaction.emoji)
        action_processed = False

        try:
            # ⏯️ Play/Pause
            if emoji == "⏯️":
                player.toggle_pause()
                await self.update_control_panel(player)
                action_processed = True

            # ⏭️ Skip
            elif emoji == "⏭️":
                if voice_client and voice_client.is_playing():
                    voice_client.stop()
                await self.update_control_panel(player)
                action_processed = True

            # ⏹️ Stop
            elif emoji == "⏹️":
                player.stopped_manually = True
                player.queue.clear()
                if voice_client and voice_client.is_playing():
                    voice_client.stop()
                await self.update_control_panel(player)
                action_processed = True

            # 🔊 Volume +
            elif emoji == "🔊":
                new_volume = min(1.0, player.volume + 0.1)
                player.set_volume(new_volume)
                await self.update_control_panel(player)
                action_processed = True

            # 🔉 Volume -
            elif emoji == "🔉":
                new_volume = max(0.0, player.volume - 0.1)
                player.set_volume(new_volume)
                await self.update_control_panel(player)
                action_processed = True

            # 🔁 Loop
            elif emoji == "🔁":
                if not player.loop_mode:
                    player.loop_mode = "single"
                elif player.loop_mode == "single":
                    player.loop_mode = "queue"
                else:
                    player.loop_mode = False
                await self.update_control_panel(player)
                action_processed = True

            # 🎲 Autoplay toggle
            elif emoji == "🎲":
                player.autoplay_enabled = not player.autoplay_enabled
                await self.update_control_panel(player)
                action_processed = True

        except Exception as e:
            self.logger.error(f"Erro ao processar reação do painel: {e}")

        finally:
            # 🧹 SEMPRE tentar remover a reação do usuário (independente de sucesso/erro)
            if action_processed:
                try:
                    await reaction.remove(user)
                    self.logger.debug(
                        f"🧹 Reação {emoji} removida do usuário {user.name}"
                    )
                except discord.Forbidden:
                    self.logger.warning(
                        "⚠️ Sem permissão para remover reações. Adicione a permissão 'Manage Messages' ao bot."
                    )
                except discord.NotFound:
                    # Mensagem ou reação já foi deletada
                    pass
                except discord.HTTPException as e:
                    self.logger.debug(f"Erro HTTP ao remover reação: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache LRU

        Returns:
            Dicionário com estatísticas do cache
        """
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = (
            (self._cache_hits / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "size": len(self._video_info_cache),
            "max_size": self._cache_max_size,
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
        }

    def _extract_video_id(self, url: str) -> Optional[str]:
        """
        Extrai o ID do vídeo de uma URL do YouTube

        Args:
            url: URL do YouTube

        Returns:
            ID do vídeo ou None
        """
        import re

        # Padrões comuns de URLs do YouTube
        patterns = [
            r"(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)",
            r"youtube\.com\/embed\/([^&\n?#]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    async def _fetch_autoplay_songs(
        self,
        player: MusicPlayer,
        voice_client: discord.VoiceClient,
        proactive: bool = False,
        reference_video_id: str = None,
        reference_title: str = None,
        reference_channel: str = None,
    ):
        """
        Busca e adiciona músicas relacionadas automaticamente

        Args:
            player: Player do servidor
            voice_client: Cliente de voz conectado
            proactive: Se True, está buscando antecipadamente (não envia mensagem)
            reference_video_id: ID do vídeo de referência (override last_video_id)
            reference_title: Título de referência (override last_video_title)
            reference_channel: Canal de referência (override last_video_channel)
        """
        # Verificar lock ANTES de tentar adquirir (não bloqueia)
        if player.autoplay_lock.locked():
            self.logger.debug(
                "� Autoplay lock ativo - ignorando chamada duplicada (race condition evitada)"
            )
            return

        # Adquirir lock atomicamente
        async with player.autoplay_lock:
            if player.is_fetching_autoplay:  # Double-check após adquirir lock
                return
            player.is_fetching_autoplay = True
        
        # ⏱️ Iniciar cronômetro da sessão
        session_start_time = time.time()
        
        self.logger.debug(
            f"🔍 Autoplay iniciado - Modo: {'proativo' if proactive else 'reativo'}, Fila atual: {len(player.queue)}"
        )

        try:
            # Importar YouTubeService aqui para evitar importação circular
            from services.youtube_service import YouTubeService

            youtube_service = YouTubeService.get_instance()

            # Usar referências fornecidas ou fallback para as salvas
            video_id = reference_video_id or player.last_video_id
            video_title = reference_title or player.last_video_title
            video_channel = reference_channel or player.last_video_channel

            if not video_id:
                self.logger.warning("⚠️ Autoplay: Nenhum vídeo de referência disponível")
                autoplay_logger.log_error("Nenhum vídeo de referência disponível")
                player.is_fetching_autoplay = False
                return

            # 📊 LOG: Início da sessão autoplay
            autoplay_logger.log_session_start({
                'title': video_title,
                'channel': video_channel,
                'id': video_id
            })
            
            self.logger.info(
                f"🎯 Autoplay usando como base: '{video_title}' de {video_channel}"
            )

            # DETECÇÃO DE LOOP: Se histórico está muito cheio (>80%), mudar estratégia automaticamente
            history_usage = len(player.autoplay_history) / config.AUTOPLAY_HISTORY_SIZE
            if history_usage > 0.8 and player.current_search_strategy == 0:
                player.current_search_strategy = 1
                self.logger.info(
                    f"🔄 Histórico alto ({history_usage:.0%}), mudando para estratégia 1"
                )

            # 🛡️ CORREÇÃO: Histórico só tem video_ids (strings), não dicts
            # Não podemos extrair títulos, apenas passar IDs
            history_titles = []  # Deixar vazio por enquanto

            # Buscar vídeos relacionados excluindo histórico
            related_videos = await youtube_service.get_related_videos(
                video_id=video_id,
                max_results=config.AUTOPLAY_QUEUE_SIZE,
                exclude_ids=list(player.autoplay_history),
                video_title=video_title,
                video_channel=video_channel,
                search_strategy=player.current_search_strategy,
                history_titles=history_titles,  # Passar histórico para IA
            )

            if not related_videos:
                # DETECÇÃO DE LOOP: Incrementar falhas e mudar estratégia
                player.autoplay_failures += 1
                self.logger.warning(
                    f"⚠️ Autoplay: Nenhum vídeo encontrado (falha {player.autoplay_failures})"
                )
                
                # 📊 LOG: Falha na tentativa
                autoplay_logger.log_failure(
                    attempt=player.autoplay_failures,
                    max_attempts=2,
                    reason="Nenhum vídeo encontrado após filtros"
                )

                # Após 2 falhas, mudar estratégia
                if player.autoplay_failures >= 2:
                    player.current_search_strategy = (
                        player.current_search_strategy + 1
                    ) % 4
                    self.logger.info(
                        f"🔄 Mudando para estratégia {player.current_search_strategy}"
                    )
                    player.autoplay_failures = 0  # Reset contador

                    # Tentar novamente com nova estratégia
                    player.is_fetching_autoplay = False
                    await self._fetch_autoplay_songs(
                        player,
                        voice_client,
                        proactive,
                        reference_video_id,
                        reference_title,
                        reference_channel,
                    )
                    return

                player.is_fetching_autoplay = False
                return

            # Se encontrou vídeos, resetar contador de falhas
            player.autoplay_failures = 0

            # SISTEMA DE RETORNO: Se está em estratégia alternativa e histórico diminuiu, voltar para estratégia 0
            if player.current_search_strategy > 0 and history_usage < 0.5:
                player.current_search_strategy = 0
                self.logger.info(
                    f"✅ Histórico normalizado ({history_usage:.0%}), voltando para estratégia 0"
                )

            # Usar o último requester válido salvo
            requester = player.last_requester

            # Se ainda não tiver, tentar pegar da fila ou música atual
            if not requester:
                if player.queue and player.queue[0].requester:
                    requester = player.queue[0].requester
                elif player.current_song and player.current_song.requester:
                    requester = player.current_song.requester

            # Adicionar músicas à fila
            added_songs = []

            # 🚀 OTIMIZAÇÃO: Processar vídeos em paralelo
            ytdl_options = config.get_ytdl_options()  # Cache options
            ydl = yt_dlp.YoutubeDL(ytdl_options)  # Reutilizar instância

            async def process_video(video):
                """Processa um vídeo do autoplay"""
                try:
                    # Capturar URL no escopo correto
                    video_url = video["url"]
                    video_id = self._extract_video_id(video_url)

                    # 🚀 Verificar cache primeiro (LRU)
                    if video_id and video_id in self._video_info_cache:
                        # Move para o final (marca como recentemente usado)
                        info = self._video_info_cache.pop(video_id)
                        self._video_info_cache[video_id] = info
                        self._cache_hits += 1
                        self.logger.debug(f"✅ Cache hit para: {video_id}")
                    else:
                        self._cache_misses += 1
                        info = await asyncio.get_event_loop().run_in_executor(
                            None,
                            lambda url=video_url: ydl.extract_info(url, download=False),
                        )

                        # Adicionar ao cache (LRU - remove mais antigo)
                        if video_id and info:
                            if len(self._video_info_cache) >= self._cache_max_size:
                                # Remove primeiro item (mais antigo)
                                self._video_info_cache.popitem(last=False)
                            self._video_info_cache[video_id] = info
                            self.logger.debug(f"💾 Cached: {video_id}")

                    if info:
                        song = Song(
                            {
                                "url": video["url"],
                                "title": info.get("title", video["title"]),
                                "duration": info.get("duration", 0),
                                "thumbnail": info.get("thumbnail", video["thumbnail"]),
                                "uploader": info.get("uploader", video["channel"]),
                                "stream_url": info.get("url", ""),
                            },
                            requester,
                        )

                        # ❌ REMOVIDO: Não adicionar ao histórico aqui
                        # Será adicionado no after_playing quando a música REALMENTE tocar

                        return song
                    return None

                except Exception as e:
                    error_msg = str(e)
                    # 🔞 Vídeos com restrição de idade - log silencioso
                    if (
                        "Sign in to confirm your age" in error_msg
                        or "age" in error_msg.lower()
                    ):
                        self.logger.debug(
                            f"🔞 Vídeo com restrição de idade ignorado: {video.get('title', 'unknown')}"
                        )
                    # ❌ Outros erros - log normal
                    else:
                        self.logger.warning(
                            f"⚠️ Erro ao processar vídeo {video.get('title', 'unknown')}: {error_msg[:100]}"
                        )
                    return None

            # 🚀 Processar todos os vídeos em PARALELO
            tasks = [process_video(video) for video in related_videos]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Adicionar músicas processadas à fila
            for song in results:
                if song and isinstance(song, Song):
                    player.add_song(song)
                    added_songs.append(song)
                    self.logger.debug(
                        f"✅ Música adicionada à fila: {song.title} | Total na fila: {len(player.queue)}"
                    )
                    
                    # 📊 LOG AUTOPLAY: Vídeo adicionado à fila
                    autoplay_logger.log_queue_added(
                        video_title=song.title,
                        queue_position=len(player.queue)
                    )

                    # � OTIMIZAÇÃO: Enviar mensagem em background (não bloqueia)
                    if not proactive and player.text_channel:
                        position = len(player.queue)
                        asyncio.create_task(
                            self._send_autoplay_notification(
                                player.text_channel, song, position
                            )
                        )

            if added_songs:
                mode_text = "proativo" if proactive else "reativo"
                strategy_names = [
                    "gênero detectado",
                    "variação do gênero",
                    "gênero aleatório",
                    "música brasileira geral",
                ]
                strategy_text = strategy_names[player.current_search_strategy]
                self.logger.info(
                    f"✅ Autoplay ({mode_text}, estratégia: {strategy_text}): {len(added_songs)} músicas adicionadas"
                )

                # 🛡️ CORREÇÃO: Só iniciar música se foi chamada REATIVAMENTE (não proativo)
                # E se realmente não tem nada tocando
                if not proactive and not player.is_playing and player.queue:
                    self.logger.info(
                        f"▶️ Autoplay reativo: Iniciando primeira música da fila (Total: {len(player.queue)})"
                    )
                    next_song = player.queue.popleft()
                    await self.play_song(player, voice_client, next_song)
                elif proactive:
                    self.logger.debug(
                        f"🎵 Autoplay proativo concluído - {len(player.queue)} músicas na fila (sem auto-start)"
                    )
            
            # 📊 LOG: Sessão bem-sucedida
            session_time = time.time() - session_start_time
            autoplay_logger.log_session_end(
                success=True,
                videos_added=len(added_songs),
                total_time=session_time
            )

        except Exception as e:
            self.logger.error(f"❌ Erro no autoplay: {e}")
            autoplay_logger.log_error("Erro crítico no autoplay", e)
            
            # 📊 LOG: Sessão com falha
            session_time = time.time() - session_start_time
            autoplay_logger.log_session_end(
                success=False,
                videos_added=0,
                total_time=session_time
            )

        finally:
            player.is_fetching_autoplay = False

    async def cleanup_inactive_players(self):
        """Remove players inativos a cada 1 hora para prevenir memory leak"""
        import time

        while True:
            try:
                await asyncio.sleep(3600)  # 1 hora

                to_remove = []
                current_time = time.time()

                for guild_id, player in self.players.items():
                    # Verificar se player está inativo
                    if not player.is_playing and not player.queue:
                        # Adicionar timestamp de última atividade se não existir
                        if not hasattr(player, "_last_activity"):
                            player._last_activity = current_time

                        # Se inativo há mais de 30 minutos, marcar para remoção
                        if current_time - player._last_activity > 1800:  # 30 min
                            to_remove.append(guild_id)
                    else:
                        # Player ativo, atualizar timestamp
                        player._last_activity = current_time

                # Remover players inativos
                for guild_id in to_remove:
                    player = self.players.get(guild_id)
                    if player and player.voice_client:
                        try:
                            await player.voice_client.disconnect()
                        except Exception as e:
                            self.logger.debug(f"Erro ao desconectar voice client: {e}")

                    del self.players[guild_id]
                    self.logger.info(
                        f"🧹 Player removido por inatividade: guild_id={guild_id}"
                    )

                if to_remove:
                    self.logger.info(
                        f"🧹 Cleanup concluído: {len(to_remove)} player(s) removido(s)"
                    )

            except asyncio.CancelledError:
                self.logger.info("🛑 Task de cleanup cancelada")
                break
            except Exception as e:
                self.logger.error(f"Erro no cleanup de players: {e}")

    @classmethod
    def get_instance(cls) -> "MusicService":
        """Retorna a instância única do serviço"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
