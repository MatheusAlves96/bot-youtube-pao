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

        # Inicializar plugin_manager como None (será criado em load_cogs)
        self.plugin_manager = None

        self._setup_events()

    def _setup_events(self):
        """Configura eventos básicos do bot"""

        @self.bot.event
        async def on_ready():
            self.logger.info(f"{self.bot.user} está online!")
            self.logger.info(f"ID: {self.bot.user.id}")
            self.logger.info(f"Servidores: {len(self.bot.guilds)}")

            # Sincronizar comandos slash (agora que application_id está disponível)
            if self.plugin_manager:
                try:
                    await self.bot.tree.sync()
                    self.logger.info("✅ Comandos slash sincronizados")
                except Exception as e:
                    self.logger.error(f"❌ Erro ao sincronizar comandos slash: {e}")

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
        from handlers.admin_commands import AdminCommands
        from plugins.plugin_manager import PluginManager
        from handlers.plugin_commands import setup as setup_plugin_commands

        try:
            # Listar cogs atuais
            current_cogs = list(self.bot.cogs.keys())
            self.logger.info(f"Cogs atuais: {current_cogs}")

            # Verificar se o cog já está carregado
            if "MusicCommands" in current_cogs:
                self.logger.warning("⚠️ MusicCommands já está carregado! Removendo...")
                await self.bot.remove_cog("MusicCommands")

            # Adicionar MusicCommands
            await self.bot.add_cog(MusicCommands(self.bot))
            self.logger.info("✅ MusicCommands carregado")

            # Adicionar AdminCommands
            if "AdminCommands" in list(self.bot.cogs.keys()):
                self.logger.warning("⚠️ AdminCommands já está carregado! Removendo...")
                await self.bot.remove_cog("AdminCommands")

            await self.bot.add_cog(AdminCommands(self.bot))
            self.logger.info("✅ AdminCommands carregado")

            # Verificar quantos comandos foram registrados
            command_count = len(self.bot.commands)
            self.logger.info(f"📝 Total de comandos registrados: {command_count}")

            # Inicializar sistema de plugins
            self.logger.info("🔌 Inicializando sistema de plugins...")
            self.plugin_manager = PluginManager(self.bot)
            # Armazenar também no bot para acesso direto
            self.bot.plugin_manager = self.plugin_manager

            # Carregar PluginCommands Cog
            if "PluginCommands" in list(self.bot.cogs.keys()):
                self.logger.warning("⚠️ PluginCommands já está carregado! Removendo...")
                await self.bot.remove_cog("PluginCommands")

            await setup_plugin_commands(self.bot, self.plugin_manager)
            self.logger.info("✅ PluginCommands carregado")

            # Carregar todos os plugins disponíveis
            loaded_count = await self.plugin_manager.load_all()
            self.logger.info(f"✅ {loaded_count} plugin(s) carregado(s)")

            # Nota: tree.sync() será chamado em on_ready quando application_id estiver disponível

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
        except (KeyboardInterrupt, asyncio.CancelledError):
            self.logger.debug("🛑 Interrupção detectada (esperado)")
            # Não fazer nada aqui - shutdown será chamado externamente
        except Exception as e:
            self.logger.error(f"Erro ao iniciar bot: {e}", exc_info=True)
            raise
        finally:
            # Não chamar close aqui - será feito no shutdown()
            pass

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
            # 0️⃣ Salvar quota antes de encerrar
            from utils.quota_tracker import quota_tracker

            quota_tracker.force_save()

            # 1️⃣ Desconectar voice clients
            if hasattr(self.bot, "voice_clients") and self.bot.voice_clients:
                self.logger.debug(
                    f"Desconectando de {len(self.bot.voice_clients)} canais de voz..."
                )
                for voice_client in list(self.bot.voice_clients):
                    try:
                        if voice_client.is_connected():
                            await asyncio.wait_for(
                                voice_client.disconnect(force=True), timeout=1.0
                            )
                    except Exception:
                        pass

            # 2️⃣ Fechar bot (isso fecha a sessão HTTP internamente)
            if not self.bot.is_closed():
                self.logger.debug("Fechando bot...")
                try:
                    await asyncio.wait_for(self.bot.close(), timeout=2.0)
                except (asyncio.TimeoutError, RuntimeError, asyncio.CancelledError):
                    pass

            # 3️⃣ Aguardar 250ms para conexões HTTP finalizarem
            await asyncio.sleep(0.25)

            self.logger.info("✅ Bot encerrado")

        except Exception as e:
            self.logger.debug(f"Erro durante encerramento: {e}")

    @classmethod
    def get_instance(cls) -> "MusicBot":
        """Retorna a instância única do bot"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
