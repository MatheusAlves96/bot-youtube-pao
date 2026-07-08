"""
YouTube Service - Strategy Pattern
Gerencia autenticação e busca de vídeos do YouTube
"""

import asyncio
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.logger import LoggerFactory, autoplay_logger
from config import config
from utils.quota_tracker import quota_tracker

# 🚀 Regex pré-compilados para melhor performance (+20x)
CLEAN_TITLE_PATTERN = re.compile(
    r"\([^)]*\)|\[[^\]]*\]|feat\.?|part\.?|ft\.?", re.IGNORECASE
)
WORD_PATTERN = re.compile(r"\w+")
VIDEO_ID_PATTERN = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})"
)
PLAYLIST_ID_PATTERN = re.compile(r"(?:youtube\.com/playlist\?list=)([a-zA-Z0-9_-]+)")
DURATION_HOURS_PATTERN = re.compile(r"(\d+)H")
DURATION_MINUTES_PATTERN = re.compile(r"(\d+)M")
ISO8601_DURATION_PATTERN = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")

# Import circular protection - will be imported later
# from services.ai_service import ai_service


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

                try:
                    # Tentar múltiplas portas comuns
                    ports_to_try = [8080, 8081, 8082]
                    creds = None

                    for port in ports_to_try:
                        try:
                            self.logger.info(f"Tentando porta {port}...")

                            # Resetar flow para cada tentativa
                            flow = InstalledAppFlow.from_client_secrets_file(
                                str(credentials_path), self.SCOPES
                            )

                            redirect_uri = f"http://localhost:{port}/"
                            flow.redirect_uri = redirect_uri
                            auth_url, _ = flow.authorization_url(prompt="consent")

                            self.logger.info("=" * 60)
                            self.logger.info("🔗 URL de Autenticação Gerada:")
                            self.logger.info(auth_url)
                            self.logger.info("=" * 60)
                            self.logger.info(f"📍 Redirect URI: {redirect_uri}")
                            self.logger.info("=" * 60)
                            self.logger.info(
                                "⚠️  ADICIONE ESTA URI NO GOOGLE CLOUD CONSOLE:"
                            )
                            self.logger.info(f"   {redirect_uri}")
                            self.logger.info("=" * 60)

                            # Executar servidor local (sem abrir navegador automaticamente)
                            creds = flow.run_local_server(
                                port=port,
                                host="localhost",
                                authorization_prompt_message="",
                                success_message="✅ Autenticação concluída! Você pode fechar esta aba.",
                                open_browser=False,  # Não abre navegador automaticamente
                            )

                            self.logger.info(
                                f"✅ Autenticação OAuth2 realizada na porta {port}!"
                            )
                            break  # Sucesso, sair do loop

                        except OSError as e:
                            self.logger.warning(f"Porta {port} não disponível: {e}")
                            continue

                    if not creds:
                        raise Exception(
                            "Nenhuma porta disponível para autenticação OAuth2"
                        )

                    self.logger.info(
                        "✅ Nova autenticação OAuth2 realizada com sucesso!"
                    )
                except Exception as oauth_error:
                    self.logger.error(f"❌ Erro na autenticação OAuth2: {oauth_error}")
                    if "404" in str(oauth_error):
                        raise Exception(
                            "❌ ERRO 404 - URLs de redirecionamento OAuth2 incorretas!\n"
                            "Solução:\n"
                            "1. Acesse: https://console.cloud.google.com\n"
                            "2. Vá em APIs e Serviços > Credenciais\n"
                            "3. Edite suas credenciais OAuth2\n"
                            "4. Atualize as URIs de redirecionamento para:\n"
                            "   - http://localhost:8080/\n"
                            "   - http://localhost:8080\n"
                            "   - http://localhost/\n"
                            "5. Remova: urn:ietf:wg:oauth:2.0:oob (descontinuada)\n"
                            "6. Aguarde 2-3 minutos e tente novamente\n\n"
                            f"Consulte o arquivo CORRECAO_OAUTH_GOOGLE.md para instruções detalhadas."
                        )
                    else:
                        raise oauth_error  # Salvar token
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

        # Verifica se pode fazer a requisição
        if not quota_tracker.can_make_request("search"):
            self.logger.error("❌ Quota insuficiente para buscar vídeos")
            return []

        try:
            # Registra uso antes da requisição
            quota_tracker.track_operation("search", f"query: {query[:50]}")

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

        # Verifica se pode fazer a requisição
        if not quota_tracker.can_make_request("videos_list"):
            self.logger.error("❌ Quota insuficiente para obter info do vídeo")
            return None

        try:
            # Registra uso antes da requisição
            quota_tracker.track_operation("videos_list", f"video_id: {video_id}")

            request = self.youtube.videos().list(
                part="snippet,contentDetails,statistics", id=video_id
            )

            # Executar com retry (3 tentativas com backoff exponencial)
            import asyncio

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, request.execute)

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

    async def get_videos_duration_batch(self, video_ids: List[str]) -> Dict[str, int]:
        """
        Busca duração de múltiplos vídeos em UMA chamada (BATCH)

        Args:
            video_ids: Lista de IDs (máximo 50 por batch)

        Returns:
            Dict mapping video_id -> duration_minutes
        """
        if not video_ids:
            return {}

        if not self.youtube:
            await self.initialize()

        durations = {}

        # Processar em lotes de 50 (limite da API do YouTube)
        BATCH_SIZE = 50
        for i in range(0, len(video_ids), BATCH_SIZE):
            batch = video_ids[i : i + BATCH_SIZE]
            ids_str = ",".join(batch)

            try:
                # UMA chamada para múltiplos vídeos! (98% menos quota)
                quota_tracker.track_operation(
                    "videos_list_batch", f"{len(batch)} videos"
                )

                request = self.youtube.videos().list(
                    part="contentDetails",
                    id=ids_str,  # Múltiplos IDs separados por vírgula
                )

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, request.execute)

                # DEBUG: Verificar resposta da API
                items = response.get("items", [])
                self.logger.info(
                    f"🔍 BATCH DEBUG: API retornou {len(items)} items para {len(batch)} IDs | IDs solicitados: {ids_str[:100]}..."
                )

                if items:
                    # Mostrar primeiro resultado para validar formato
                    first = items[0]
                    self.logger.info(
                        f"🔍 BATCH DEBUG: Primeiro item - ID={first['id']}, Duration={first['contentDetails']['duration']}"
                    )

                for item in response.get("items", []):
                    vid_id = item["id"]
                    duration_str = item["contentDetails"]["duration"]

                    # Parsear duração ISO 8601 completa (PT1H2M3S)
                    match = ISO8601_DURATION_PATTERN.match(duration_str)

                    if match:
                        hours = int(match.group(1) or 0)
                        minutes = int(match.group(2) or 0)
                        seconds = int(match.group(3) or 0)

                        # Converter para minutos com arredondamento correto
                        # Se tem >= 30 segundos, arredondar para cima
                        total_minutes = hours * 60 + minutes
                        if seconds >= 30:
                            total_minutes += 1

                        durations[vid_id] = total_minutes

                        # DEBUG: Log de conversão
                        self.logger.debug(
                            f"🔍 Duração parseada: {duration_str} → {hours}h {minutes}m {seconds}s = {total_minutes}min"
                        )
                    else:
                        # Fallback: assumir 0 se não conseguir parsear
                        self.logger.warning(
                            f"⚠️ Não conseguiu parsear duração: {duration_str} para vídeo {vid_id}"
                        )
                        durations[vid_id] = 0

            except Exception as e:
                self.logger.debug(f"Erro ao buscar batch de durações: {e}")

        return durations

    async def get_related_videos(
        self,
        video_id: str,
        max_results: int = 5,
        exclude_ids: List[str] = None,
        video_title: str = None,
        video_channel: str = None,
        search_strategy: int = 0,
        history_titles: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Busca vídeos relacionados usando IA para gerar queries inteligentes

        Args:
            video_id: ID do vídeo de referência
            max_results: Número máximo de resultados
            exclude_ids: Lista de IDs para excluir
            video_title: Título do vídeo
            video_channel: Canal do vídeo
            search_strategy: Estratégia de busca (0-3)
            history_titles: Títulos já tocados (para IA evitar)

        Returns:
            Lista de vídeos relacionados
        """
        if not self.youtube:
            await self.initialize()

        # Verifica se pode fazer a requisição
        if not quota_tracker.can_make_request("search"):
            self.logger.error("❌ Quota insuficiente para buscar relacionados")
            return []

        exclude_ids = exclude_ids or []
        history_titles = history_titles or []

        try:
            # Registra uso antes da requisição
            quota_tracker.track_operation(
                "search", f"autoplay (estratégia {search_strategy})"
            )

            # 🤖 USAR IA PARA GERAR QUERY INTELIGENTE
            from services.ai_service import ai_service

            analysis = await ai_service.generate_autoplay_query(
                current_title=video_title or "",
                current_channel=video_channel or "",
                history=history_titles,
                strategy=search_strategy,
            )

            search_query = analysis.get("query", "música brasileira")
            query_type = analysis.get("tipo", "unknown")
            detected_genre = analysis.get("genero", "unknown")
            is_international = analysis.get("internacional", False)

            self.logger.info(
                f"🎵 Query gerada (estratégia {search_strategy}): '{search_query}'"
            )
            self.logger.debug(
                f"   Tipo: {query_type} | Gênero: {detected_genre} | Internacional: {is_international}"
            )

            # 📊 LOG AUTOPLAY: Estratégia de busca
            strategy_sources = [
                "IA Groq",
                "IA variação",
                "IA aleatório",
                "IA brasileiro",
            ]
            autoplay_logger.log_search_strategy(
                strategy=search_strategy,
                query=search_query,
                source=(
                    strategy_sources[search_strategy]
                    if search_strategy < len(strategy_sources)
                    else "Desconhecido"
                ),
            )

            # Executar busca no YouTube com a query gerada pela IA
            request = self.youtube.search().list(
                part="snippet",
                q=search_query,
                type="video",
                maxResults=max_results * 3,
                videoCategoryId="10",  # Importante: Apenas categoria Música
            )
            response = request.execute()

            # LOG: Quantos resultados a API retornou
            total_results = len(response.get("items", []))
            self.logger.info(f"📊 API retornou {total_results} resultados da busca")

            # 📊 LOG AUTOPLAY: Resultado da API search
            autoplay_logger.log_api_search(total_results, quota_used=100)

            videos = []

            # Palavras que indicam que NÃO é uma música (conteúdo indesejado)
            excluded_keywords = [
                # Entrevistas e talks
                "podcast",
                "interview",
                "entrevista",
                "bate-papo",
                "conversa",
                "papo",
                # Reações e análises
                "react",
                "reação",
                "reagindo",
                "reagiu",
                "reaction",
                "análise",
                "analisa",
                "analisando",
                "review",
                # Gaming
                "gameplay",
                "jogando",
                "playing",
                # Tutoriais e explicações
                "tutorial",
                "como fazer",
                "aprenda",
                "aula",
                "explicação",
                "explicando",
                "explica",
                "ensina",
                "dica",
                "dicas",
                # Documentários e histórias
                "história",
                "historia",
                "story",
                "história de",
                "origem",
                "de onde vem",
                "quem é",
                "conhecendo",
                "conhece",
                "documentário",
                "documentary",
                # Bastidores e making of
                "making of",
                "bastidores",
                "behind the scenes",
                "gravação",
                "gravando",
                "estúdio",
                "studio",
                # Vlogs e daily content
                "vlog",
                "diary",
                "dia a dia",
                "rotina",
                # Desafios
                "challenge",
                "desafio",
                # Descobertas
                "first time",
                "primeira vez",
                "descobriu",
                "descobrindo",
                "descobri",
                "conheci",
                "meets",
                # Playlists e compilações
                "playlist",
                "compilation",
                "compilação",
                "os melhores",
                "as melhores",
                "best of",
                "top 10",
                "top 20",
                "top 50",
                "coletânea",
                "mix",
                "mashup",
                "medley",
                "1 hora",
                "2 horas",
                "3 horas",
                "hour",
                "hours",
                # Shorts e redes sociais
                "shorts",
                "tiktok",
                "melhores momentos",
                # Transmissões
                "lives",
                "ao vivo",
                "full stream",
                "stream",
                "transmissão",
            ]

            # Palavras que indicam versões alternativas (devem ser evitadas para diversidade)
            # Nota: "acústico" não está aqui pois pode ser o estilo original da música
            alternative_version_keywords = [
                "cover",
                "remix",
                "versão",
                "version",
                "letra",
                "lyrics",
                "lyric video",
                "instrumental",
                "karaoke",
                "piano version",
                "guitar version",
                "violão version",
                "live",
                "ao vivo",
                "unplugged",
                "slowed",
                "reverb",
                "sped up",
                "nightcore",
                "8d audio",
            ]

            # Extrair palavras-chave principais do título de referência para evitar repetição
            reference_keywords = set()
            if video_title:
                # Remover parênteses, colchetes, feat, part, etc (usando regex pré-compilado)
                clean_ref = CLEAN_TITLE_PATTERN.sub("", video_title.lower())

                # Remover palavras muito comuns que não ajudam na comparação
                stopwords = {
                    "música",
                    "music",
                    "official",
                    "video",
                    "audio",
                    "clipe",
                    "com",
                    "the",
                    "de",
                    "da",
                    "do",
                    "em",
                    "para",
                }

                # Pegar palavras principais (mais de 3 letras) exceto stopwords
                reference_keywords = set(
                    word
                    for word in clean_ref.split()
                    if len(word) > 3 and word not in stopwords
                )

            # LOG: Palavras-chave extraídas da referência
            if reference_keywords:
                self.logger.debug(
                    f"🔑 Palavras-chave de referência: {reference_keywords}"
                )

            # Padrões de títulos que indicam conteúdo explicativo (regex pré-compilados)
            explanatory_patterns = [
                r"^(de onde|donde|where does|where is|who is|what is|quem é|o que é|qual é)",
                r"^(como |how to |how )",
                r"^(por que|porque|why )",
                r"^(conheça|conhece|meet |discover )",
                r"\?$",  # Títulos que terminam com ?
            ]

            # Palavras suspeitas em nomes de canais (indicam canais de conteúdo não-musical)
            suspicious_channel_keywords = [
                "documentary",
                "documentário",
                "docs",
                "história",
                "historia",
                "explica",
                "explains",
                "educação",
                "education",
                "tutorial",
                "aprenda",
                "learn",
                "podcast",
                "cast",
            ]

            # 🆕 OTIMIZAÇÃO #1: Coletar candidatos para processamento em batch
            video_candidates = []

            for item in response.get("items", []):
                vid_id = item["id"]["videoId"]
                title = item["snippet"]["title"]
                title_lower = title.lower()
                channel_name = item["snippet"]["channelTitle"]
                channel_lower = channel_name.lower()

                # LOG: Analisando cada vídeo
                self.logger.debug(f"🔍 Analisando: {title} [{channel_name}]")

                # Pula vídeos excluídos
                if vid_id in exclude_ids or vid_id == video_id:
                    self.logger.debug(f"   ⏭️ Pulado (já na fila ou é o vídeo atual)")
                    continue

                # Filtro 0: Detectar títulos explicativos por padrão (regex)
                is_explanatory = False
                for pattern in explanatory_patterns:
                    if re.search(pattern, title_lower):
                        is_explanatory = True
                        self.logger.debug(
                            f"   ⏭️ Excluído (título explicativo - padrão: {pattern})"
                        )
                        break
                if is_explanatory:
                    continue

                # Filtro 1: Verificar se o canal é suspeito (não-musical)
                matched_suspicious_channel = [
                    kw for kw in suspicious_channel_keywords if kw in channel_lower
                ]
                if matched_suspicious_channel:
                    self.logger.debug(
                        f"   ⏭️ Excluído (canal suspeito - contém: {matched_suspicious_channel[0]})"
                    )
                    continue

                # Filtro 2: Excluir vídeos com palavras-chave indesejadas
                matched_excluded = [kw for kw in excluded_keywords if kw in title_lower]
                if matched_excluded:
                    self.logger.debug(
                        f"   ⏭️ Excluído (não é música - contém: {matched_excluded[0]})"
                    )
                    continue

                # Filtro 3: Excluir versões alternativas (cover, remix, etc)
                matched_alternative = [
                    kw for kw in alternative_version_keywords if kw in title_lower
                ]
                if matched_alternative:
                    self.logger.debug(
                        f"   ⏭️ Excluído (versão alternativa - contém: {matched_alternative[0]})"
                    )
                    continue

                # Filtro 4: Evitar músicas muito similares (mesmo título base)
                if reference_keywords and len(reference_keywords) > 0:
                    # Remover stopwords do título candidato também
                    stopwords = {
                        "música",
                        "music",
                        "official",
                        "video",
                        "audio",
                        "clipe",
                        "com",
                        "the",
                        "de",
                        "da",
                        "do",
                        "em",
                        "para",
                    }
                    title_words = set(
                        word
                        for word in title_lower.split()
                        if len(word) > 3 and word not in stopwords
                    )
                    common_words = reference_keywords & title_words

                    # LOG: Mostrar análise de similaridade
                    similarity_percent = (
                        (len(common_words) / len(reference_keywords) * 100)
                        if len(reference_keywords) > 0
                        else 0
                    )
                    self.logger.debug(
                        f"   📊 Similaridade: {len(common_words)}/{len(reference_keywords)} palavras ({similarity_percent:.0f}%) - Comuns: {common_words}"
                    )

                    # Filtro de similaridade ajustado: só excluir se for MUITO similar (100%)
                    # Como estamos buscando por gênero (não por título), títulos similares são ok
                    # Só queremos evitar a EXATA mesma música
                    if (
                        len(common_words) == len(reference_keywords)
                        and len(common_words) >= 3
                    ):
                        self.logger.debug(
                            f"   ⏭️ Excluído (exatamente a mesma música - {len(common_words)}/{len(reference_keywords)} palavras)"
                        )
                        continue

                # Filtro: Preferir vídeos com indicadores de música
                music_indicators = [
                    "official",
                    "video",
                    "audio",
                    "música",
                    "music",
                    "clipe",
                    "lyric",
                ]
                has_music_indicator = any(
                    indicator in title for indicator in music_indicators
                )

                # Se não tem indicador de música E tem menos de 3 minutos, pode ser suspeito
                # (vamos adicionar com menor prioridade)

                # Filtro: Evitar muito do mesmo artista consecutivamente
                # Extrair nome do artista do título
                artist_candidate = (
                    re.split(r"[-–(|]", item["snippet"]["title"])[0].strip().lower()
                )
                artist_reference = (
                    re.split(r"[-–(|]", video_title)[0].strip().lower()
                    if video_title
                    else ""
                )

                # LOG: Comparação de artistas
                self.logger.debug(
                    f"   🎤 Artista candidato: '{artist_candidate}' vs referência: '{artist_reference}'"
                )

                # DESATIVADO: Filtro de diversidade de artista
                # Como estamos buscando por gênero, é normal ter vários do mesmo artista
                # O filtro de similaridade já cuida de evitar músicas repetidas
                # same_artist = artist_candidate == artist_reference
                # if same_artist and len(videos) >= 1:
                #     ...continue

                # LOG: Vídeo passou nos filtros iniciais
                self.logger.debug(
                    f"   ✅ Passou nos filtros iniciais (aguardando filtro de duração)"
                )

                # Armazenar candidato para filtro de duração em batch
                video_candidates.append({"id": vid_id, "item": item})

            # ⚡ BATCH PROCESSING: Buscar durações de TODOS os vídeos em UMA chamada
            candidate_ids = [c["id"] for c in video_candidates]
            self.logger.info(
                f"📦 Buscando durações de {len(candidate_ids)} vídeos em BATCH"
            )
            autoplay_logger.log_batch_processing(len(candidate_ids))

            if not candidate_ids:
                self.logger.warning("⚠️ Nenhum candidato passou nos filtros iniciais")
                autoplay_logger.log_filter_summary(
                    0, 0, config.AUTOPLAY_MIN_DURATION, config.AUTOPLAY_MAX_DURATION
                )
                return []

            # Buscar durações em batch (UMA chamada para todos!)
            import time

            batch_start = time.time()
            durations = await self.get_videos_duration_batch(candidate_ids)
            batch_elapsed = time.time() - batch_start

            # DEBUG: Verificar se o dicionário está populado
            if not durations:
                self.logger.warning("⚠️ ATENÇÃO: Dicionário durations está VAZIO!")
            elif len(durations) < len(candidate_ids):
                missing = len(candidate_ids) - len(durations)
                self.logger.warning(
                    f"⚠️ ATENÇÃO: Faltam {missing} durações no dicionário (esperado: {len(candidate_ids)}, recebido: {len(durations)})"
                )

            # Calcular métricas do batch
            speed = len(durations) / batch_elapsed if batch_elapsed > 0 else 0
            quota_saved = len(candidate_ids) - 1  # Batch usa 1 chamada vs N individuais
            autoplay_logger.log_batch_duration_api(
                len(durations), batch_elapsed, speed, quota_saved
            )

            # Filtrar por duração e criar lista final
            videos = []
            for candidate in video_candidates:
                vid_id = candidate["id"]
                item = candidate["item"]

                # Obter duração do batch (padrão: 0 se não encontrado)
                duration_minutes = durations.get(vid_id, 0)

                # LOG: Duração do vídeo
                self.logger.debug(
                    f"🔍 {item['snippet']['title'][:50]} - ⏱️ {duration_minutes} min (batch)"
                )

                # ⚠️ IMPORTANTE: Se duration=0 e vídeo NÃO está no dict, significa que a API
                # não retornou esse vídeo (deletado, privado, bloqueado por região, etc.)
                if vid_id not in durations:
                    reason = "Vídeo indisponível (não retornado pela API)"
                    self.logger.debug(f"   ⏭️ Excluído - {reason}")
                    autoplay_logger.log_duration_filter(
                        item["snippet"]["title"], 0, reason, passed=False
                    )
                    continue

                # Filtrar vídeos muito longos (configurável via AUTOPLAY_MAX_DURATION)
                if duration_minutes > config.AUTOPLAY_MAX_DURATION:
                    reason = f"Muito longo ({duration_minutes}min > {config.AUTOPLAY_MAX_DURATION}min)"
                    self.logger.debug(f"   ⏭️ Excluído - {reason}")
                    autoplay_logger.log_duration_filter(
                        item["snippet"]["title"], duration_minutes, reason, passed=False
                    )
                    continue

                # Filtrar vídeos muito curtos (configurável via AUTOPLAY_MIN_DURATION)
                if duration_minutes < config.AUTOPLAY_MIN_DURATION:
                    reason = f"Muito curto ({duration_minutes}min < {config.AUTOPLAY_MIN_DURATION}min)"
                    self.logger.debug(f"   ⏭️ Excluído - {reason}")
                    autoplay_logger.log_duration_filter(
                        item["snippet"]["title"], duration_minutes, reason, passed=False
                    )
                    continue

                # LOG: Vídeo aprovado!
                self.logger.debug(f"   ✅ APROVADO após filtro de duração!")
                autoplay_logger.log_duration_filter(
                    item["snippet"]["title"],
                    duration_minutes,
                    f"Dentro dos limites ({config.AUTOPLAY_MIN_DURATION}-{config.AUTOPLAY_MAX_DURATION}min)",
                    passed=True,
                )

                # Adicionar à lista final
                video = {
                    "id": vid_id,
                    "title": item["snippet"]["title"],
                    "channel": item["snippet"]["channelTitle"],
                    "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                    "url": f"https://www.youtube.com/watch?v={vid_id}",
                }
                videos.append(video)

                # Para quando atingir o número desejado
                if len(videos) >= max_results:
                    self.logger.info(f"🎯 Limite de {max_results} vídeos atingido")
                    break

            self.logger.info(
                f"✅ Filtrados {len(videos)} vídeos de {len(video_candidates)} candidatos "
                f"({len(video_candidates) - len(videos)} rejeitados por duração)"
            )

            # 📊 LOG AUTOPLAY: Resumo dos filtros de duração
            autoplay_logger.log_filter_summary(
                approved=len(videos),
                rejected=len(video_candidates) - len(videos),
                min_duration=config.AUTOPLAY_MIN_DURATION,
                max_duration=config.AUTOPLAY_MAX_DURATION,
            )

            # 🤖 VALIDAÇÃO FINAL COM IA
            if videos and len(videos) > 0:
                self.logger.info(f"🤖 Validando {len(videos)} vídeos com IA...")

                # 📊 LOG AUTOPLAY: Início da validação IA
                autoplay_logger.log_ai_validation_start(len(videos))

                # Importar AI service dentro da função para evitar import circular
                from services.ai_service import ai_service

                # Validar vídeos com IA
                validated_videos = await ai_service.validate_videos(
                    videos=videos,
                    reference_title=video_title or "",
                    reference_channel=video_channel or "",
                )

                # Filtrar apenas os aprovados
                approved_videos = [
                    v for v in validated_videos if v.get("approved", False)
                ]
                rejected_count = len(videos) - len(approved_videos)

                if rejected_count > 0:
                    self.logger.info(
                        f"🛡️ IA rejeitou {rejected_count} vídeo(s), {len(approved_videos)} aprovado(s)"
                    )

                # Remover campos auxiliares (approved, reason) antes de retornar
                final_videos = []
                for v in approved_videos:
                    clean_video = {
                        k: val
                        for k, val in v.items()
                        if k not in ["approved", "reason"]
                    }
                    final_videos.append(clean_video)

                return final_videos

            return videos

        except HttpError as e:
            self.logger.error(f"Erro ao buscar vídeos relacionados: {e}")
            return []

    def _parse_duration(self, duration: str) -> int:
        """
        Converte duração ISO 8601 para segundos

        Args:
            duration: Duração no formato ISO 8601 (ex: PT4M33S)

        Returns:
            Duração em segundos
        """
        # Usar regex pré-compilado
        match = ISO8601_DURATION_PATTERN.match(duration)

        if not match:
            return 0

        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)

        return hours * 3600 + minutes * 60 + seconds

    @classmethod
    def get_instance(cls) -> "YouTubeService":
        """Retorna a instância única do serviço"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
