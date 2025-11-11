"""
YouTube Music Discord Bot
Ponto de entrada da aplicação
"""

import asyncio
import sys
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# IMPORTANTE: Carregar variáveis de ambiente ANTES de importar o config
from dotenv import load_dotenv

load_dotenv()

from core import MusicBot, LoggerFactory
from config import config


class BotRunner:
    """Gerenciador de execução do bot com suporte a threading"""

    def __init__(self):
        self.logger = LoggerFactory.create_logger(__name__)
        self.music_bot = None
        self.bot_thread = None
        self.shutdown_event = threading.Event()
        self.loop = None

    def run_bot_in_thread(self):
        """Executa o bot em uma thread separada"""
        try:
            # Criar novo loop de eventos para esta thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Carregar cogs
            self.loop.run_until_complete(self.music_bot.load_cogs())

            # Executar bot
            self.logger.info("🤖 Bot iniciado na thread")
            self.loop.run_until_complete(
                self.music_bot.start_async(config.DISCORD_TOKEN)
            )

        except Exception as e:
            self.logger.error(f"Erro na thread do bot: {e}", exc_info=True)
        finally:
            self.logger.info("Thread do bot encerrada")

    def start(self):
        """Inicia o bot"""
        self.logger.info("=" * 50)
        self.logger.info("YouTube Music Discord Bot")
        self.logger.info("=" * 50)

        # Validar configuração
        is_valid, errors = config.validate()
        if not is_valid:
            self.logger.error("Configuração inválida:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return False

        # Criar instância do bot
        self.music_bot = MusicBot.get_instance()

        # Iniciar bot em thread separada
        self.bot_thread = threading.Thread(target=self.run_bot_in_thread, daemon=False)
        self.bot_thread.start()

        self.logger.info("✅ Bot iniciado (Pressione Ctrl+C para encerrar)")
        return True

    def stop(self):
        """Para o bot graciosamente"""
        if self.shutdown_event.is_set():
            self.logger.warning("⚠️  Já está encerrando...")
            return

        self.shutdown_event.set()
        self.logger.info("\n🛑 Iniciando encerramento gracioso...")

        try:
            if self.music_bot and self.loop and not self.loop.is_closed():
                # Agendar encerramento no loop do bot
                future = asyncio.run_coroutine_threadsafe(
                    self.music_bot.shutdown(), self.loop
                )
                # Aguardar até 5 segundos pelo encerramento
                try:
                    future.result(timeout=5)
                except Exception as e:
                    self.logger.warning(f"Timeout no encerramento: {e}")

            # Aguardar thread terminar
            if self.bot_thread and self.bot_thread.is_alive():
                self.logger.info("Aguardando thread do bot...")
                self.bot_thread.join(timeout=3)

                if self.bot_thread.is_alive():
                    self.logger.warning("⚠️  Thread não respondeu a tempo")

        except Exception as e:
            self.logger.error(f"Erro durante encerramento: {e}")
        finally:
            self.logger.info("✅ Encerramento concluído")

    def wait(self):
        """Aguarda até que Ctrl+C seja pressionado"""
        try:
            # Aguardar a thread do bot
            while self.bot_thread and self.bot_thread.is_alive():
                self.bot_thread.join(timeout=0.5)

        except KeyboardInterrupt:
            self.logger.info("\n🛑 Ctrl+C detectado!")
            self.stop()


def main():
    """Função principal"""
    logger = LoggerFactory.create_logger(__name__)

    # Verificar se há múltiplas instâncias
    try:
        import psutil
        import os

        current_pid = os.getpid()
        python_processes = [
            p
            for p in psutil.process_iter(["pid", "name", "cmdline"])
            if p.info["name"]
            and "python" in p.info["name"].lower()
            and p.info["cmdline"]
            and "main.py" in " ".join(p.info["cmdline"])
        ]

        if len(python_processes) > 1:
            logger.warning("⚠️" * 20)
            logger.warning(
                f"⚠️ ATENÇÃO: Detectadas {len(python_processes)} instâncias do bot rodando!"
            )
            logger.warning(f"⚠️ PID Atual: {current_pid}")
            for p in python_processes:
                logger.warning(f"⚠️ Processo encontrado - PID: {p.info['pid']}")
            logger.warning("⚠️ Isso pode causar comandos duplicados!")
            logger.warning("⚠️ Feche as outras instâncias antes de continuar.")
            logger.warning("⚠️" * 20)
    except ImportError:
        pass  # psutil não instalado, ignorar verificação
    except Exception as e:
        logger.warning(f"Não foi possível verificar múltiplas instâncias: {e}")

    runner = BotRunner()

    try:
        if not runner.start():
            sys.exit(1)

        # Aguardar até encerramento
        runner.wait()

    except KeyboardInterrupt:
        runner.logger.info("\n🛑 KeyboardInterrupt capturado")
        runner.stop()

    except Exception as e:
        runner.logger.error(f"❌ Erro fatal: {e}", exc_info=True)
        sys.exit(1)

    finally:
        runner.logger.info("👋 Até logo!")


if __name__ == "__main__":
    main()
