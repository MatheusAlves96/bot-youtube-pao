"""
Music Commands - Command Pattern
Implementa comandos de música para o bot
"""
import discord
from discord.ext import commands
from typing import Optional

from services import MusicService, YouTubeService
from core.logger import LoggerFactory
from config import config


class MusicCommands(commands.Cog):
    """
    Cog com comandos de música
    Utiliza Command Pattern através do sistema de comandos do discord.py
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.music_service = MusicService.get_instance()
        self.youtube_service = YouTubeService.get_instance()
        self.logger = LoggerFactory.create_logger(__name__)

    async def cog_load(self):
        """Inicializa serviços ao carregar o cog"""
        try:
            await self.youtube_service.initialize()
            self.logger.info("YouTube Service inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar YouTube Service: {e}")

    def _check_voice_state(self, ctx: commands.Context) -> Optional[str]:
        """Verifica se o usuário está em um canal de voz"""
        if not ctx.author.voice:
            return "❌ Você precisa estar em um canal de voz!"

        if ctx.voice_client and ctx.voice_client.channel != ctx.author.voice.channel:
            return "❌ Você precisa estar no mesmo canal de voz que eu!"

        return None

    @commands.command(name='play', aliases=['p', 'tocar'])
    async def play(self, ctx: commands.Context, *, query: str):
        """
        Toca uma música do YouTube

        Uso: !play <URL ou termo de busca>
        """
        # Verificar estado de voz
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        # Conectar ao canal de voz se necessário
        if not ctx.voice_client:
            try:
                await ctx.author.voice.channel.connect()
                self.logger.info(f"Conectado ao canal: {ctx.author.voice.channel.name}")
            except Exception as e:
                await ctx.send(f"❌ Erro ao conectar ao canal de voz: {e}")
                return

        # Mensagem de processamento
        processing_msg = await ctx.send("🔍 Buscando música...")

        try:
            # Extrair informações da música
            song = await self.music_service.extract_info(query, ctx.author)

            # Obter player do servidor
            player = self.music_service.get_player(ctx.guild.id)

            # Se já está tocando, adicionar à fila
            if player.is_playing:
                player.add_song(song)

                embed = discord.Embed(
                    title="➕ Adicionado à Fila",
                    description=f"**{song.title}**",
                    color=discord.Color.green()
                )
                embed.add_field(name="Canal", value=song.uploader, inline=True)
                embed.add_field(name="Posição", value=len(player.queue), inline=True)
                embed.set_thumbnail(url=song.thumbnail)

                await processing_msg.edit(content=None, embed=embed)
            else:
                # Tocar imediatamente
                await self.music_service.play_song(player, ctx.voice_client, song)
                await processing_msg.edit(content=None, embed=song.to_embed())

        except Exception as e:
            self.logger.error(f"Erro ao tocar música: {e}", exc_info=True)
            await processing_msg.edit(content=f"❌ Erro ao processar música: {str(e)}")

    @commands.command(name='pause', aliases=['pausar'])
    async def pause(self, ctx: commands.Context):
        """Pausa ou retoma a reprodução"""
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        player = self.music_service.get_player(ctx.guild.id)
        is_paused = player.toggle_pause()

        if is_paused:
            await ctx.send("⏸️ Música pausada")
        else:
            await ctx.send("▶️ Música retomada")

    @commands.command(name='skip', aliases=['pular', 's'])
    async def skip(self, ctx: commands.Context):
        """Pula a música atual"""
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        player = self.music_service.get_player(ctx.guild.id)

        if not player.current_song:
            await ctx.send("❌ Nenhuma música está tocando!")
            return

        skipped = player.skip()
        await ctx.send(f"⏭️ Pulada: **{skipped.title}**")

    @commands.command(name='stop', aliases=['parar'])
    async def stop(self, ctx: commands.Context):
        """Para a reprodução e limpa a fila"""
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        player = self.music_service.get_player(ctx.guild.id)
        player.clear_queue()

        if ctx.voice_client:
            ctx.voice_client.stop()

        await ctx.send("⏹️ Reprodução parada e fila limpa")

    @commands.command(name='queue', aliases=['q', 'fila'])
    async def queue(self, ctx: commands.Context):
        """Mostra a fila de músicas"""
        player = self.music_service.get_player(ctx.guild.id)

        if not player.current_song and not player.queue:
            await ctx.send("📭 A fila está vazia!")
            return

        embed = discord.Embed(
            title="🎵 Fila de Músicas",
            color=discord.Color.blue()
        )

        # Música atual
        if player.current_song:
            current = player.current_song
            embed.add_field(
                name="▶️ Tocando Agora",
                value=f"**{current.title}**\nPor: {current.requester.mention}",
                inline=False
            )

        # Próximas músicas
        if player.queue:
            queue_list = player.get_queue()
            next_songs = "\n".join([
                f"`{i+1}.` **{song.title}** - {song.requester.mention}"
                for i, song in enumerate(queue_list[:10])
            ])

            embed.add_field(
                name=f"📋 Próximas ({len(queue_list)} músicas)",
                value=next_songs,
                inline=False
            )

            if len(queue_list) > 10:
                embed.set_footer(text=f"... e mais {len(queue_list) - 10} músicas")

        await ctx.send(embed=embed)

    @commands.command(name='nowplaying', aliases=['np', 'tocando'])
    async def now_playing(self, ctx: commands.Context):
        """Mostra a música que está tocando"""
        player = self.music_service.get_player(ctx.guild.id)

        if not player.current_song:
            await ctx.send("❌ Nenhuma música está tocando!")
            return

        await ctx.send(embed=player.current_song.to_embed())

    @commands.command(name='volume', aliases=['vol', 'v'])
    async def volume(self, ctx: commands.Context, volume: int):
        """
        Ajusta o volume (0-100)

        Uso: !volume <0-100>
        """
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        if not 0 <= volume <= 100:
            await ctx.send("❌ Volume deve estar entre 0 e 100!")
            return

        player = self.music_service.get_player(ctx.guild.id)
        player.set_volume(volume / 100.0)

        await ctx.send(f"🔊 Volume ajustado para {volume}%")

    @commands.command(name='clear', aliases=['limpar'])
    async def clear(self, ctx: commands.Context):
        """Limpa a fila de músicas"""
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        player = self.music_service.get_player(ctx.guild.id)
        queue_size = len(player.queue)
        player.clear_queue()

        await ctx.send(f"🗑️ Fila limpa! ({queue_size} músicas removidas)")

    @commands.command(name='shuffle', aliases=['embaralhar'])
    async def shuffle(self, ctx: commands.Context):
        """Embaralha a fila"""
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        player = self.music_service.get_player(ctx.guild.id)

        if not player.queue:
            await ctx.send("❌ A fila está vazia!")
            return

        player.shuffle()
        await ctx.send("🔀 Fila embaralhada!")

    @commands.command(name='disconnect', aliases=['dc', 'leave', 'sair'])
    async def disconnect(self, ctx: commands.Context):
        """Desconecta o bot do canal de voz"""
        if not ctx.voice_client:
            await ctx.send("❌ Não estou conectado a nenhum canal de voz!")
            return

        player = self.music_service.get_player(ctx.guild.id)
        player.clear_queue()

        await ctx.voice_client.disconnect()
        await ctx.send("👋 Desconectado do canal de voz")

    @commands.command(name='search', aliases=['buscar'])
    async def search(self, ctx: commands.Context, *, query: str):
        """
        Busca músicas no YouTube

        Uso: !search <termo>
        """
        processing_msg = await ctx.send("🔍 Buscando no YouTube...")

        try:
            results = await self.youtube_service.search_video(query, max_results=5)

            if not results:
                await processing_msg.edit(content="❌ Nenhum resultado encontrado!")
                return

            embed = discord.Embed(
                title=f"🔍 Resultados para: {query}",
                color=discord.Color.blue()
            )

            for i, video in enumerate(results, 1):
                embed.add_field(
                    name=f"{i}. {video['title']}",
                    value=f"Canal: {video['channel']}\n[Assistir]({video['url']})",
                    inline=False
                )

            embed.set_footer(text=f"Use {config.COMMAND_PREFIX}play <URL> para tocar")

            await processing_msg.edit(content=None, embed=embed)

        except Exception as e:
            self.logger.error(f"Erro na busca: {e}", exc_info=True)
            await processing_msg.edit(content=f"❌ Erro na busca: {str(e)}")

    @commands.command(name='help', aliases=['ajuda', 'h'])
    async def help_command(self, ctx: commands.Context):
        """Mostra todos os comandos disponíveis"""
        embed = discord.Embed(
            title="🎵 Bot de Música - Comandos",
            description="Lista de todos os comandos disponíveis",
            color=discord.Color.blue()
        )

        commands_list = {
            "🎵 Reprodução": [
                f"`{config.COMMAND_PREFIX}play <URL/busca>` - Toca uma música",
                f"`{config.COMMAND_PREFIX}pause` - Pausa/retoma a música",
                f"`{config.COMMAND_PREFIX}skip` - Pula a música atual",
                f"`{config.COMMAND_PREFIX}stop` - Para e limpa a fila",
            ],
            "📋 Fila": [
                f"`{config.COMMAND_PREFIX}queue` - Mostra a fila",
                f"`{config.COMMAND_PREFIX}clear` - Limpa a fila",
                f"`{config.COMMAND_PREFIX}shuffle` - Embaralha a fila",
            ],
            "ℹ️ Informações": [
                f"`{config.COMMAND_PREFIX}nowplaying` - Música atual",
                f"`{config.COMMAND_PREFIX}search <termo>` - Busca no YouTube",
            ],
            "⚙️ Configurações": [
                f"`{config.COMMAND_PREFIX}volume <0-100>` - Ajusta o volume",
                f"`{config.COMMAND_PREFIX}disconnect` - Desconecta o bot",
            ]
        }

        for category, cmds in commands_list.items():
            embed.add_field(
                name=category,
                value="\n".join(cmds),
                inline=False
            )

        embed.set_footer(text="🎵 YouTube Music Bot | Desenvolvido com ❤️")

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    """Setup function para carregar o cog"""
    await bot.add_cog(MusicCommands(bot))
