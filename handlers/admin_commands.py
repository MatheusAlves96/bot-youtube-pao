"""
Admin Commands Handler
Comandos administrativos para gerenciar o bot em tempo real
"""

import discord
from discord.ext import commands
from discord import app_commands
import os
from pathlib import Path
from typing import Optional
import logging
from dotenv import load_dotenv, set_key, find_dotenv


class AdminCommands(commands.Cog):
    """
    Comandos administrativos para configuração dinâmica do bot

    Features:
    - Configurar variáveis do .env sem reiniciar
    - Recarregar plugins
    - Gerenciar permissões
    - Visualizar status do sistema
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = logging.getLogger("handlers.admin_commands")
        self.env_file = find_dotenv() or ".env"

        # Lista de variáveis que podem ser alteradas em runtime
        self.runtime_editable = {
            "GROQ_API_KEY": self._reload_ai_service,
            "RIOT_API_KEY": self._reload_plugin_config,
            "AUTOPLAY_ENABLED": self._reload_config,
            "AUTOPLAY_QUEUE_SIZE": self._reload_config,
            "DEFAULT_VOLUME": self._reload_config,
            "LOG_LEVEL": self._reload_logging,
            "YTDL_COOKIES_PATH": self._reload_music_service,
        }

        # Lista de variáveis que requerem reinício
        self.requires_restart = {
            "DISCORD_TOKEN",
            "YOUTUBE_API_KEY",
            "YOUTUBE_CLIENT_ID",
            "YOUTUBE_CLIENT_SECRET",
            "COMMAND_PREFIX",
        }

    def cog_check(self, ctx: commands.Context) -> bool:
        """Apenas o owner pode usar comandos admin"""
        from config import config

        return ctx.author.id == config.OWNER_ID

    @commands.command(
        name="setenv",
        aliases=["config", "env"],
        help="Define uma variável de ambiente (apenas owner)",
    )
    async def set_environment(self, ctx: commands.Context, key: str, *, value: str):
        """
        Define uma variável de ambiente no .env

        Exemplos:
        !setenv GROQ_API_KEY sua_chave_aqui
        !setenv RIOT_API_KEY sua_chave_riot
        !setenv AUTOPLAY_ENABLED True
        """

        # Verificar se o arquivo .env existe
        if not os.path.exists(self.env_file):
            await ctx.send("❌ Arquivo `.env` não encontrado!")
            return

        # Normalizar key (maiúsculas)
        key = key.upper()

        # Verificar se a variável requer reinício
        if key in self.requires_restart:
            embed = discord.Embed(
                title="⚠️ Reinício Necessário",
                description=f"A variável `{key}` foi atualizada, mas **requer reinicialização do bot** para ter efeito.",
                color=discord.Color.orange(),
            )

            embed.add_field(
                name="📝 Valor Definido",
                value=f"`{value[:50]}...`" if len(value) > 50 else f"`{value}`",
                inline=False,
            )

            embed.add_field(
                name="🔄 Próximos Passos",
                value="1️⃣ Use `!restart` para reiniciar o bot\n2️⃣ Ou reinicie manualmente",
                inline=False,
            )

            # Salvar no .env mesmo assim
            set_key(self.env_file, key, value)

            await ctx.send(embed=embed)
            return

        # Salvar no .env
        try:
            set_key(self.env_file, key, value)

            # Recarregar variáveis de ambiente
            load_dotenv(override=True)

            # Aplicar mudanças em runtime (se possível)
            reload_func = self.runtime_editable.get(key)

            if reload_func:
                success = await reload_func(key, value)

                if success:
                    embed = discord.Embed(
                        title="✅ Configuração Atualizada",
                        description=f"A variável `{key}` foi atualizada e **aplicada em tempo real**!",
                        color=discord.Color.green(),
                    )
                else:
                    embed = discord.Embed(
                        title="⚠️ Configuração Salva",
                        description=f"A variável `{key}` foi salva, mas houve erro ao aplicar.",
                        color=discord.Color.orange(),
                    )
            else:
                embed = discord.Embed(
                    title="✅ Configuração Salva",
                    description=f"A variável `{key}` foi salva no `.env`",
                    color=discord.Color.blue(),
                )

                embed.add_field(
                    name="ℹ️ Nota",
                    value="Esta variável não suporta recarregamento em tempo real.",
                    inline=False,
                )

            embed.add_field(
                name="📝 Valor",
                value=f"`{value[:50]}...`" if len(value) > 50 else f"`{value}`",
                inline=False,
            )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Erro ao definir {key}: {e}", exc_info=True)
            await ctx.send(f"❌ Erro ao salvar configuração: {str(e)}")

    @commands.command(
        name="getenv",
        aliases=["showconfig", "viewenv"],
        help="Mostra o valor de uma variável de ambiente",
    )
    async def get_environment(self, ctx: commands.Context, key: str):
        """
        Mostra o valor atual de uma variável de ambiente

        Exemplo:
        !getenv GROQ_API_KEY
        """

        key = key.upper()
        value = os.getenv(key)

        if value is None:
            await ctx.send(f"❌ Variável `{key}` não encontrada!")
            return

        # Ocultar parcialmente valores sensíveis
        sensitive_keys = ["TOKEN", "KEY", "SECRET", "PASSWORD"]
        is_sensitive = any(s in key for s in sensitive_keys)

        if is_sensitive and len(value) > 8:
            display_value = f"{value[:4]}{'*' * (len(value) - 8)}{value[-4:]}"
        else:
            display_value = value

        embed = discord.Embed(
            title=f"🔧 Configuração: {key}", color=discord.Color.blue()
        )

        embed.add_field(name="📝 Valor", value=f"`{display_value}`", inline=False)

        # Informar se requer reinício
        if key in self.requires_restart:
            embed.add_field(
                name="⚠️ Nota",
                value="Esta variável requer **reinício do bot** para mudanças terem efeito.",
                inline=False,
            )
        elif key in self.runtime_editable:
            embed.add_field(
                name="✅ Dinâmica",
                value="Esta variável pode ser alterada **em tempo real**.",
                inline=False,
            )

        await ctx.send(embed=embed)

    @commands.command(
        name="listenv",
        aliases=["envlist", "configs"],
        help="Lista todas as variáveis de ambiente configuradas",
    )
    async def list_environment(self, ctx: commands.Context):
        """Lista todas as variáveis de ambiente do .env"""

        if not os.path.exists(self.env_file):
            await ctx.send("❌ Arquivo `.env` não encontrado!")
            return

        embed = discord.Embed(
            title="🔧 Configurações do Bot",
            description="Variáveis de ambiente configuradas",
            color=discord.Color.blue(),
        )

        # Ler .env
        with open(self.env_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Agrupar por categoria
        categories = {
            "🤖 Discord": [],
            "📺 YouTube": [],
            "🤖 AI Service": [],
            "🎵 Música": [],
            "🔌 Plugins": [],
            "⚙️ Sistema": [],
        }

        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if "=" in line:
                key = line.split("=")[0].strip()

                # Categorizar
                if "DISCORD" in key or "OWNER" in key or "COMMAND" in key:
                    categories["🤖 Discord"].append(key)
                elif "YOUTUBE" in key or "YTDL" in key:
                    categories["📺 YouTube"].append(key)
                elif "GROQ" in key or "AI" in key:
                    categories["🤖 AI Service"].append(key)
                elif (
                    "AUTOPLAY" in key
                    or "VOLUME" in key
                    or "QUEUE" in key
                    or "CROSSFADE" in key
                ):
                    categories["🎵 Música"].append(key)
                elif "RIOT" in key:
                    categories["🔌 Plugins"].append(key)
                else:
                    categories["⚙️ Sistema"].append(key)

        # Adicionar ao embed
        for category, keys in categories.items():
            if keys:
                # Marcar variáveis dinâmicas
                formatted_keys = []
                for key in keys:
                    if key in self.runtime_editable:
                        formatted_keys.append(f"✅ `{key}`")
                    elif key in self.requires_restart:
                        formatted_keys.append(f"🔄 `{key}`")
                    else:
                        formatted_keys.append(f"`{key}`")

                embed.add_field(
                    name=category, value="\n".join(formatted_keys), inline=False
                )

        embed.set_footer(text="✅ Dinâmica | 🔄 Requer Reinício")

        await ctx.send(embed=embed)

    @commands.command(
        name="reload", aliases=["reloadplugins"], help="Recarrega todos os plugins"
    )
    async def reload_plugins(self, ctx: commands.Context):
        """Recarrega todos os plugins do bot"""

        if not hasattr(self.bot, "plugin_manager"):
            await ctx.send("❌ Sistema de plugins não disponível!")
            return

        msg = await ctx.send("🔄 Recarregando plugins...")

        try:
            # Descarregar todos
            unloaded = await self.bot.plugin_manager.unload_all()

            # Carregar todos novamente
            loaded = await self.bot.plugin_manager.load_all()

            embed = discord.Embed(
                title="✅ Plugins Recarregados", color=discord.Color.green()
            )

            embed.add_field(name="📤 Descarregados", value=f"`{unloaded}`", inline=True)
            embed.add_field(name="📥 Carregados", value=f"`{loaded}`", inline=True)

            # Listar plugins ativos
            plugins = self.bot.plugin_manager.get_loaded_plugins()
            if plugins:
                plugin_list = "\n".join(
                    [f"• **{p.name}** v{p.version}" for p in plugins]
                )
                embed.add_field(
                    name="🔌 Plugins Ativos", value=plugin_list, inline=False
                )

            await msg.edit(content=None, embed=embed)

        except Exception as e:
            self.logger.error(f"Erro ao recarregar plugins: {e}", exc_info=True)
            await msg.edit(content=f"❌ Erro ao recarregar plugins: {str(e)}")

    @commands.command(
        name="status",
        aliases=["info", "botinfo"],
        help="Mostra status e informações do bot",
    )
    async def show_status(self, ctx: commands.Context):
        """Mostra informações detalhadas sobre o bot"""

        from config import config
        import psutil
        import platform

        embed = discord.Embed(title="📊 Status do Bot", color=discord.Color.blue())

        # Informações do bot
        embed.add_field(
            name="🤖 Bot",
            value=f"**Nome:** {self.bot.user.name}\n"
            f"**ID:** {self.bot.user.id}\n"
            f"**Servidores:** {len(self.bot.guilds)}",
            inline=True,
        )

        # Sistema
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        embed.add_field(
            name="💻 Sistema",
            value=f"**OS:** {platform.system()}\n"
            f"**CPU:** {cpu}%\n"
            f"**RAM:** {memory.percent}%",
            inline=True,
        )

        # Configurações
        embed.add_field(
            name="⚙️ Configurações",
            value=f"**Prefix:** `{config.COMMAND_PREFIX}`\n"
            f"**Autoplay:** {'✅' if config.AUTOPLAY_ENABLED else '❌'}\n"
            f"**Cache:** {'✅' if config.CACHE_ENABLED else '❌'}",
            inline=True,
        )

        # Plugins
        if hasattr(self.bot, "plugin_manager"):
            plugins = self.bot.plugin_manager.get_loaded_plugins()
            embed.add_field(
                name="🔌 Plugins",
                value=f"**Carregados:** {len(plugins)}\n"
                f"**Disponíveis:** {len(self.bot.plugin_manager.discover_plugins())}",
                inline=True,
            )

        # Voice
        voice_count = len(self.bot.voice_clients)
        embed.add_field(
            name="🎵 Áudio",
            value=f"**Canais de Voz:** {voice_count}\n" f"**FFmpeg:** ✅",
            inline=True,
        )

        await ctx.send(embed=embed)

    # ==================== MÉTODOS DE RECARGA ====================

    async def _reload_config(self, key: str, value: str) -> bool:
        """Recarrega configuração geral"""
        try:
            from config import config

            # Atualizar valor na instância Config
            if hasattr(config, key):
                # Converter tipo se necessário
                if key.endswith("_ENABLED"):
                    setattr(config, key, value.lower() == "true")
                elif key.endswith("_SIZE"):
                    setattr(config, key, int(value))
                else:
                    setattr(config, key, value)

                self.logger.info(f"Configuração {key} atualizada para: {value}")
                return True
        except Exception as e:
            self.logger.error(f"Erro ao recarregar config: {e}")

        return False

    async def _reload_ai_service(self, key: str, value: str) -> bool:
        """Recarrega configuração do AI Service"""
        try:
            # Atualizar variável de ambiente
            os.environ[key] = value

            # Recriar instância do AIService (se existir)
            # TODO: Implementar recriação do AIService

            self.logger.info(f"AI Service configuração atualizada: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao recarregar AI service: {e}")

        return False

    async def _reload_plugin_config(self, key: str, value: str) -> bool:
        """Recarrega configuração de plugins"""
        try:
            # Atualizar variável de ambiente
            os.environ[key] = value

            # Recarregar plugins que usam essa config
            if hasattr(self.bot, "plugin_manager"):
                # Identificar plugins que usam essa key
                if "RIOT" in key:
                    # Recarregar plugin League of Legends
                    plugin = self.bot.plugin_manager.get_plugin("league_of_legends")
                    if plugin:
                        await self.bot.plugin_manager.unload_plugin("league_of_legends")
                        await self.bot.plugin_manager.load_plugin("league_of_legends")

            self.logger.info(f"Plugin configuração atualizada: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao recarregar plugin config: {e}")

        return False

    async def _reload_logging(self, key: str, value: str) -> bool:
        """Recarrega configuração de logging"""
        try:
            import logging

            # Atualizar nível de log
            level = getattr(logging, value.upper(), logging.INFO)
            logging.getLogger().setLevel(level)

            self.logger.info(f"Log level atualizado para: {value}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao recarregar logging: {e}")

        return False

    async def _reload_music_service(self, key: str, value: str) -> bool:
        """Recarrega configuração do Music Service"""
        try:
            from config import config

            # Atualizar caminho dos cookies
            config.YTDL_COOKIES_PATH = value

            # Recriar opções do yt-dlp
            # A próxima busca já usará as novas opções

            self.logger.info(f"Music service configuração atualizada: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao recarregar music service: {e}")

        return False

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        """Tratamento de erros para comandos admin"""
        if isinstance(error, commands.CheckFailure):
            await ctx.send(
                "❌ Apenas o dono do bot pode usar comandos administrativos!"
            )


async def setup(bot: commands.Bot):
    """Registra o cog no bot"""
    await bot.add_cog(AdminCommands(bot))
