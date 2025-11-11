"""
Configurações do Bot de Música para Discord
Utiliza Singleton Pattern para garantir uma única instância de configuração
"""

import os
from typing import Optional
from pathlib import Path


class Config:
    """
    Classe de configuração usando Singleton Pattern
    Centraliza todas as configurações do bot
    """

    _instance: Optional["Config"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._load_config()
        self._create_directories()  # Criar diretórios aqui (uma vez só)

    def _load_config(self):
        """Carrega as configurações de variáveis de ambiente ou valores padrão"""

        # Discord Configuration
        self.DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
        self.COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")
        self.OWNER_ID = int(os.getenv("OWNER_ID", "0"))

        # Canal dedicado para comandos de música (None = aceita em qualquer canal)
        music_channel = os.getenv("MUSIC_CHANNEL_ID", "")
        self.MUSIC_CHANNEL_ID = int(music_channel) if music_channel else None

        # YouTube Configuration
        self.YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
        self.YOUTUBE_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "")
        self.YOUTUBE_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "")

        # OAuth2 Credentials Path
        self.CREDENTIALS_PATH = Path(
            os.getenv("CREDENTIALS_PATH", "config/credentials.json")
        )
        self.TOKEN_PATH = Path(os.getenv("TOKEN_PATH", "config/token.json"))

        # AI Service (Groq API)
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

        # Music Player Configuration
        self.MAX_QUEUE_SIZE = int(os.getenv("MAX_QUEUE_SIZE", "100"))
        self.DEFAULT_VOLUME = float(os.getenv("DEFAULT_VOLUME", "0.5"))
        self.TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "300"))

        # Autoplay Configuration
        self.AUTOPLAY_ENABLED = os.getenv("AUTOPLAY_ENABLED", "False").lower() == "true"
        self.AUTOPLAY_QUEUE_SIZE = int(
            os.getenv("AUTOPLAY_QUEUE_SIZE", "2")
        )  # Músicas a adicionar por vez
        self.AUTOPLAY_HISTORY_SIZE = int(
            os.getenv("AUTOPLAY_HISTORY_SIZE", "100")
        )  # Evitar repetir últimas X músicas da sessão

        # Crossfade Configuration
        self.CROSSFADE_ENABLED = (
            os.getenv("CROSSFADE_ENABLED", "True").lower() == "true"
        )
        self.CROSSFADE_DURATION = int(
            os.getenv("CROSSFADE_DURATION", "10")
        )  # Duração do fade em segundos

        # Audio Quality Settings
        self.AUDIO_FORMAT = os.getenv("AUDIO_FORMAT", "bestaudio/best")
        self.BITRATE = int(os.getenv("BITRATE", "192"))

        # FFmpeg Configuration
        self.FFMPEG_OPTIONS = {
            "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            "options": "-vn",
        }

        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FILE = os.getenv("LOG_FILE", "bot.log")

        # Cache Configuration
        self.CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True").lower() == "true"
        self.CACHE_DIR = Path(os.getenv("CACHE_DIR", "cache"))
        self.CACHE_MAX_SIZE_MB = int(os.getenv("CACHE_MAX_SIZE_MB", "500"))

        # Feature Flags
        self.ENABLE_PLAYLISTS = os.getenv("ENABLE_PLAYLISTS", "True").lower() == "true"
        self.ENABLE_FILTERS = os.getenv("ENABLE_FILTERS", "True").lower() == "true"
        self.ENABLE_LYRICS = os.getenv("ENABLE_LYRICS", "False").lower() == "true"

    def _create_directories(self):
        """Cria diretórios necessários (chamado apenas no __init__)"""
        # Criar diretório de configurações
        if not self.CREDENTIALS_PATH.parent.exists():
            self.CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Criar diretório de cache
        if not self.CACHE_DIR.exists() and self.CACHE_ENABLED:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Criar diretório de logs
        log_path = Path(self.LOG_FILE).parent
        if not log_path.exists():
            log_path.mkdir(parents=True, exist_ok=True)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Valida se todas as configurações obrigatórias estão presentes
        SEM I/O - diretórios já foram criados no __init__

        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []

        if not self.DISCORD_TOKEN:
            errors.append("DISCORD_TOKEN não configurado")

        if not self.YOUTUBE_API_KEY and not (
            self.YOUTUBE_CLIENT_ID and self.YOUTUBE_CLIENT_SECRET
        ):
            errors.append(
                "Credenciais do YouTube não configuradas (API_KEY ou CLIENT_ID/SECRET)"
            )

        return len(errors) == 0, errors

    def get_ytdl_options(self) -> dict:
        """Retorna as opções configuradas para yt-dlp"""
        options = {
            "format": self.AUDIO_FORMAT,
            "noplaylist": not self.ENABLE_PLAYLISTS,
            "nocheckcertificate": True,
            "ignoreerrors": False,
            "logtostderr": False,
            "quiet": True,
            "no_warnings": True,
            "default_search": "auto",
            "source_address": "0.0.0.0",
            "extract_flat": False,
            "retries": 3,
            "fragment_retries": 3,
            "extractor_retries": 3,
            "skip_unavailable_fragments": True,
            "socket_timeout": 30,
        }

        # 🍪 Opcional: Usar cookies do navegador para vídeos com restrição de idade
        # Descomente a linha abaixo e escolha o navegador (chrome, firefox, edge, etc.)
        # options["cookiesfrombrowser"] = ("chrome",)  # ou "firefox", "edge", etc.

        return options

    @classmethod
    def get_instance(cls) -> "Config":
        """Retorna a instância única da configuração"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Instância global para fácil acesso
config = Config.get_instance()
