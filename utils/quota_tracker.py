"""
Quota Tracker - Monitoramento de uso da YouTube Data API v3
Rastreia consumo de quota e exibe estatísticas em tempo real
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from core.logger import LoggerFactory

logger = LoggerFactory.create_logger(__name__)


class QuotaTracker:
    """
    Singleton para rastrear uso de quota da YouTube API e Groq API
    """

    _instance = None

    # Limites da API (YouTube Data API v3 - Free Tier)
    DAILY_LIMIT = 10000
    PER_MINUTE_LIMIT = 1800000
    PER_MINUTE_PER_USER_LIMIT = 180000

    # Limites da Groq API (Free Tier)
    GROQ_DAILY_LIMIT = 14400  # 14.4K requests/day
    GROQ_PER_MINUTE_LIMIT = 30  # 30 requests/minute

    # Custos de cada operação
    OPERATION_COSTS = {
        "search": 100,
        "videos_list": 1,
        "channels_list": 1,
        "playlists_list": 1,
        "playlistItems_list": 1,
        "groq_autoplay": 1,  # 1 request por chamada de autoplay
        "groq_validation": 1,  # 1 request por validação de vídeos
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.cache_dir = Path(__file__).parent.parent / "cache"
        self.cache_dir.mkdir(exist_ok=True)
        self.quota_file = self.cache_dir / "quota_usage.json"

        # YouTube API counters
        self.daily_usage = 0
        self.minute_usage = 0
        self.operations_history: List[Dict] = []

        # Groq API counters
        self.groq_daily_usage = 0
        self.groq_minute_usage = 0
        self.groq_operations_history: List[Dict] = []

        self.current_minute = datetime.now().replace(second=0, microsecond=0)

        # 🆕 OTIMIZAÇÃO #6: Batch save (salvar a cada N operações)
        self._save_counter = 0
        self._save_interval = 10  # Salvar a cada 10 operações
        self._last_save_time = datetime.now()
        self._dirty = False  # Flag indicando mudanças não salvas

        self._load_usage()

    def _load_usage(self):
        """Carrega uso do dia do arquivo de cache"""
        if not self.quota_file.exists():
            return

        try:
            with open(self.quota_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Verifica se é do mesmo dia
            last_date = datetime.fromisoformat(data.get("date", "2000-01-01"))
            today = datetime.now().date()

            if last_date.date() == today:
                self.daily_usage = data.get("daily_usage", 0)
                self.operations_history = data.get("operations", [])
                self.groq_daily_usage = data.get("groq_daily_usage", 0)
                self.groq_operations_history = data.get("groq_operations", [])
                logger.info(
                    f"📊 Quota carregada - YouTube: {self.daily_usage}/{self.DAILY_LIMIT} | Groq: {self.groq_daily_usage}/{self.GROQ_DAILY_LIMIT}"
                )
            else:
                logger.info("📊 Novo dia! Resetando contadores de quota")
                self._reset_daily()

        except Exception as e:
            logger.error(f"❌ Erro ao carregar quota: {e}")

    def _save_usage(self):
        """Salva uso atual no arquivo"""
        try:
            data = {
                "date": datetime.now().isoformat(),
                "daily_usage": self.daily_usage,
                "operations": self.operations_history[-100:],  # Últimas 100 operações
                "groq_daily_usage": self.groq_daily_usage,
                "groq_operations": self.groq_operations_history[-100:],
            }

            with open(self.quota_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"❌ Erro ao salvar quota: {e}")

    def _reset_daily(self):
        """Reseta contadores diários"""
        self.daily_usage = 0
        self.operations_history = []
        self.groq_daily_usage = 0
        self.groq_operations_history = []
        self._save_usage()

    def _cleanup_minute_usage(self):
        """Remove operações antigas (mais de 1 minuto)"""
        now = datetime.now()
        current_minute = now.replace(second=0, microsecond=0)

        # Se mudou de minuto, limpa contador
        if current_minute != self.current_minute:
            self.current_minute = current_minute
            self.minute_usage = 0
            self.groq_minute_usage = 0

            # Remove operações antigas do histórico (mantém últimas 24h)
            cutoff = now - timedelta(hours=24)
            self.operations_history = [
                op
                for op in self.operations_history
                if datetime.fromisoformat(op["timestamp"]) > cutoff
            ]
            self.groq_operations_history = [
                op
                for op in self.groq_operations_history
                if datetime.fromisoformat(op["timestamp"]) > cutoff
            ]

    def track_operation(self, operation: str, details: str = ""):
        """
        Registra uma operação da API

        Args:
            operation: Tipo de operação (search, videos_list, groq_autoplay, etc)
            details: Detalhes adicionais (query, video_id, etc)
        """
        cost = self.OPERATION_COSTS.get(operation, 1)

        # Limpa operações antigas
        self._cleanup_minute_usage()

        # Verifica se é operação do Groq
        is_groq = operation.startswith("groq_")

        # Atualiza contadores apropriados
        if is_groq:
            self.groq_daily_usage += cost
            self.groq_minute_usage += cost

            # Registra operação do Groq
            operation_data = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "cost": cost,
                "details": details,
            }
            self.groq_operations_history.append(operation_data)
        else:
            self.daily_usage += cost
            self.minute_usage += cost

            # Registra operação do YouTube
            operation_data = {
                "timestamp": datetime.now().isoformat(),
                "operation": operation,
                "cost": cost,
                "details": details,
            }
            self.operations_history.append(operation_data)

        # 🆕 OTIMIZAÇÃO #6: Batch save ao invés de salvar toda operação
        self._dirty = True
        self._save_counter += 1

        # Decidir se deve salvar agora
        time_since_save = (datetime.now() - self._last_save_time).total_seconds()

        should_save = (
            self._save_counter >= self._save_interval  # A cada N ops
            or time_since_save > 300  # Ou a cada 5 minutos (segurança)
            or self._is_critical_threshold()  # Ou se chegou perto do limite
        )

        if should_save and self._dirty:
            self._save_usage()
            self._save_counter = 0
            self._last_save_time = datetime.now()
            self._dirty = False
            logger.debug(
                f"💾 Quota salva (counter: {self._save_counter}, "
                f"time: {time_since_save:.0f}s)"
            )

        # Log com estatísticas
        self._log_usage(operation, cost, details, is_groq)

        # Avisos se próximo dos limites
        self._check_limits()

    def _log_usage(
        self, operation: str, cost: int, details: str, is_groq: bool = False
    ):
        """Exibe log colorido com uso atual"""
        if is_groq:
            daily_percent = (self.groq_daily_usage / self.GROQ_DAILY_LIMIT) * 100
            minute_percent = (self.groq_minute_usage / self.GROQ_PER_MINUTE_LIMIT) * 100

            # Emoji baseado no percentual
            if daily_percent < 50:
                emoji = "🟢"
            elif daily_percent < 80:
                emoji = "🟡"
            else:
                emoji = "🔴"

            logger.info(
                f"{emoji} Groq API | {operation} (+{cost}) | "
                f"Dia: {self.groq_daily_usage:,}/{self.GROQ_DAILY_LIMIT:,} ({daily_percent:.1f}%) | "
                f"Min: {self.groq_minute_usage}/{self.GROQ_PER_MINUTE_LIMIT}"
            )
        else:
            daily_percent = (self.daily_usage / self.DAILY_LIMIT) * 100
            minute_percent = (self.minute_usage / self.PER_MINUTE_LIMIT) * 100

            # Emoji baseado no percentual
            if daily_percent < 50:
                emoji = "🟢"
            elif daily_percent < 80:
                emoji = "🟡"
            else:
                emoji = "🔴"

            logger.info(
                f"{emoji} YouTube API | {operation} (+{cost}) | "
                f"Dia: {self.daily_usage:,}/{self.DAILY_LIMIT:,} ({daily_percent:.1f}%) | "
                f"Min: {self.minute_usage:,}/{self.PER_MINUTE_LIMIT:,}"
            )

        if details:
            logger.debug(f"   └─ {details}")

    def _check_limits(self):
        """Verifica se está próximo dos limites"""
        # YouTube API limits
        daily_percent = (self.daily_usage / self.DAILY_LIMIT) * 100
        minute_percent = (self.minute_usage / self.PER_MINUTE_LIMIT) * 100

        # Aviso diário YouTube
        if daily_percent >= 90:
            logger.warning(
                f"⚠️ QUOTA CRÍTICA (YouTube): {self.daily_usage}/{self.DAILY_LIMIT} "
                f"({daily_percent:.1f}%) usado hoje!"
            )
        elif daily_percent >= 75:
            logger.warning(
                f"⚠️ Quota alta (YouTube): {self.daily_usage}/{self.DAILY_LIMIT} "
                f"({daily_percent:.1f}%) usado hoje"
            )

        # Aviso por minuto YouTube
        if minute_percent >= 50:
            logger.warning(
                f"⚠️ Alto uso por minuto (YouTube): {self.minute_usage:,}/{self.PER_MINUTE_LIMIT:,}"
            )

        # Groq API limits
        groq_daily_percent = (self.groq_daily_usage / self.GROQ_DAILY_LIMIT) * 100
        groq_minute_percent = (
            self.groq_minute_usage / self.GROQ_PER_MINUTE_LIMIT
        ) * 100

        # Aviso diário Groq
        if groq_daily_percent >= 90:
            logger.warning(
                f"⚠️ QUOTA CRÍTICA (Groq): {self.groq_daily_usage}/{self.GROQ_DAILY_LIMIT} "
                f"({groq_daily_percent:.1f}%) usado hoje!"
            )
        elif groq_daily_percent >= 75:
            logger.warning(
                f"⚠️ Quota alta (Groq): {self.groq_daily_usage}/{self.GROQ_DAILY_LIMIT} "
                f"({groq_daily_percent:.1f}%) usado hoje"
            )

        # Aviso por minuto Groq
        if groq_minute_percent >= 80:  # Groq tem limite menor (30/min)
            logger.warning(
                f"⚠️ Alto uso por minuto (Groq): {self.groq_minute_usage}/{self.GROQ_PER_MINUTE_LIMIT}"
            )

    def get_stats(self) -> Dict:
        """
        Retorna estatísticas detalhadas de uso

        Returns:
            Dict com estatísticas de uso
        """
        self._cleanup_minute_usage()

        # YouTube stats
        daily_percent = (self.daily_usage / self.DAILY_LIMIT) * 100
        daily_remaining = self.DAILY_LIMIT - self.daily_usage

        # Contagem de operações por tipo (últimas 24h)
        operations_count = {}
        for op in self.operations_history:
            op_type = op["operation"]
            operations_count[op_type] = operations_count.get(op_type, 0) + 1

        # Groq stats
        groq_daily_percent = (self.groq_daily_usage / self.GROQ_DAILY_LIMIT) * 100
        groq_daily_remaining = self.GROQ_DAILY_LIMIT - self.groq_daily_usage

        # Contagem de operações Groq por tipo
        groq_operations_count = {}
        for op in self.groq_operations_history:
            op_type = op["operation"]
            groq_operations_count[op_type] = groq_operations_count.get(op_type, 0) + 1

        return {
            # YouTube API
            "daily_usage": self.daily_usage,
            "daily_limit": self.DAILY_LIMIT,
            "daily_percent": daily_percent,
            "daily_remaining": daily_remaining,
            "minute_usage": self.minute_usage,
            "minute_limit": self.PER_MINUTE_LIMIT,
            "operations_count": operations_count,
            "total_operations": len(self.operations_history),
            # Groq API
            "groq_daily_usage": self.groq_daily_usage,
            "groq_daily_limit": self.GROQ_DAILY_LIMIT,
            "groq_daily_percent": groq_daily_percent,
            "groq_daily_remaining": groq_daily_remaining,
            "groq_minute_usage": self.groq_minute_usage,
            "groq_minute_limit": self.GROQ_PER_MINUTE_LIMIT,
            "groq_operations_count": groq_operations_count,
            "groq_total_operations": len(self.groq_operations_history),
            "last_reset": datetime.now()
            .replace(hour=0, minute=0, second=0)
            .isoformat(),
        }

    def format_stats(self) -> str:
        """
        Formata estatísticas para exibição

        Returns:
            String formatada com estatísticas
        """
        stats = self.get_stats()

        lines = [
            "📊 **Estatísticas de Uso das APIs**",
            "",
            "🎥 **YouTube Data API v3:**",
            f"├─ Quota Diária: {stats['daily_usage']:,} / {stats['daily_limit']:,} ({stats['daily_percent']:.1f}%)",
            f"├─ Restante: {stats['daily_remaining']:,} unidades",
            f"└─ Uso/minuto: {stats['minute_usage']:,} / {stats['minute_limit']:,}",
            "",
            f"**Operações YouTube (últimas 24h):**",
        ]

        for op_type, count in stats["operations_count"].items():
            cost = self.OPERATION_COSTS.get(op_type, 1)
            total_cost = count * cost
            lines.append(f"├─ {op_type}: {count}x (custo: {total_cost:,})")

        lines.append(f"└─ Total: {stats['total_operations']} operações")

        lines.extend(
            [
                "",
                "🤖 **Groq API (IA Autoplay):**",
                f"├─ Quota Diária: {stats['groq_daily_usage']:,} / {stats['groq_daily_limit']:,} ({stats['groq_daily_percent']:.1f}%)",
                f"├─ Restante: {stats['groq_daily_remaining']:,} requisições",
                f"└─ Uso/minuto: {stats['groq_minute_usage']} / {stats['groq_minute_limit']}",
                "",
                f"**Operações Groq (últimas 24h):**",
            ]
        )

        for op_type, count in stats["groq_operations_count"].items():
            lines.append(f"├─ {op_type}: {count}x")

        lines.append(f"└─ Total: {stats['groq_total_operations']} requisições")

        return "\n".join(lines)

    def _is_critical_threshold(self) -> bool:
        """
        Verifica se está perto de limites críticos (salvar imediatamente)

        Returns:
            True se deve salvar agora (perto de limites)
        """
        youtube_critical = (self.daily_usage / self.DAILY_LIMIT) > 0.9  # 90%
        groq_critical = (self.groq_daily_usage / self.GROQ_DAILY_LIMIT) > 0.9
        return youtube_critical or groq_critical

    def force_save(self):
        """
        Força salvamento imediato (chamar no shutdown do bot)

        Use caso:
            - Shutdown do bot
            - Antes de operações críticas
            - Testes
        """
        if self._dirty:
            self._save_usage()
            self._dirty = False
            self._save_counter = 0
            self._last_save_time = datetime.now()
            logger.info("💾 Quota salva (forçado)")
        else:
            logger.debug("💾 Quota já está salva")

    def can_make_request(self, operation: str = "search") -> bool:
        """
        Verifica se pode fazer uma requisição sem estourar limites

        Args:
            operation: Tipo de operação a ser realizada

        Returns:
            True se pode fazer a requisição
        """
        cost = self.OPERATION_COSTS.get(operation, 1)
        is_groq = operation.startswith("groq_")

        if is_groq:
            # Verifica limite diário Groq
            if self.groq_daily_usage + cost > self.GROQ_DAILY_LIMIT:
                logger.error(
                    f"❌ Quota diária Groq esgotada! {self.groq_daily_usage}/{self.GROQ_DAILY_LIMIT}"
                )
                return False

            # Verifica limite por minuto Groq
            if self.groq_minute_usage + cost > self.GROQ_PER_MINUTE_LIMIT:
                logger.warning(f"⚠️ Limite por minuto Groq atingido! Aguarde...")
                return False
        else:
            # Verifica limite diário YouTube
            if self.daily_usage + cost > self.DAILY_LIMIT:
                logger.error(
                    f"❌ Quota diária YouTube esgotada! {self.daily_usage}/{self.DAILY_LIMIT}"
                )
                return False

            # Verifica limite por minuto YouTube
            if self.minute_usage + cost > self.PER_MINUTE_LIMIT:
                logger.warning(f"⚠️ Limite por minuto YouTube atingido! Aguarde...")
                return False

        return True


# Instância global (Singleton)
quota_tracker = QuotaTracker()
