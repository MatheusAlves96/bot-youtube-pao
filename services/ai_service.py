"""
AI Service - Geração Inteligente de Queries para Autoplay
Usa Groq API (gratuita) com modelo Llama para análise musical
"""

import aiohttp
import asyncio
import json
from typing import Optional, Dict, Any, List
from core.logger import LoggerFactory
from config import config
from utils.quota_tracker import quota_tracker


class AIService:
    """Serviço de IA para gerar queries inteligentes de autoplay"""

    _instance: Optional["AIService"] = None

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
        self.api_key = config.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # Modelo rápido e gratuito
        
        # Cache de respostas (24h TTL)
        self._response_cache: Dict[str, tuple[Dict[str, Any], float]] = {}
        self._cache_ttl = 86400  # 24 horas em segundos

        if self.api_key:
            self.logger.info("✅ AIService inicializado com Groq API")
        else:
            self.logger.warning(
                "⚠️ GROQ_API_KEY não configurada - usando fallback manual"
            )

    async def generate_autoplay_query(
        self,
        current_title: str,
        current_channel: str,
        history: List[str] = None,
        strategy: int = 0,
    ) -> Dict[str, Any]:
        """
        Gera query inteligente baseada na música atual

        Args:
            current_title: Título da música atual
            current_channel: Canal/artista da música atual
            history: Lista de títulos já tocados (últimos 20)
            strategy: Estratégia de diversificação (0-3)

        Returns:
            Dict com: query, tipo, genero, internacional, explicacao
        """
        if not self.api_key:
            self.logger.debug("⚠️ Usando fallback (GROQ_API_KEY não configurada)")
            return self._fallback_query_generation(
                current_title, current_channel, strategy
            )

        history = history or []
        
        # Gerar chave de cache (title + channel + history_hash + strategy)
        import hashlib
        import time
        history_hash = hashlib.md5("".join(history[-5:]).encode()).hexdigest()[:8]
        cache_key = f"{current_title}:{current_channel}:{history_hash}:{strategy}"
        
        # Verificar cache
        if cache_key in self._response_cache:
            cached_response, cached_time = self._response_cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                self.logger.debug(f"✅ Cache HIT para autoplay query (age: {int(time.time() - cached_time)}s)")
                return cached_response
            else:
                # Cache expirado, remover
                del self._response_cache[cache_key]

        # Construir prompt para IA
        prompt = self._build_prompt(current_title, current_channel, history, strategy)

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um especialista em música que analisa músicas e gera queries de busca otimizadas para YouTube. Responda SEMPRE em JSON válido.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.3
                    + (strategy * 0.2),  # Mais criativo conforme estratégia aumenta
                    "max_tokens": 300,
                    "response_format": {"type": "json_object"},
                }

                timeout = aiohttp.ClientTimeout(total=10)
                async with session.post(
                    self.api_url, headers=headers, json=payload, timeout=timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(
                            f"❌ Erro na API Groq ({response.status}): {error_text[:200]}"
                        )
                        return self._fallback_query_generation(
                            current_title, current_channel, strategy
                        )

                    # ✅ Rastrear uso da API Groq
                    quota_tracker.track_operation(
                        "groq_autoplay", f"estratégia {strategy} | {current_title[:40]}"
                    )

                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]

                    # Parse da resposta JSON
                    analysis = json.loads(content)

                    self.logger.info(
                        f"🤖 IA gerou query: '{analysis.get('query', 'N/A')}'"
                    )
                    self.logger.debug(
                        f"   Tipo: {analysis.get('tipo', 'N/A')} | Gênero: {analysis.get('genero', 'N/A')}"
                    )
                    self.logger.debug(
                        f"   Internacional: {analysis.get('internacional', False)} | {analysis.get('explicacao', '')}"
                    )
                    
                    # Salvar no cache
                    import time
                    self._response_cache[cache_key] = (analysis, time.time())
                    self.logger.debug(f"💾 Resposta salva no cache (TTL: 24h)")

                    return analysis

        except asyncio.TimeoutError:
            self.logger.warning("⏱️ Timeout na API Groq - usando fallback")
            return self._fallback_query_generation(
                current_title, current_channel, strategy
            )
        except Exception as e:
            self.logger.error(f"❌ Erro ao chamar IA: {e}")
            return self._fallback_query_generation(
                current_title, current_channel, strategy
            )

    def _build_prompt(
        self, title: str, channel: str, history: List[str], strategy: int
    ) -> str:
        """Constrói prompt otimizado para IA"""

        strategy_descriptions = {
            0: "buscar músicas muito similares (mesmo gênero e estilo)",
            1: "expandir um pouco o gênero (artistas relacionados)",
            2: "explorar gêneros adjacentes (diversificar)",
            3: "buscar algo completamente diferente (evitar loop)",
        }

        history_str = (
            "\n".join(f"- {h}" for h in history[-10:])
            if history
            else "- (nenhuma música tocada ainda)"
        )

        prompt = f"""Analise esta música e gere uma query de busca otimizada para YouTube:

MÚSICA ATUAL:
- Título: "{title}"
- Canal/Artista: "{channel}"

HISTÓRICO RECENTE (últimas músicas tocadas - EVITE REPETIR):
{history_str}

ESTRATÉGIA DE BUSCA: {strategy_descriptions.get(strategy, "padrão")}

INSTRUÇÕES:
1. Detecte: artista principal, gênero musical, mood/energia, idioma (português/inglês/outro)
2. Identifique se é: música brasileira, internacional, indie, mainstream
3. Verifique se é: original, cover, remix, live, acústico
4. EVITE sugerir artistas/músicas que estão no histórico
5. Gere query que traga resultados DIVERSOS mas COERENTES musicalmente

REGRAS IMPORTANTES:
- Se música BRASILEIRA: adicione "brasileiro", "nacional" ou "br" na query
- Se música INTERNACIONAL: use termos em inglês como "official", "music", "similar to"
- Se estratégia 0-1: mantenha o gênero mas varie artistas
- Se estratégia 2-3: seja mais criativo e explore gêneros relacionados
- NUNCA repita exatamente os mesmos artistas do histórico
- Priorize termos que trazem músicas OFICIAIS (não covers/remixes)

Responda APENAS com JSON válido nesta estrutura EXATA:
{{
  "query": "query otimizada para busca no YouTube (string, 3-8 palavras)",
  "tipo": "artista_similar|genero|mood|exploratorio (string)",
  "genero": "gênero musical detectado (string)",
  "internacional": true ou false (boolean),
  "explicacao": "justificativa breve da query (string, max 60 chars)"
}}

EXEMPLO 1 - Música Brasileira (Estratégia 0):
Música: "Ari Acústico - A Droga do Amor"
{{
  "query": "rap melodico acustico brasileiro",
  "tipo": "genero",
  "genero": "rap acústico",
  "internacional": false,
  "explicacao": "Rap melódico acústico nacional similar"
}}

EXEMPLO 2 - Internacional (Estratégia 1):
Música: "Adele - Skyfall"
{{
  "query": "Sam Smith Amy Winehouse powerful vocals",
  "tipo": "artista_similar",
  "genero": "pop soul",
  "internacional": true,
  "explicacao": "Vozes poderosas soul/pop internacional"
}}

EXEMPLO 3 - Brasileira (Estratégia 2):
Música: "Djonga - Olho de Tigre"
{{
  "query": "rap consciente poesia brasileira",
  "tipo": "mood",
  "genero": "rap consciente",
  "internacional": false,
  "explicacao": "Expandindo para rap poético nacional"
}}"""

        return prompt

    def _fallback_query_generation(
        self, title: str, channel: str, strategy: int
    ) -> Dict[str, Any]:
        """Fallback manual caso IA não esteja disponível"""

        import re

        title_lower = title.lower()
        channel_lower = channel.lower()

        # Lista de artistas internacionais conhecidos
        international_artists = {
            "adele",
            "ed sheeran",
            "taylor swift",
            "drake",
            "beyoncé",
            "ariana grande",
            "billie eilish",
            "the weeknd",
            "dua lipa",
            "harry styles",
            "post malone",
            "travis scott",
            "kendrick lamar",
            "bruno mars",
            "rihanna",
            "justin bieber",
            "sia",
            "coldplay",
            "imagine dragons",
            "maroon 5",
            "one direction",
            "sam smith",
            "lewis capaldi",
            "shawn mendes",
            "camila cabello",
            "demi lovato",
            "selena gomez",
            "miley cyrus",
            "katy perry",
            "lady gaga",
            "pink",
            "eminem",
            "snoop dogg",
            "dr dre",
            "50 cent",
            "jay-z",
            "kanye west",
            "foo fighters",
            "linkin park",
            "green day",
            "red hot chili peppers",
            "amy winehouse",
            "jessie j",
            "alicia keys",
            "john legend",
            "frank ocean",
        }

        # Detectar se é internacional
        international_indicators = [
            "official video",
            "vevo",
            "lyrics",
            "official audio",
            "official music video",
        ]
        is_international = any(
            ind in title_lower for ind in international_indicators
        ) or any(artist in channel_lower for artist in international_artists)

        # Detectar gênero básico
        genre_keywords = {
            "rap": ["rap", "hip hop", "freestyle", "trap"],
            "trap": ["trap"],
            "funk": ["funk", "baile"],
            "rock": ["rock", "metal", "punk"],
            "pop": ["pop"],
            "acústico": ["acústico", "acoustic", "violão", "guitar"],
            "sertanejo": ["sertanejo", "country"],
            "pagode": ["pagode", "samba"],
            "reggae": ["reggae", "ska"],
        }

        detected_genre = None
        for genre, keywords in genre_keywords.items():
            if any(kw in title_lower or kw in channel_lower for kw in keywords):
                detected_genre = genre
                break

        # Gerar query baseada na estratégia
        if strategy == 0:
            # Busca similar ao gênero
            if detected_genre:
                if is_international:
                    query = f"{detected_genre} music official 2024"
                else:
                    query = f"{detected_genre} brasileiro oficial"
            else:
                # Buscar por artista
                artist = re.split(r"[-–(|]", title)[0].strip()
                if is_international:
                    query = f"{artist} similar artists music"
                else:
                    query = f"{artist} música brasileira"

        elif strategy == 1:
            # Busca por gênero expandido
            if detected_genre:
                if is_international:
                    query = f"{detected_genre} best songs 2023 2024"
                else:
                    query = f"{detected_genre} nacional 2024"
            else:
                query = (
                    "top music 2024" if is_international else "música brasileira 2024"
                )

        elif strategy == 2:
            # Busca exploratória relacionada
            if is_international:
                query = "indie alternative music official"
            else:
                query = "indie brasileiro música alternativa"

        else:
            # Busca ampla
            if is_international:
                query = "popular music official audio"
            else:
                query = "música brasileira popular oficial"

        return {
            "query": query,
            "tipo": "fallback",
            "genero": detected_genre or "desconhecido",
            "internacional": is_international,
            "explicacao": "Gerado automaticamente (IA indisponível)",
        }

    async def validate_videos(
        self,
        videos: List[Dict[str, str]],
        reference_title: str,
        reference_channel: str,
    ) -> List[Dict[str, Any]]:
        """
        Valida se os vídeos encontrados são músicas adequadas

        Args:
            videos: Lista de vídeos encontrados [{title, channel}, ...]
            reference_title: Título da música de referência
            reference_channel: Canal da música de referência

        Returns:
            Lista de vídeos validados com campo 'approved' (True/False) e 'reason'
        """
        if not self.api_key:
            self.logger.debug("⚠️ IA indisponível, aprovando todos os vídeos")
            return [
                {
                    **video,
                    "approved": True,
                    "reason": "IA indisponível (aprovação automática)",
                }
                for video in videos
            ]

        if not videos:
            return []

        try:
            # Construir prompt para validação
            videos_text = "\n".join(
                [
                    f"{i+1}. Título: \"{v['title']}\" | Canal: \"{v['channel']}\""
                    for i, v in enumerate(videos)
                ]
            )

            prompt = f"""Você é um especialista em música que valida se vídeos do YouTube são músicas adequadas para autoplay.

MÚSICA DE REFERÊNCIA:
Título: "{reference_title}"
Canal: "{reference_channel}"

VÍDEOS ENCONTRADOS:
{videos_text}

TAREFA: Analise cada vídeo e determine se é uma MÚSICA adequada ou CONTEÚDO INDESEJADO.

CONSIDERE CONTEÚDO INDESEJADO:
- Documentários, vídeos explicativos ("De onde vem...", "A história de...", "Quem é...")
- Podcasts, entrevistas, bate-papos (sem música de fundo)
- Reações, análises, reviews de músicas
- Tutoriais, aulas, making-of (sem ser a música em si)
- Gameplays, vlogs, desafios
- Compilações muito longas, playlists
- Vídeos motivacionais, meditação
- Qualquer conteúdo que NÃO seja música para ouvir

CONSIDERE MÚSICA ADEQUADA (SEJA FLEXÍVEL):
✅ Músicas oficiais (official audio/video)
✅ Participações/featurings (MC A, MC B, MC C)
✅ Covers, remixes, versões acústicas
✅ Clipes musicais, lyric videos
✅ Músicas ao vivo, apresentações
✅ Músicas do mesmo gênero ou artistas similares
✅ Qualquer música que é BOA para ouvir, mesmo que não seja do canal oficial

Responda APENAS com JSON válido:
{{
  "validations": [
    {{
      "index": 1,
      "approved": true ou false,
      "reason": "breve justificativa (max 50 chars)"
    }},
    ...
  ]
}}

IMPORTANTE:
- Seja FLEXÍVEL com músicas (covers, participações, remixes são BEM-VINDOS)
- Seja RIGOROSO com conteúdo não-musical (podcasts, reações, análises)
- Na dúvida entre música e não-música: APROVE a música"""

            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Você é um validador de conteúdo musical. Responda SEMPRE em JSON válido.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,  # Baixa temperatura para ser consistente
                    "max_tokens": 500,
                    "response_format": {"type": "json_object"},
                }

                timeout = aiohttp.ClientTimeout(total=15)
                async with session.post(
                    self.api_url, headers=headers, json=payload, timeout=timeout
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        self.logger.error(
                            f"❌ Erro na validação IA ({response.status}): {error_text[:200]}"
                        )
                        # Em caso de erro, aprovar todos (dar benefício da dúvida)
                        return [
                            {
                                **video,
                                "approved": True,
                                "reason": "Erro na IA (aprovado por padrão)",
                            }
                            for video in videos
                        ]

                    # Rastrear uso da API
                    quota_tracker.track_operation(
                        "groq_validation", f"validando {len(videos)} vídeos"
                    )

                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    validation_data = json.loads(content)

                    # Processar resultados
                    validated_videos = []
                    validations = validation_data.get("validations", [])

                    for i, video in enumerate(videos):
                        validation = next(
                            (v for v in validations if v.get("index") == i + 1), None
                        )

                        if validation:
                            approved = validation.get("approved", False)
                            reason = validation.get("reason", "Validado pela IA")

                            validated_videos.append(
                                {**video, "approved": approved, "reason": reason}
                            )

                            status = "✅" if approved else "❌"
                            self.logger.info(
                                f"{status} IA validação [{i+1}]: \"{video['title'][:50]}...\" - {reason}"
                            )
                        else:
                            # Se não encontrou validação, aprovar por segurança
                            validated_videos.append(
                                {
                                    **video,
                                    "approved": True,
                                    "reason": "Validação não encontrada (aprovado)",
                                }
                            )

                    return validated_videos

        except asyncio.TimeoutError:
            self.logger.warning("⏱️ Timeout na validação IA - aprovando todos")
            return [
                {**video, "approved": True, "reason": "Timeout (aprovado por padrão)"}
                for video in videos
            ]
        except Exception as e:
            self.logger.error(f"❌ Erro na validação IA: {e}")
            return [
                {**video, "approved": True, "reason": f"Erro: {str(e)[:30]}"}
                for video in videos
            ]

    @classmethod
    def get_instance(cls) -> "AIService":
        """Retorna instância singleton"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


# Instância global
ai_service = AIService.get_instance()
