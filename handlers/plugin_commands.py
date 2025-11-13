"""
Comandos de gerenciamento de plugins
Permite carregar/descarregar/listar plugins via Discord
"""

import discord
from discord import app_commands
from discord.ext import commands
from plugins.plugin_manager import PluginManager
from typing import Optional


class PluginCommands(commands.Cog):
    """Comandos administrativos para gerenciar plugins"""

    def __init__(self, bot: commands.Bot, plugin_manager: PluginManager):
        self.bot = bot
        self.plugin_manager = plugin_manager

    @commands.command(name="plugins", aliases=["plugin_list"])
    @commands.has_permissions(administrator=True)
    async def list_plugins_prefix(self, ctx: commands.Context):
        """Lista todos os plugins e seus status (comando com prefixo)"""
        plugins = self.plugin_manager.get_all_plugins()

        if not plugins:
            await ctx.send("❌ Nenhum plugin carregado.")
            return

        embed = discord.Embed(
            title="📦 Plugins Carregados",
            description=f"Total: {len(plugins)} plugins",
            color=discord.Color.blue(),
        )

        for plugin in plugins:
            status = "🟢 Habilitado" if plugin.enabled else "🔴 Desabilitado"
            embed.add_field(
                name=f"{plugin.name} v{plugin.version}",
                value=f"{status}\n*{plugin.description}*\nAutor: {plugin.author}",
                inline=False,
            )

        await ctx.send(embed=embed)

    @app_commands.command(
        name="plugins", description="Lista todos os plugins carregados"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def list_plugins(self, interaction: discord.Interaction):
        """Lista todos os plugins e seus status"""
        plugins = self.plugin_manager.get_all_plugins()

        if not plugins:
            await interaction.response.send_message(
                "❌ Nenhum plugin carregado.", ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📦 Plugins Carregados",
            description=f"Total: {len(plugins)} plugins",
            color=discord.Color.blue(),
        )

        for plugin in plugins:
            status = "🟢 Habilitado" if plugin.enabled else "🔴 Desabilitado"
            embed.add_field(
                name=f"{plugin.name} v{plugin.version}",
                value=f"{status}\n*{plugin.description}*\nAutor: {plugin.author}",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.command(name="plugin_reload")
    @commands.has_permissions(administrator=True)
    async def reload_plugin_prefix(self, ctx: commands.Context, plugin_name: str):
        """Recarrega um plugin específico (comando com prefixo)"""
        msg = await ctx.send(f"🔄 Recarregando plugin '{plugin_name}'...")

        success = await self.plugin_manager.reload_plugin(plugin_name)

        if success:
            await msg.edit(content=f"✅ Plugin '{plugin_name}' recarregado com sucesso!")
        else:
            await msg.edit(content=f"❌ Falha ao recarregar plugin '{plugin_name}'")

    @app_commands.command(
        name="plugin_reload", description="Recarrega um plugin específico"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def reload_plugin(self, interaction: discord.Interaction, plugin_name: str):
        """Recarrega um plugin"""
        await interaction.response.defer(ephemeral=True)

        success = await self.plugin_manager.reload_plugin(plugin_name)

        if success:
            await interaction.followup.send(
                f"✅ Plugin '{plugin_name}' recarregado com sucesso!", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Falha ao recarregar plugin '{plugin_name}'", ephemeral=True
            )

    @commands.command(name="plugin_load")
    @commands.has_permissions(administrator=True)
    async def load_plugin_prefix(self, ctx: commands.Context, plugin_name: str):
        """Carrega um plugin específico (comando com prefixo)"""
        msg = await ctx.send(f"📥 Carregando plugin '{plugin_name}'...")

        success = await self.plugin_manager.load_plugin(plugin_name)

        if success:
            await self.bot.tree.sync()
            await msg.edit(content=f"✅ Plugin '{plugin_name}' carregado com sucesso!")
        else:
            await msg.edit(content=f"❌ Falha ao carregar plugin '{plugin_name}'")

    @app_commands.command(
        name="plugin_load", description="Carrega um plugin específico"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def load_plugin(self, interaction: discord.Interaction, plugin_name: str):
        """Carrega um plugin"""
        await interaction.response.defer(ephemeral=True)

        success = await self.plugin_manager.load_plugin(plugin_name)

        if success:
            # Sincronizar comandos
            await self.bot.tree.sync()
            await interaction.followup.send(
                f"✅ Plugin '{plugin_name}' carregado com sucesso!", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Falha ao carregar plugin '{plugin_name}'", ephemeral=True
            )

    @commands.command(name="plugin_unload")
    @commands.has_permissions(administrator=True)
    async def unload_plugin_prefix(self, ctx: commands.Context, plugin_name: str):
        """Descarrega um plugin específico (comando com prefixo)"""
        msg = await ctx.send(f"📤 Descarregando plugin '{plugin_name}'...")

        success = await self.plugin_manager.unload_plugin(plugin_name)

        if success:
            await self.bot.tree.sync()
            await msg.edit(content=f"✅ Plugin '{plugin_name}' descarregado com sucesso!")
        else:
            await msg.edit(content=f"❌ Falha ao descarregar plugin '{plugin_name}'")

    @app_commands.command(
        name="plugin_unload", description="Descarrega um plugin específico"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def unload_plugin(self, interaction: discord.Interaction, plugin_name: str):
        """Descarrega um plugin"""
        await interaction.response.defer(ephemeral=True)

        success = await self.plugin_manager.unload_plugin(plugin_name)

        if success:
            # Sincronizar comandos
            await self.bot.tree.sync()
            await interaction.followup.send(
                f"✅ Plugin '{plugin_name}' descarregado com sucesso!", ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"❌ Falha ao descarregar plugin '{plugin_name}'", ephemeral=True
            )


async def setup(bot: commands.Bot, plugin_manager: PluginManager):
    """Adiciona os comandos de plugin ao bot"""
    await bot.add_cog(PluginCommands(bot, plugin_manager))
