"""
Plugin de Exemplo: Hello World
Demonstra como criar um plugin básico
"""

import discord
from discord.ext import commands
from plugins.plugin_base import PluginBase


class HelloWorldPlugin(PluginBase):
    """Plugin de exemplo que adiciona comando .hello"""

    @property
    def name(self) -> str:
        return "Hello World"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Plugin de exemplo que responde 'Hello World!'"

    @property
    def author(self) -> str:
        return "Bot Team"

    async def on_load(self) -> bool:
        """Inicialização do plugin"""
        print(f"🔌 {self.name} v{self.version} carregando...")
        return True

    async def on_unload(self) -> bool:
        """Limpeza ao descarregar"""
        print(f"🔌 {self.name} descarregado")
        return True

    def get_commands(self) -> list:
        """Retorna comandos do plugin"""

        @commands.command(
            name="hello",
            aliases=["oi", "ola"],
            help="Responde com Hello World e informações do plugin",
        )
        async def hello(ctx: commands.Context):
            embed = discord.Embed(
                title="👋 Hello World!",
                description=f"Olá! Eu sou um plugin de exemplo.",
                color=discord.Color.blue(),
            )
            embed.add_field(name="📦 Plugin", value=self.name, inline=True)
            embed.add_field(name="🔢 Versão", value=self.version, inline=True)
            embed.add_field(name="👤 Autor", value=self.author, inline=True)
            embed.add_field(name="📝 Descrição", value=self.description, inline=False)
            embed.set_footer(text="Sistema de Plugins v1.0")

            await ctx.send(embed=embed)

        return [hello]

    async def on_message(self, message: discord.Message) -> None:
        """Reage a mensagens que contenham 'hello'"""
        if message.author.bot:
            return

        if "hello" in message.content.lower():
            await message.add_reaction("👋")
