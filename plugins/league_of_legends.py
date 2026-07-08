"""
Plugin League of Legends
Traz informações sobre LoL para o servidor Discord
"""

import discord
from discord.ext import commands
from discord import app_commands
from plugins.plugin_base import PluginBase
import aiohttp
from typing import Optional, List, Dict
import logging
import os


class LeagueOfLegendsPlugin(PluginBase):
    """
    Plugin para informações de League of Legends

    Features:
    - Informações de invocador
    - Status do servidor
    - Rotação de campeões gratuitos
    - Build de campeões
    - Patch notes
    """

    @property
    def name(self) -> str:
        return "League of Legends"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Informações de League of Legends para seu servidor Discord"

    @property
    def author(self) -> str:
        return "Matheus Alves"

    async def on_load(self) -> bool:
        """Inicialização do plugin"""
        self.logger = logging.getLogger(f"plugin.{self.name}")

        # Configurações da Riot API
        # TODO: Adicionar sua RIOT_API_KEY no .env
        self.riot_api_key = os.getenv("RIOT_API_KEY", "")

        if not self.riot_api_key:
            self.logger.warning(
                "⚠️ RIOT_API_KEY não configurada! Plugin funcionará em modo limitado."
            )

        # URLs base da API
        self.api_base = "https://br1.api.riotgames.com"
        self.ddragon_base = "https://ddragon.leagueoflegends.com"

        # Cache de dados
        self.champions_cache = {}
        self.version_cache = None

        # Session HTTP
        self.session = aiohttp.ClientSession()

        self.logger.info(f"✅ {self.name} v{self.version} carregado!")
        return True

    async def on_unload(self) -> bool:
        """Limpeza ao descarregar"""
        if hasattr(self, "session"):
            await self.session.close()

        self.logger.info(f"🔌 {self.name} descarregado")
        return True

    # ==================== MÉTODOS AUXILIARES ====================

    async def get_latest_version(self) -> str:
        """Obtém a versão mais recente do jogo"""
        if self.version_cache:
            return self.version_cache

        try:
            url = f"{self.ddragon_base}/api/versions.json"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    versions = await resp.json()
                    self.version_cache = versions[0]
                    return self.version_cache
        except Exception as e:
            self.logger.error(f"Erro ao obter versão: {e}")

        return "14.22.1"  # Fallback

    async def get_champion_data(self, champion_name: str) -> Optional[Dict]:
        """Obtém dados de um campeão"""
        try:
            version = await self.get_latest_version()
            url = f"{self.ddragon_base}/cdn/{version}/data/pt_BR/champion/{champion_name}.json"

            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data["data"][champion_name]
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do campeão {champion_name}: {e}")

        return None

    async def get_summoner_by_name(
        self, summoner_name: str, region: str = "br1"
    ) -> Optional[Dict]:
        """Obtém informações de um invocador pelo nome"""
        if not self.riot_api_key:
            return None

        try:
            # Riot API v4 - Summoner-V4
            url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
            headers = {"X-Riot-Token": self.riot_api_key}

            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return await resp.json()
                elif resp.status == 404:
                    return None
                else:
                    self.logger.error(f"API Error: {resp.status}")
        except Exception as e:
            self.logger.error(f"Erro ao buscar invocador {summoner_name}: {e}")

        return None

    async def get_free_rotation(self) -> Optional[List[int]]:
        """Obtém rotação de campeões gratuitos"""
        if not self.riot_api_key:
            return None

        try:
            url = f"{self.api_base}/lol/platform/v3/champion-rotations"
            headers = {"X-Riot-Token": self.riot_api_key}

            async with self.session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("freeChampionIds", [])
        except Exception as e:
            self.logger.error(f"Erro ao obter rotação gratuita: {e}")

        return None

    # ==================== COMANDOS ====================

    def get_commands(self) -> list:
        """Retorna lista de comandos do plugin"""

        # Comando 1: Informações do Plugin
        @commands.command(
            name="lol",
            aliases=["league"],
            help="Mostra informações do plugin League of Legends",
        )
        async def lol_info(ctx: commands.Context):
            """Informações sobre o plugin"""
            embed = discord.Embed(
                title="🎮 League of Legends Bot",
                description="Plugin de informações sobre League of Legends",
                color=discord.Color.gold(),
            )

            embed.add_field(name="📦 Versão", value=self.version, inline=True)

            embed.add_field(name="👤 Autor", value=self.author, inline=True)

            embed.add_field(
                name="🔑 API Status",
                value="✅ Configurada" if self.riot_api_key else "❌ Não configurada",
                inline=True,
            )

            # Comandos disponíveis
            commands_list = [
                "`!lol` - Informações do plugin",
                "`!summoner <nome>` - Busca invocador",
                "`!champion <nome>` - Info de campeão",
                "`!rotation` - Campeões gratuitos da semana",
                "`!patch` - Notas do patch atual",
            ]

            embed.add_field(
                name="📋 Comandos", value="\n".join(commands_list), inline=False
            )

            embed.set_thumbnail(
                url="https://static.wikia.nocookie.net/leagueoflegends/images/1/12/League_of_Legends_icon.png"
            )

            embed.set_footer(text="Dados fornecidos pela Riot Games API")

            await ctx.send(embed=embed)

        # Comando 2: Buscar Invocador
        @commands.command(
            name="summoner",
            aliases=["invocador", "player"],
            help="Busca informações de um invocador",
        )
        async def summoner_search(ctx: commands.Context, *, summoner_name: str):
            """Busca informações de um invocador"""

            if not self.riot_api_key:
                await ctx.send(
                    "❌ **API Key não configurada!**\n"
                    "Configure a `RIOT_API_KEY` no arquivo `.env`"
                )
                return

            await ctx.send(f"🔍 Buscando invocador **{summoner_name}**...")

            summoner = await self.get_summoner_by_name(summoner_name)

            if not summoner:
                await ctx.send(f"❌ Invocador **{summoner_name}** não encontrado!")
                return

            embed = discord.Embed(
                title=f"👤 {summoner['name']}", color=discord.Color.blue()
            )

            version = await self.get_latest_version()
            icon_url = f"{self.ddragon_base}/cdn/{version}/img/profileicon/{summoner['profileIconId']}.png"

            embed.set_thumbnail(url=icon_url)

            embed.add_field(
                name="📊 Nível", value=f"`{summoner['summonerLevel']}`", inline=True
            )

            embed.add_field(
                name="🆔 Summoner ID", value=f"`{summoner['id'][:8]}...`", inline=True
            )

            embed.set_footer(text="Dados da Riot Games API")

            await ctx.send(embed=embed)

        # Comando 3: Informações de Campeão
        @commands.command(
            name="champion",
            aliases=["champ", "campeao"],
            help="Mostra informações de um campeão",
        )
        async def champion_info(ctx: commands.Context, *, champion_name: str):
            """Informações sobre um campeão"""

            # Normalizar nome (primeira letra maiúscula)
            champion_name = champion_name.title().replace(" ", "")

            await ctx.send(f"🔍 Buscando campeão **{champion_name}**...")

            champion = await self.get_champion_data(champion_name)

            if not champion:
                await ctx.send(f"❌ Campeão **{champion_name}** não encontrado!")
                return

            version = await self.get_latest_version()

            embed = discord.Embed(
                title=f"{champion['name']} - {champion['title']}",
                description=champion["blurb"],
                color=discord.Color.red(),
            )

            # Imagem do campeão
            splash_url = (
                f"{self.ddragon_base}/cdn/img/champion/splash/{champion['id']}_0.jpg"
            )
            embed.set_image(url=splash_url)

            # Tags (Função)
            tags = ", ".join(champion["tags"])
            embed.add_field(name="🎭 Função", value=tags, inline=True)

            # Dificuldade
            difficulty = "⭐" * champion["info"]["difficulty"]
            embed.add_field(
                name="📊 Dificuldade", value=difficulty or "N/A", inline=True
            )

            # Stats
            stats = champion["stats"]
            embed.add_field(
                name="💪 Atributos Base",
                value=f"❤️ HP: {stats['hp']}\n"
                f"⚔️ AD: {stats['attackdamage']}\n"
                f"🛡️ Armor: {stats['armor']}\n"
                f"✨ MR: {stats['spellblock']}",
                inline=True,
            )

            embed.set_footer(text=f"Patch {version} • Riot Games")

            await ctx.send(embed=embed)

        # Comando 4: Rotação Gratuita
        @commands.command(
            name="rotation",
            aliases=["free", "gratuitos"],
            help="Mostra os campeões gratuitos da semana",
        )
        async def free_rotation(ctx: commands.Context):
            """Campeões gratuitos da semana"""

            if not self.riot_api_key:
                await ctx.send(
                    "❌ **API Key não configurada!**\n"
                    "Configure a `RIOT_API_KEY` no arquivo `.env`"
                )
                return

            await ctx.send("🔍 Buscando rotação gratuita...")

            rotation_ids = await self.get_free_rotation()

            if not rotation_ids:
                await ctx.send("❌ Erro ao obter rotação gratuita!")
                return

            embed = discord.Embed(
                title="🎁 Campeões Gratuitos da Semana",
                description=f"**{len(rotation_ids)} campeões** disponíveis gratuitamente!",
                color=discord.Color.green(),
            )

            # TODO: Converter IDs para nomes de campeões
            # Por enquanto, só mostra a quantidade

            embed.add_field(
                name="📊 Total", value=f"`{len(rotation_ids)}` campeões", inline=True
            )

            embed.set_footer(text="Rotação atualizada semanalmente")

            await ctx.send(embed=embed)

        # Comando 5: Patch Notes
        @commands.command(
            name="patch",
            aliases=["patchnotes", "versao"],
            help="Mostra informações do patch atual",
        )
        async def patch_info(ctx: commands.Context):
            """Informações do patch atual"""

            version = await self.get_latest_version()

            embed = discord.Embed(
                title=f"📰 Patch {version}",
                description="Patch atual de League of Legends",
                color=discord.Color.purple(),
            )

            embed.add_field(name="🔢 Versão", value=f"`{version}`", inline=True)

            # Link para patch notes
            patch_url = f"https://www.leagueoflegends.com/pt-br/news/game-updates/patch-{version.replace('.', '-')}-notes/"

            embed.add_field(
                name="🔗 Links", value=f"[📖 Patch Notes]({patch_url})", inline=False
            )

            embed.set_footer(text="League of Legends • Riot Games")

            await ctx.send(embed=embed)

        # Retornar todos os comandos
        return [lol_info, summoner_search, champion_info, free_rotation, patch_info]

    # ==================== HOOKS DE EVENTOS ====================

    async def on_message(self, message: discord.Message) -> None:
        """Reage a mensagens relacionadas a LoL"""

        if message.author.bot:
            return

        content_lower = message.content.lower()

        # Easter egg: reage a menções de LoL
        lol_keywords = ["league", "lol", "riot", "teemo", "yasuo"]

        for keyword in lol_keywords:
            if keyword in content_lower:
                await message.add_reaction("🎮")
                break
