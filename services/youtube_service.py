"""
YouTube Service - Strategy Pattern
Gerencia autenticação e busca de vídeos do YouTube
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.logger import LoggerFactory
from config import config


class YouTubeAuthStrategy(ABC):
    """Strategy abstrata para autenticação YouTube"""

    @abstractmethod
    async def authenticate(self) -> Any:
        """Realiza autenticação e retorna cliente"""
        pass


class YouTubeOAuth2Strategy(YouTubeAuthStrategy):
    """Estratégia de autenticação OAuth2"""

    SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

    def __init__(self):
        self.logger = LoggerFactory.create_logger(__name__)
        self.credentials: Optional[Credentials] = None

    async def authenticate(self) -> Any:
        """
        Realiza autenticação OAuth2 do YouTube

        Returns:
            Cliente da API do YouTube autenticado
        """
        creds = None
        token_path = config.TOKEN_PATH
        credentials_path = config.CREDENTIALS_PATH

        # Carregar token salvo
        if token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(
                    str(token_path), self.SCOPES
                )
                self.logger.info("Token OAuth2 carregado do arquivo")
            except Exception as e:
                self.logger.warning(f"Erro ao carregar token: {e}")

        # Se não há credenciais válidas, fazer login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    self.logger.info("Token OAuth2 renovado")
                except Exception as e:
                    self.logger.error(f"Erro ao renovar token: {e}")
                    creds = None

            if not creds:
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        f"Arquivo de credenciais não encontrado: {credentials_path}\n"
                        "Baixe as credenciais OAuth2 do Google Cloud Console"
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(credentials_path), self.SCOPES
                )

                # Usar método local_server com porta fixa
                self.logger.info("=" * 60)
                self.logger.info("AUTENTICAÇÃO DO YOUTUBE NECESSÁRIA")
                self.logger.info("=" * 60)
                self.logger.info("1. Uma página será aberta no seu navegador")
                self.logger.info("2. Faça login com sua conta Google")
                self.logger.info("3. Autorize o acesso")
                self.logger.info("4. Você será redirecionado automaticamente")
                self.logger.info("=" * 60)

                # Usar porta fixa 8080
                creds = flow.run_local_server(port=8080, open_browser=True)
                self.logger.info(
                    "✅ Nova autenticação OAuth2 realizada com sucesso!"
                )  # Salvar token
            token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
            self.logger.info("Token OAuth2 salvo")

        self.credentials = creds
        return build("youtube", "v3", credentials=creds)


class YouTubeAPIKeyStrategy(YouTubeAuthStrategy):
    """Estratégia de autenticação via API Key"""

    def __init__(self):
        self.logger = LoggerFactory.create_logger(__name__)

    async def authenticate(self) -> Any:
        """
        Autenticação via API Key

        Returns:
            Cliente da API do YouTube com API Key
        """
        if not config.YOUTUBE_API_KEY:
            raise ValueError("YOUTUBE_API_KEY não configurada")

        self.logger.info("Usando autenticação via API Key")
        return build("youtube", "v3", developerKey=config.YOUTUBE_API_KEY)


class YouTubeService:
    """
    Serviço de YouTube usando Strategy Pattern
    Singleton para gerenciar conexão única
    """

    _instance: Optional["YouTubeService"] = None

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
        self.youtube = None
        self._auth_strategy: Optional[YouTubeAuthStrategy] = None

    def set_auth_strategy(self, strategy: YouTubeAuthStrategy):
        """Define a estratégia de autenticação"""
        self._auth_strategy = strategy

    async def initialize(self):
        """Inicializa o serviço e autentica"""
        if not self._auth_strategy:
            # Escolher estratégia automaticamente
            if config.YOUTUBE_CLIENT_ID and config.YOUTUBE_CLIENT_SECRET:
                self._auth_strategy = YouTubeOAuth2Strategy()
                self.logger.info("Usando OAuth2 para autenticação")
            elif config.YOUTUBE_API_KEY:
                self._auth_strategy = YouTubeAPIKeyStrategy()
                self.logger.info("Usando API Key para autenticação")
            else:
                raise ValueError("Nenhuma credencial do YouTube configurada")

        self.youtube = await self._auth_strategy.authenticate()
        self.logger.info("YouTube Service inicializado")

    async def search_video(
        self, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca vídeos no YouTube

        Args:
            query: Termo de busca
            max_results: Número máximo de resultados

        Returns:
            Lista de vídeos encontrados
        """
        if not self.youtube:
            await self.initialize()

        try:
            request = self.youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=max_results,
                videoCategoryId="10",  # Categoria Música
            )

            response = request.execute()

            videos = []
            for item in response.get("items", []):
                video = {
                    "id": item["id"]["videoId"],
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                    "url": f"https://www.youtube.com/watch?v={item['id']['videoId']}",
                }
                videos.append(video)

            self.logger.info(f"Encontrados {len(videos)} vídeos para: {query}")
            return videos

        except HttpError as e:
            self.logger.error(f"Erro na API do YouTube: {e}")
            return []

    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações detalhadas de um vídeo

        Args:
            video_id: ID do vídeo

        Returns:
            Informações do vídeo
        """
        if not self.youtube:
            await self.initialize()

        try:
            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics", id=video_id
            )

            response = request.execute()

            if not response.get("items"):
                return None

            item = response["items"][0]

            return {
                "id": item["id"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "description": item["snippet"]["description"],
                "duration": item["contentDetails"]["duration"],
                "views": item["statistics"].get("viewCount", "N/A"),
                "likes": item["statistics"].get("likeCount", "N/A"),
                "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
                "url": f"https://www.youtube.com/watch?v={item['id']}",
            }

        except HttpError as e:
            self.logger.error(f"Erro ao obter informações do vídeo: {e}")
            return None

    @classmethod
    def get_instance(cls) -> "YouTubeService":
        """Retorna a instância única do serviço"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
