"""
Logger Factory - Factory Pattern
Cria loggers configurados para diferentes módulos
"""
import logging
import colorlog
from pathlib import Path
from config import config


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
            '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            }
        )
        console_handler.setFormatter(console_formatter)

        # Handler para arquivo
        log_file = Path(config.LOG_FILE)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)

        # Adicionar handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
