"""
Logger Factory - Factory Pattern
Cria loggers configurados para diferentes módulos
"""

import logging
import colorlog
from pathlib import Path
from datetime import datetime
from config import config


class AutoplayLogger:
    """
    Logger especializado para Autoplay com arquivo dedicado
    Registra todo o fluxo: busca, filtros, validação IA, decisões
    """

    def __init__(self):
        self.logger = logging.getLogger("autoplay")
        self.logger.setLevel(logging.DEBUG)

        # Evita duplicação de handlers
        if self.logger.handlers:
            return

        # Arquivo dedicado para autoplay
        autoplay_log_file = Path("logs/autoplay.log")
        autoplay_log_file.parent.mkdir(parents=True, exist_ok=True)

        # Handler para arquivo autoplay (formato estruturado)
        file_handler = logging.FileHandler(autoplay_log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Formato detalhado para análise
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler (apenas INFO+)
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s🤖 AUTOPLAY | %(message)s",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log_session_start(self, reference_video: dict):
        """Inicia nova sessão de autoplay"""
        self.logger.info("=" * 80)
        self.logger.info(
            f"🎬 NOVA SESSÃO AUTOPLAY - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        self.logger.info(f"📀 Vídeo base: {reference_video.get('title', 'N/A')}")
        self.logger.info(f"👤 Canal: {reference_video.get('channel', 'N/A')}")
        self.logger.info("=" * 80)

    def log_search_strategy(self, strategy: int, query: str, source: str):
        """Registra estratégia de busca usada"""
        self.logger.debug(f"🎯 Estratégia #{strategy} | Fonte: {source}")
        self.logger.debug(f"🔍 Query gerada: '{query}'")

    def log_api_search(self, results_count: int, quota_used: int):
        """Registra resultado da busca API"""
        self.logger.debug(
            f"📡 YouTube API Search retornou {results_count} resultados (quota: +{quota_used})"
        )

    def log_batch_processing(self, candidate_count: int):
        """Registra início do processamento em batch"""
        self.logger.debug(f"📦 Processando {candidate_count} candidatos em batch...")

    def log_batch_duration_api(
        self, video_count: int, elapsed: float, speed: float, quota_saved: int
    ):
        """Registra resultado da API de duração em batch"""
        self.logger.debug(
            f"⚡ Batch Duration API: {video_count} vídeos em {elapsed:.2f}s "
            f"({speed:.1f} vídeos/s) - Economia: {quota_saved} chamadas!"
        )

    def log_duration_filter(
        self, video_title: str, duration: float, reason: str, passed: bool
    ):
        """Registra filtro de duração"""
        emoji = "✅" if passed else "⏭️"
        status = "APROVADO" if passed else "REJEITADO"
        self.logger.debug(
            f"{emoji} [{status}] {video_title[:60]} | {duration}min | {reason}"
        )

    def log_filter_summary(
        self, approved: int, rejected: int, min_duration: int, max_duration: int
    ):
        """Registra resumo dos filtros de duração"""
        total = approved + rejected
        approval_rate = (approved / total * 100) if total > 0 else 0
        self.logger.info(
            f"📊 Filtro de Duração: {approved}/{total} aprovados ({approval_rate:.1f}%) "
            f"| Limites: {min_duration}-{max_duration}min"
        )
        if rejected > 0:
            self.logger.debug(f"   ├─ {rejected} vídeos rejeitados por duração")

    def log_ai_validation_start(self, video_count: int):
        """Registra início da validação IA"""
        self.logger.info(f"🤖 Validando {video_count} vídeos com IA (Groq)...")

    def log_ai_validation_result(
        self, video_title: str, approved: bool, reason: str, confidence: float
    ):
        """Registra resultado da validação IA por vídeo"""
        emoji = "✅" if approved else "❌"
        status = "APROVADO" if approved else "REJEITADO"
        self.logger.debug(
            f"{emoji} IA [{status}] {video_title[:60]} | "
            f"Confiança: {confidence:.0%} | Razão: {reason}"
        )

    def log_ai_summary(self, approved: int, rejected: int, quota_used: int):
        """Registra resumo da validação IA"""
        total = approved + rejected
        approval_rate = (approved / total * 100) if total > 0 else 0
        self.logger.info(
            f"🎯 Validação IA: {approved}/{total} aprovados ({approval_rate:.1f}%) "
            f"| Quota Groq: +{quota_used}"
        )

    def log_final_selection(self, video_title: str, video_channel: str, video_url: str):
        """Registra vídeo selecionado para adicionar à fila"""
        self.logger.info(f"🎵 SELECIONADO: {video_title}")
        self.logger.debug(f"   ├─ Canal: {video_channel}")
        self.logger.debug(f"   └─ URL: {video_url}")

    def log_queue_added(self, video_title: str, queue_position: int):
        """Registra adição à fila"""
        self.logger.info(
            f"✅ Adicionado à fila (posição #{queue_position}): {video_title}"
        )

    def log_failure(self, attempt: int, max_attempts: int, reason: str):
        """Registra falha de tentativa"""
        self.logger.warning(
            f"⚠️ Tentativa {attempt}/{max_attempts} falhou | Razão: {reason}"
        )

    def log_session_end(self, success: bool, videos_added: int, total_time: float):
        """Finaliza sessão de autoplay"""
        emoji = "✅" if success else "❌"
        status = "SUCESSO" if success else "FALHA"
        self.logger.info(f"{emoji} Sessão finalizada: {status}")
        self.logger.info(
            f"📊 Vídeos adicionados: {videos_added} | Tempo total: {total_time:.2f}s"
        )
        self.logger.info("=" * 80 + "\n")

    def log_error(self, error_msg: str, exception: Exception = None):
        """Registra erro crítico"""
        self.logger.error(f"❌ ERRO: {error_msg}")
        if exception:
            self.logger.error(
                f"   └─ Exceção: {type(exception).__name__}: {str(exception)}"
            )


# Singleton do AutoplayLogger
autoplay_logger = AutoplayLogger()


class LoggerFactory:
    """
    Factory Pattern para criar loggers configurados
    """

    @staticmethod
    def create_logger(name: str) -> logging.Logger:
        """
        Cria e configura um logger

        Args:
            name: Nome do logger (geralmente __name__ do módulo)

        Returns:
            Logger configurado
        """
        logger = logging.getLogger(name)

        # Evita duplicação de handlers
        if logger.handlers:
            return logger

        logger.setLevel(getattr(logging, config.LOG_LEVEL))

        # Handler para console com cores
        console_handler = colorlog.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        console_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler.setFormatter(console_formatter)

        # Handler para arquivo
        log_file = Path(config.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)

        # Adicionar handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
