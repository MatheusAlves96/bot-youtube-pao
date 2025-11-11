"""
Bot Client Core - Singleton Pattern
"""

import asyncio
import discord
from discord.ext import commands
from typing import Optional
import logging
from config import config


class MusicBot:
    """
    Bot principal usando Singleton Pattern
    Garante uma única instância do bot em execução
    """

    _instance: Optional["MusicBot"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.logger = logging.getLogger(__name__)

        # Configurar intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True

        # Criar bot
        self.bot = commands.Bot(
            command_prefix=config.COMMAND_PREFIX, intents=intents, help_command=None
        )

        self._setup_events()

    def _setup_events(self):
        """Configura eventos básicos do bot"""

        @self.bot.event
        async def on_ready():
            self.logger.info(f"{self.bot.user} está online!")
            self.logger.info(f"ID: {self.bot.user.id}")
            self.logger.info(f"Servidores: {len(self.bot.guilds)}")

            # Configurar status
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=f"{config.COMMAND_PREFIX}help | YouTube Music",
                )
            )

        @self.bot.event
        async def on_command_error(ctx, error):
            # Ignorar CheckFailure - é tratado pelo cog_command_error
            if isinstance(error, commands.CheckFailure):
                return
            elif isinstance(error, commands.CommandNotFound):
                await ctx.send(
                    "❌ Comando não encontrado. Use `!help` para ver os comandos disponíveis."
                )
            elif isinstance(error, commands.MissingRequiredArgument):
                await ctx.send(f"❌ Argumento faltando: `{error.param.name}`")
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ Você não tem permissão para usar este comando.")
            else:
                self.logger.error(f"Erro no comando: {error}", exc_info=True)
                await ctx.send(f"❌ Ocorreu um erro: {str(error)}")

    async def load_cogs(self):
        """Carrega todos os cogs (comandos) do bot"""
        from handlers.music_commands import MusicCommands

        try:
            # Listar cogs atuais
            current_cogs = list(self.bot.cogs.keys())
            self.logger.info(f"Cogs atuais: {current_cogs}")

            # Verificar se o cog já está carregado
            if "MusicCommands" in current_cogs:
                self.logger.warning("⚠️ MusicCommands já está carregado! Removendo...")
                await self.bot.remove_cog("MusicCommands")

            # Adicionar novo cog
            await self.bot.add_cog(MusicCommands(self.bot))
            self.logger.info("✅ Cogs carregados com sucesso")

            # Verificar quantos comandos foram registrados
            command_count = len(self.bot.commands)
            self.logger.info(f"📝 Total de comandos registrados: {command_count}")

        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar cogs: {e}", exc_info=True)

    async def start_async(self, token: str):
        """
        Inicia o bot de forma assíncrona (permite melhor controle de encerramento)

        Args:
            token: Token do Discord
        """
        self.logger.info("Conectando ao Discord...")
        try:
            await self.bot.start(token)
        except KeyboardInterrupt:
            self.logger.info("🛑 Interrupção detectada")
            await self.shutdown()
        except Exception as e:
            self.logger.error(f"Erro ao iniciar bot: {e}", exc_info=True)
            raise
        finally:
            if not self.bot.is_closed():
                await self.bot.close()

    def run(self):
        """
        Inicia o bot (método síncrono para compatibilidade)
        Use start_async() para melhor controle de encerramento
        """
        is_valid, errors = config.validate()
        if not is_valid:
            self.logger.error("Configuração inválida:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return

        self.logger.info("Iniciando bot...")
        try:
            self.bot.run(config.DISCORD_TOKEN)
        except KeyboardInterrupt:
            self.logger.info("🛑 Interrupção detectada no bot.run()")
        finally:
            self.logger.info("Bot.run() finalizado")

    async def shutdown(self):
        """Encerra o bot graciosamente"""
        self.logger.info("Iniciando encerramento gracioso...")

        try:
            # Desconectar de todos os canais de voz
            if hasattr(self.bot, "voice_clients") and self.bot.voice_clients:
                self.logger.info(
                    f"Desconectando de {len(self.bot.voice_clients)} canais de voz..."
                )
                for voice_client in list(self.bot.voice_clients):
                    try:
                        await asyncio.wait_for(
                            voice_client.disconnect(force=True), timeout=2.0
                        )
                    except asyncio.TimeoutError:
                        self.logger.warning(
                            f"Timeout ao desconectar de {voice_client.channel}"
                        )
                    except Exception as e:
                        self.logger.warning(f"Erro ao desconectar: {e}")

            # Limpar sessões HTTP
            try:
                if hasattr(self.bot, "http") and self.bot.http:
                    await self.bot.http.close()
            except Exception as e:
                self.logger.warning(f"Erro ao fechar HTTP: {e}")

            # Fechar conexão do bot
            if not self.bot.is_closed():
                self.logger.info("Fechando conexão do bot...")
                try:
                    await asyncio.wait_for(self.bot.close(), timeout=3.0)
                except asyncio.TimeoutError:
                    self.logger.warning("Timeout ao fechar bot, forçando...")
                except Exception as e:
                    self.logger.warning(f"Erro ao fechar bot: {e}")

            self.logger.info("✅ Bot encerrado com sucesso")

        except Exception as e:
            self.logger.error(f"Erro durante encerramento: {e}", exc_info=True)
        finally:
            # Garantir que todas as tarefas pending sejam canceladas
            try:
                tasks = [t for t in asyncio.all_tasks() if not t.done()]
                if tasks:
                    self.logger.info(f"Cancelando {len(tasks)} tarefas pendentes...")
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
            except Exception as e:
                self.logger.warning(f"Erro ao cancelar tarefas: {e}")

    @classmethod
    def get_instance(cls) -> "MusicBot":
        """Retorna a instância única do bot"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
