"""
Music Service - Observer Pattern
Gerencia reprodução de música, fila e estado
"""
import asyncio
import discord
import yt_dlp
from typing import Optional, List, Dict, Any
from collections import deque
from datetime import datetime

from core.logger import LoggerFactory
from config import config


class Song:
    """Representa uma música na fila"""

    def __init__(self, data: Dict[str, Any], requester: discord.Member):
        self.url = data.get('url', '')
        self.title = data.get('title', 'Unknown')
        self.duration = data.get('duration', 0)
        self.thumbnail = data.get('thumbnail', '')
        self.uploader = data.get('uploader', 'Unknown')
        self.stream_url = data.get('stream_url', '')
        self.requester = requester
        self.requested_at = datetime.now()

    def __str__(self):
        return f"{self.title} - {self.uploader}"

    def to_embed(self) -> discord.Embed:
        """Cria um embed com informações da música"""
        embed = discord.Embed(
            title="🎵 Tocando Agora",
            description=f"**{self.title}**",
            color=discord.Color.blue()
        )

        embed.add_field(name="Canal", value=self.uploader, inline=True)

        duration_str = f"{self.duration // 60}:{self.duration % 60:02d}"
        embed.add_field(name="Duração", value=duration_str, inline=True)

        embed.add_field(
            name="Solicitado por",
            value=self.requester.mention,
            inline=True
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
        self.volume = config.DEFAULT_VOLUME
        self.loop_mode = False  # False, 'single', 'queue'
        self.is_playing = False
        self.is_paused = False
        self.logger = LoggerFactory.create_logger(__name__)

    def add_song(self, song: Song):
        """Adiciona uma música à fila"""
        if len(self.queue) >= config.MAX_QUEUE_SIZE:
            raise ValueError(f"Fila cheia! Máximo: {config.MAX_QUEUE_SIZE}")

        self.queue.append(song)
        self.logger.info(f"Música adicionada à fila: {song.title}")

    def get_queue(self) -> List[Song]:
        """Retorna a fila atual"""
        return list(self.queue)

    def clear_queue(self):
        """Limpa a fila"""
        self.queue.clear()
        self.logger.info("Fila limpa")

    def shuffle(self):
        """Embaralha a fila"""
        import random
        queue_list = list(self.queue)
        random.shuffle(queue_list)
        self.queue = deque(queue_list)
        self.logger.info("Fila embaralhada")

    def skip(self) -> Optional[Song]:
        """Pula a música atual"""
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

    def set_volume(self, volume: float):
        """Define o volume (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.voice_client and self.voice_client.source:
            self.voice_client.source.volume = self.volume
        self.logger.info(f"Volume definido para {self.volume * 100:.0f}%")


class MusicService:
    """
    Serviço de música - Singleton
    Gerencia players de música para diferentes servidores
    """
    _instance: Optional['MusicService'] = None

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

        # Configurar yt-dlp
        self.ytdl = yt_dlp.YoutubeDL(config.get_ytdl_options())

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
            # Executar em thread separada para não bloquear
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None,
                lambda: self.ytdl.extract_info(url, download=False)
            )

            # Se for playlist, pegar primeiro vídeo
            if 'entries' in data:
                data = data['entries'][0]

            # Obter URL de stream
            formats = data.get('formats', [])
            stream_url = data.get('url')

            # Procurar melhor formato de áudio
            for fmt in formats:
                if fmt.get('acodec') != 'none':
                    stream_url = fmt.get('url')
                    break

            song_data = {
                'url': data.get('webpage_url', url),
                'title': data.get('title', 'Unknown'),
                'duration': data.get('duration', 0),
                'thumbnail': data.get('thumbnail', ''),
                'uploader': data.get('uploader', 'Unknown'),
                'stream_url': stream_url
            }

            song = Song(song_data, requester)
            self.logger.info(f"Informações extraídas: {song.title}")

            return song

        except Exception as e:
            self.logger.error(f"Erro ao extrair informações: {e}", exc_info=True)
            raise

    async def play_song(
        self,
        player: MusicPlayer,
        voice_client: discord.VoiceClient,
        song: Song
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

        # Criar fonte de áudio
        audio_source = discord.FFmpegPCMAudio(
            song.stream_url,
            **config.FFMPEG_OPTIONS
        )

        # Aplicar volume
        audio_source = discord.PCMVolumeTransformer(
            audio_source,
            volume=player.volume
        )

        def after_playing(error):
            """Callback após terminar de tocar"""
            if error:
                self.logger.error(f"Erro na reprodução: {error}")

            player.is_playing = False
            player.current_song = None

            # Tocar próxima música da fila
            if player.queue:
                next_song = player.queue.popleft()
                asyncio.run_coroutine_threadsafe(
                    self.play_song(player, voice_client, next_song),
                    voice_client.client.loop
                )

        voice_client.play(audio_source, after=after_playing)
        self.logger.info(f"Reproduzindo: {song.title}")

    @classmethod
    def get_instance(cls) -> 'MusicService':
        """Retorna a instância única do serviço"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
