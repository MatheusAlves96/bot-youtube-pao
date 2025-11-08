"""
Bot Client Core - Singleton Pattern
"""
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
    _instance: Optional['MusicBot'] = None

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
            command_prefix=config.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )

        self._setup_events()

    def _setup_events(self):
        """Configura eventos básicos do bot"""

        @self.bot.event
        async def on_ready():
            self.logger.info(f'{self.bot.user} está online!')
            self.logger.info(f'ID: {self.bot.user.id}')
            self.logger.info(f'Servidores: {len(self.bot.guilds)}')

            # Configurar status
            await self.bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.listening,
                    name=f"{config.COMMAND_PREFIX}help | YouTube Music"
                )
            )

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("❌ Comando não encontrado. Use `!help` para ver os comandos disponíveis.")
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
            await self.bot.add_cog(MusicCommands(self.bot))
            self.logger.info("Cogs carregados com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao carregar cogs: {e}", exc_info=True)

    def run(self):
        """Inicia o bot"""
        is_valid, errors = config.validate()
        if not is_valid:
            self.logger.error("Configuração inválida:")
            for error in errors:
                self.logger.error(f"  - {error}")
            return

        self.logger.info("Iniciando bot...")
        self.bot.run(config.DISCORD_TOKEN)

    @classmethod
    def get_instance(cls) -> 'MusicBot':
        """Retorna a instância única do bot"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
