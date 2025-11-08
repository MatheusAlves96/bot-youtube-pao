"""
YouTube Music Discord Bot
Ponto de entrada da aplicação
"""

import asyncio
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# IMPORTANTE: Carregar variáveis de ambiente ANTES de importar o config
from dotenv import load_dotenv

load_dotenv()

from core import MusicBot, LoggerFactory
from config import config


def main():
    """Função principal"""

    # Configurar logger
    logger = LoggerFactory.create_logger(__name__)

    logger.info("=" * 50)
    logger.info("YouTube Music Discord Bot")
    logger.info("=" * 50)

    try:
        # Criar instância do bot
        music_bot = MusicBot.get_instance()

        # Carregar cogs
        async def load_extensions():
            await music_bot.load_cogs()

        # Executar carregamento de cogs
        asyncio.run(load_extensions())

        # Iniciar bot
        logger.info("Iniciando bot...")
        music_bot.run()

    except KeyboardInterrupt:
        logger.info("Bot encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
