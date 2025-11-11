"""
Music Commands - Command Pattern
Implementa comandos de música para o bot
"""

import asyncio
import discord
from discord.ext import commands
from typing import Optional

from services import MusicService, YouTubeService
from core.logger import LoggerFactory
from config import config
from utils.quota_tracker import quota_tracker


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
        self._channel_cache = {}  # Cache de canais de voz por guild_id

    async def cog_load(self):
        """Inicializa serviços ao carregar o cog"""
        try:
            await self.youtube_service.initialize()
            self.logger.info("YouTube Service inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar YouTube Service: {e}")

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        """
        Tratamento de erros para comandos deste cog
        """
        # Se for erro de check (canal errado), já foi tratado em _check_music_channel
        if isinstance(error, commands.CheckFailure):
            # Não fazer nada, mensagem já foi enviada
            return

        # Para outros erros, propagar
        raise error

    async def cog_check(self, ctx: commands.Context) -> bool:
        """
        Verifica condições antes de executar qualquer comando deste cog
        Chamado automaticamente para todos os comandos
        """
        # Não verificar o canal para o comando help
        if ctx.command.name == "help":
            return True

        # Verificar canal de música para todos os outros comandos
        return await self._check_music_channel(ctx)

    async def _check_music_channel(self, ctx: commands.Context) -> bool:
        """
        Verifica se o comando foi enviado no canal de música correto

        Returns:
            True se pode continuar, False se deve bloquear
        """
        # Se não há canal configurado, aceita em qualquer lugar
        if config.MUSIC_CHANNEL_ID is None:
            return True

        # Se está no canal correto, permite
        if ctx.channel.id == config.MUSIC_CHANNEL_ID:
            return True

        # Canal errado - apagar mensagem e redirecionar
        try:
            # Obter o canal correto ANTES de deletar a mensagem
            music_channel = self.bot.get_channel(config.MUSIC_CHANNEL_ID)

            self.logger.info(
                f"🔍 Debug - Canal configurado ID: {config.MUSIC_CHANNEL_ID}, "
                f"Canal encontrado: {music_channel.name if music_channel else 'None'}"
            )

            if music_channel:
                # Deletar a mensagem do canal errado PRIMEIRO (silenciosamente)
                try:
                    await ctx.message.delete()
                except discord.Forbidden:
                    # Se não tiver permissão, apenas ignora
                    self.logger.warning(
                        f"Sem permissão para deletar mensagem no canal #{ctx.channel.name}"
                    )

                # Enviar mensagem APENAS no canal de música
                await music_channel.send(
                    f"👋 {ctx.author.mention}, use os comandos de música aqui!"
                )

                self.logger.info(
                    f"Comando {ctx.command.name} bloqueado no canal #{ctx.channel.name}, "
                    f"redirecionado para #{music_channel.name}"
                )
            else:
                # Se não encontrar o canal, só logar (não avisar usuário)
                self.logger.error(
                    f"Canal de música ID {config.MUSIC_CHANNEL_ID} não encontrado!"
                )

        except Exception as e:
            self.logger.error(f"Erro ao verificar canal de música: {e}")

        return False

    def _get_cached_voice_channel(self, ctx: commands.Context):
        """
        Obtém canal de voz do usuário com cache

        Returns:
            Canal de voz ou None
        """
        guild_id = ctx.guild.id

        # Verificar cache primeiro
        if guild_id in self._channel_cache:
            channel = self._channel_cache[guild_id]
            # Validar se o canal ainda é válido
            if channel and channel.guild == ctx.guild:
                return channel

        # Se não está em cache ou inválido, buscar
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            self._channel_cache[guild_id] = channel
            return channel

        return None

    def _check_voice_state(self, ctx: commands.Context) -> Optional[str]:
        """Verifica se o usuário está em um canal de voz"""
        voice_channel = self._get_cached_voice_channel(ctx)
        if not voice_channel:
            return "❌ Você precisa estar em um canal de voz!"

        if ctx.voice_client and ctx.voice_client.channel != voice_channel:
            return "❌ Você precisa estar no mesmo canal de voz que eu!"

        return None

    def _ensure_text_channel(self, ctx: commands.Context):
        """Garante que o player tenha referência ao canal de texto"""
        player = self.music_service.get_player(ctx.guild.id)
        if player and not player.text_channel:
            player.text_channel = ctx.channel
        return player

    @commands.command(name="play", aliases=["p", "tocar"])
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
                voice_channel = self._get_cached_voice_channel(ctx)
                if not voice_channel:
                    await ctx.send("❌ Você precisa estar em um canal de voz!")
                    return
                
                await voice_channel.connect()
                self.logger.info(f"Conectado ao canal: {voice_channel.name}")
            except Exception as e:
                await ctx.send(f"❌ Erro ao conectar ao canal de voz: {e}")
                return

        # Mensagem de processamento
        processing_msg = await ctx.send("🔍 Buscando música...")

        try:
            # Obter player do servidor e garantir que tem canal de texto
            player = self._ensure_text_channel(ctx)

            # Verificar se é uma playlist
            is_playlist_url = "playlist" in query.lower() or "list=" in query

            if is_playlist_url:
                # Processar playlist
                await processing_msg.edit(
                    content="📋 Processando playlist... Isso pode levar alguns segundos.\n"
                    "💡 Use `.cancelar` para interromper o processamento."
                )

                # Variáveis para controle de adição
                songs_added = 0
                songs_failed = 0
                first_song_playing = False

                # Callback para atualizar progresso E adicionar músicas em tempo real
                async def update_progress(
                    current, total, processed, failed, current_title, song=None
                ):
                    nonlocal songs_added, songs_failed, first_song_playing

                    # Se recebeu uma música, adicionar à fila IMEDIATAMENTE
                    if song:
                        try:
                            # Primeira música: tocar imediatamente se nada está tocando
                            if not player.is_playing and not first_song_playing:
                                first_song_playing = True
                                songs_added += 1
                                # Tocar em background (não bloquear processamento)
                                asyncio.create_task(
                                    self.music_service.play_song(
                                        player, ctx.voice_client, song
                                    )
                                )
                                self.logger.info(
                                    f"🎵 Tocando primeira música: {song.title}"
                                )
                            else:
                                # Adicionar às próximas da fila
                                if len(player.queue) < config.MAX_QUEUE_SIZE:
                                    player.add_song(song)
                                    songs_added += 1
                                    self.logger.info(
                                        f"➕ Adicionada à fila: {song.title}"
                                    )
                        except Exception as e:
                            songs_failed += 1
                            self.logger.warning(f"Erro ao adicionar música: {e}")

                    # Atualizar mensagem de progresso
                    try:
                        progress_text = (
                            f"📋 **Processando Playlist**\n\n"
                            f"📊 Progresso: {current}/{total} itens\n"
                            f"✅ Adicionadas: {songs_added} músicas\n"
                            f"❌ Falhas: {failed}\n"
                            f"🎵 Processando: {current_title[:40]}...\n\n"
                            f"💡 Use `.cancelar` para interromper"
                        )
                        await processing_msg.edit(content=progress_text)
                    except (discord.HTTPException, asyncio.TimeoutError) as e:
                        self.logger.debug(f"Erro ao atualizar progresso: {e}")
                        pass  # Ignorar erros de edição (rate limit, etc)
                    except Exception as e:
                        self.logger.error(
                            f"Erro inesperado ao atualizar progresso: {e}"
                        )

                result = await self.music_service.extract_playlist(
                    query, ctx.author, player, update_progress
                )

                # Músicas já foram adicionadas em tempo real pelo callback!
                # Apenas verificar se alguma foi adicionada
                if songs_added == 0 and not result["songs"]:
                    await processing_msg.edit(
                        content="❌ Nenhuma música pôde ser extraída da playlist."
                    )
                    return

                # Calcular músicas que não couberam (se houver)
                songs_skipped = max(0, len(result["songs"]) - songs_added)

                # Criar embed com resumo
                embed_title = "📋 Playlist Adicionada"
                embed_color = discord.Color.blue()

                # Se foi cancelado, mudar título e cor
                if result.get("cancelled", False):
                    embed_title = "� Playlist Cancelada"
                    embed_color = discord.Color.orange()

                embed = discord.Embed(
                    title=embed_title,
                    description=f"**{result.get('playlist_title', 'Playlist')}**",
                    color=embed_color,
                )

                # Informação sobre total e processamento
                total_info = f"{result['total']} itens na playlist"
                if result.get("not_processed", 0) > 0:
                    total_info += f"\n⚠️ Apenas {result['processed']} foram processados (limite da fila)"

                embed.add_field(
                    name="📊 Total",
                    value=total_info,
                    inline=False,
                )

                embed.add_field(
                    name="✅ Adicionadas",
                    value=f"{songs_added} músicas",
                    inline=True,
                )

                if result["failed"] > 0:
                    embed.add_field(
                        name="❌ Falhas",
                        value=f"{result['failed']} músicas",
                        inline=True,
                    )

                if songs_skipped > 0:
                    embed.add_field(
                        name="⚠️ Ignoradas",
                        value=f"{songs_skipped} músicas (fila cheia)",
                        inline=True,
                    )

                # Adicionar erros se houver (limitado)
                if result["errors"]:
                    error_list = "\n".join(result["errors"][:5])
                    if len(result["errors"]) > 5:
                        error_list += f"\n... e mais {len(result['errors']) - 5} erros"
                    embed.add_field(
                        name="⚠️ Detalhes dos Erros",
                        value=f"```{error_list}```",
                        inline=False,
                    )

                await processing_msg.edit(content=None, embed=embed)

                # Primeira música já foi tocada automaticamente pelo callback!
                # Não precisa fazer nada aqui

            else:
                # Processar música única
                song = await self.music_service.extract_info(query, ctx.author)

                # Se já está tocando, adicionar à fila
                if player.is_playing:
                    player.add_song(song)

                    embed = discord.Embed(
                        title="➕ Adicionado à Fila",
                        description=f"**{song.title}**",
                        color=discord.Color.green(),
                    )
                    embed.add_field(name="Canal", value=song.uploader, inline=True)
                    embed.add_field(
                        name="Posição", value=len(player.queue), inline=True
                    )
                    embed.set_thumbnail(url=song.thumbnail)

                    await processing_msg.edit(content=None, embed=embed)
                else:
                    # Tocar imediatamente
                    await self.music_service.play_song(player, ctx.voice_client, song)
                    await processing_msg.edit(content=None, embed=song.to_embed())

        except ValueError as e:
            # Erros específicos de validação com mensagens amigáveis
            self.logger.warning(f"Erro de validação ao tocar música: {e}")
            await processing_msg.edit(content=f"⚠️ {str(e)}")
        except Exception as e:
            # Outros erros mais técnicos
            self.logger.error(f"Erro ao tocar música: {e}", exc_info=True)

            error_str = str(e).lower()

            # Determinar mensagem de erro baseada no tipo
            if "copyright" in error_str or "blocked" in error_str:
                error_msg = (
                    "❌ Este vídeo está bloqueado por direitos autorais e não pode ser reproduzido.\n"
                    "💡 Tente buscar outra versão ou música similar."
                )
            elif "age" in error_str or "sign in to confirm" in error_str:
                error_msg = (
                    "🔞 Este vídeo tem restrição de idade e não pode ser reproduzido.\n"
                    "💡 Tente buscar outra versão da música."
                )
            elif "private" in error_str:
                error_msg = "❌ Este vídeo é privado e não pode ser acessado."
            elif "unavailable" in error_str and "copyright" not in error_str:
                error_msg = "❌ Este vídeo não está disponível no momento."
            elif "network" in error_str or "connection" in error_str:
                error_msg = "❌ Erro de conexão. Tente novamente em alguns segundos."
            elif "premium" in error_str or "membership" in error_str:
                error_msg = "❌ Este vídeo requer assinatura premium do YouTube."
            else:
                error_msg = f"❌ Erro ao processar música: {str(e)[:100]}..."

            await processing_msg.edit(content=error_msg)

    @commands.command(name="pause", aliases=["pausar"])
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

    @commands.command(name="skip", aliases=["pular", "s"])
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

    @commands.command(name="stop", aliases=["parar"])
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

    @commands.command(name="queue", aliases=["q", "fila"])
    async def queue(self, ctx: commands.Context):
        """Mostra a fila de músicas"""
        player = self.music_service.get_player(ctx.guild.id)

        if not player.current_song and not player.queue:
            await ctx.send("📭 A fila está vazia!")
            return

        embed = discord.Embed(title="🎵 Fila de Músicas", color=discord.Color.blue())

        # Música atual
        if player.current_song:
            current = player.current_song
            requester_text = (
                current.requester.mention if current.requester else "🤖 Autoplay"
            )
            embed.add_field(
                name="▶️ Tocando Agora",
                value=f"**{current.title}**\nPor: {requester_text}",
                inline=False,
            )

        # Próximas músicas
        if player.queue:
            queue_list = player.get_queue()
            next_songs = "\n".join(
                [
                    f"`{i+1}.` **{song.title}** - {song.requester.mention if song.requester else '🤖 Autoplay'}"
                    for i, song in enumerate(queue_list[:10])
                ]
            )

            embed.add_field(
                name=f"📋 Próximas ({len(queue_list)} músicas)",
                value=next_songs,
                inline=False,
            )

            if len(queue_list) > 10:
                embed.set_footer(text=f"... e mais {len(queue_list) - 10} músicas")

        await ctx.send(embed=embed)

    @commands.command(name="nowplaying", aliases=["np", "tocando"])
    async def now_playing(self, ctx: commands.Context):
        """Mostra a música que está tocando"""
        player = self.music_service.get_player(ctx.guild.id)

        if not player.current_song:
            await ctx.send("❌ Nenhuma música está tocando!")
            return

        await ctx.send(embed=player.current_song.to_embed())

    @commands.command(name="volume", aliases=["vol", "v"])
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

    @commands.command(name="clear", aliases=["limpar"])
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

    @commands.command(name="remove", aliases=["remover", "rm"])
    async def remove(self, ctx: commands.Context, position: int):
        """
        Remove uma música da fila pela posição

        Uso: !remove <posição>
        Exemplo: !remove 3 (remove a 3ª música da fila)
        """
        error = self._check_voice_state(ctx)
        if error:
            await ctx.send(error)
            return

        player = self.music_service.get_player(ctx.guild.id)

        if not player.queue:
            await ctx.send("📭 A fila está vazia!")
            return

        if position < 1 or position > len(player.queue):
            await ctx.send(
                f"❌ Posição inválida! Use um número entre 1 e {len(player.queue)}"
            )
            return

        # Remover música (position - 1 porque a fila começa em 0)
        queue_list = list(player.queue)
        removed_song = queue_list.pop(position - 1)
        player.queue = __import__("collections").deque(queue_list)

        embed = discord.Embed(
            title="🗑️ Música Removida",
            description=f"**{removed_song.title}**",
            color=discord.Color.red(),
        )
        embed.add_field(name="Posição", value=f"#{position}", inline=True)
        embed.add_field(
            name="Solicitada por",
            value=(
                removed_song.requester.mention
                if removed_song.requester
                else "🤖 Autoplay"
            ),
            inline=True,
        )
        embed.set_footer(text=f"💡 {len(player.queue)} músicas restantes na fila")

        await ctx.send(embed=embed)

    @commands.command(name="cancelar", aliases=["cancel", "abortar"])
    async def cancel_playlist(self, ctx: commands.Context):
        """Cancela o processamento de playlist em andamento"""
        player = self.music_service.get_player(ctx.guild.id)

        if not player.cancel_playlist_processing:
            player.cancel_playlist_processing = True
            await ctx.send("🛑 Cancelando processamento de playlist...")
        else:
            await ctx.send("⚠️ Nenhum processamento em andamento.")

    @commands.command(name="shuffle", aliases=["embaralhar"])
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

    @commands.command(name="disconnect", aliases=["dc", "leave", "sair"])
    async def disconnect(self, ctx: commands.Context):
        """Desconecta o bot do canal de voz"""
        if not ctx.voice_client:
            await ctx.send("❌ Não estou conectado a nenhum canal de voz!")
            return

        player = self.music_service.get_player(ctx.guild.id)
        player.clear_queue()

        await ctx.voice_client.disconnect()
        await ctx.send("👋 Desconectado do canal de voz")

    @commands.command(name="search", aliases=["buscar"])
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
                title=f"🔍 Resultados para: {query}", color=discord.Color.blue()
            )

            for i, video in enumerate(results, 1):
                embed.add_field(
                    name=f"{i}. {video['title']}",
                    value=f"Canal: {video['channel']}\n[Assistir]({video['url']})",
                    inline=False,
                )

            embed.set_footer(text=f"Use {config.COMMAND_PREFIX}play <URL> para tocar")

            await processing_msg.edit(content=None, embed=embed)

        except Exception as e:
            self.logger.error(f"Erro na busca: {e}", exc_info=True)
            await processing_msg.edit(content=f"❌ Erro na busca: {str(e)}")

    @commands.command(name="autoplay", aliases=["auto"])
    async def autoplay_command(self, ctx: commands.Context, mode: str = None):
        """
        Ativa/desativa autoplay de músicas relacionadas

        Uso:
            .autoplay on  - Ativa autoplay
            .autoplay off - Desativa autoplay
            .autoplay     - Mostra status atual
        """
        player = self.music_service.get_player(ctx.guild.id)

        if not player:
            await ctx.send("❌ Nenhum player ativo neste servidor")
            return

        # Se nenhum modo especificado, mostrar status
        if mode is None:
            status = "🟢 Ativado" if player.autoplay_enabled else "🔴 Desativado"

            embed = discord.Embed(
                title="🎵 Status do Autoplay",
                description=f"O autoplay está atualmente **{status}**",
                color=(
                    discord.Color.green()
                    if player.autoplay_enabled
                    else discord.Color.red()
                ),
            )

            if player.autoplay_enabled:
                embed.add_field(
                    name="ℹ️ Como funciona",
                    value=(
                        "• Quando a fila acabar, o bot automaticamente adiciona músicas relacionadas\n"
                        f"• Adiciona {config.AUTOPLAY_QUEUE_SIZE} músicas por vez\n"
                        f"• Evita repetir as últimas {config.AUTOPLAY_HISTORY_SIZE} músicas\n"
                        "• Use `.autoplay off` para desativar"
                    ),
                    inline=False,
                )

                if len(player.autoplay_history) > 0:
                    embed.add_field(
                        name="📊 Estatísticas",
                        value=f"Músicas no histórico: {len(player.autoplay_history)}",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="💡 Dica",
                    value="Use `.autoplay on` para ativar e o bot continuará tocando músicas similares!",
                    inline=False,
                )

            await ctx.send(embed=embed)
            return

        # Processar comando on/off
        mode_lower = mode.lower()

        if mode_lower in ["on", "ativar", "ativo", "sim", "yes", "1"]:
            if player.autoplay_enabled:
                await ctx.send("ℹ️ Autoplay já está ativado!")
                return

            player.autoplay_enabled = True

            embed = discord.Embed(
                title="✅ Autoplay Ativado",
                description="O bot agora continuará tocando músicas relacionadas quando a fila acabar!",
                color=discord.Color.green(),
            )

            embed.add_field(
                name="🎵 Funcionamento",
                value=(
                    f"• Adiciona automaticamente {config.AUTOPLAY_QUEUE_SIZE} músicas relacionadas\n"
                    "• Baseado na última música tocada\n"
                    f"• Evita repetir últimas {config.AUTOPLAY_HISTORY_SIZE} músicas\n"
                    "• Use `.autoplay off` para desativar a qualquer momento"
                ),
                inline=False,
            )

            embed.set_footer(
                text="💡 O autoplay usa a YouTube API (100 unidades por busca)"
            )

            await ctx.send(embed=embed)
            self.logger.info(f"Autoplay ativado no servidor {ctx.guild.name}")

        elif mode_lower in ["off", "desativar", "desativo", "não", "no", "0"]:
            if not player.autoplay_enabled:
                await ctx.send("ℹ️ Autoplay já está desativado!")
                return

            player.autoplay_enabled = False

            embed = discord.Embed(
                title="🔴 Autoplay Desativado",
                description="O bot não adicionará mais músicas automaticamente.",
                color=discord.Color.red(),
            )

            embed.add_field(
                name="ℹ️ Histórico",
                value=f"Músicas no histórico foram mantidas: {len(player.autoplay_history)}",
                inline=False,
            )

            embed.set_footer(text="💡 Use .autoplay on para reativar")

            await ctx.send(embed=embed)
            self.logger.info(f"Autoplay desativado no servidor {ctx.guild.name}")

        else:
            await ctx.send(
                "❌ Modo inválido! Use:\n"
                "• `.autoplay on` para ativar\n"
                "• `.autoplay off` para desativar\n"
                "• `.autoplay` para ver status"
            )

    @commands.command(name="crossfade", aliases=["fade", "transicao"])
    async def crossfade_command(self, ctx: commands.Context, mode: str = None):
        """
        Ativa/desativa crossfade (transição suave entre músicas)

        Uso:
            .crossfade on  - Ativa crossfade
            .crossfade off - Desativa crossfade
            .crossfade     - Mostra status atual
        """
        player = self.music_service.get_player(ctx.guild.id)

        if not player:
            await ctx.send("❌ Nenhum player ativo neste servidor")
            return

        # Se nenhum modo especificado, mostrar status
        if mode is None:
            status = "🟢 Ativado" if player.crossfade_enabled else "🔴 Desativado"

            embed = discord.Embed(
                title="🎵 Status do Crossfade",
                description=f"O crossfade está atualmente **{status}**",
                color=(
                    discord.Color.green()
                    if player.crossfade_enabled
                    else discord.Color.red()
                ),
            )

            if player.crossfade_enabled:
                embed.add_field(
                    name="ℹ️ Como funciona",
                    value=(
                        f"• Fade out: últimos **{player.crossfade_duration}s** da música\n"
                        f"• Fade in: primeiros **{player.crossfade_duration}s** da próxima\n"
                        "• Transição suave e profissional entre músicas\n"
                        "• Use `.crossfade off` para desativar"
                    ),
                    inline=False,
                )
            else:
                embed.add_field(
                    name="💡 Dica",
                    value="Use `.crossfade on` para ativar transições suaves entre músicas!",
                    inline=False,
                )

            await ctx.send(embed=embed)
            return

        # Processar comando on/off
        mode_lower = mode.lower()

        if mode_lower in ["on", "ativar", "ativo", "sim", "yes", "1"]:
            if player.crossfade_enabled:
                await ctx.send("ℹ️ Crossfade já está ativado!")
                return

            player.crossfade_enabled = True

            embed = discord.Embed(
                title="✅ Crossfade Ativado",
                description="Transições suaves entre músicas ativadas!",
                color=discord.Color.green(),
            )

            embed.add_field(
                name="🎵 Funcionamento",
                value=(
                    f"**Fade Out:** Últimos {player.crossfade_duration}s\n"
                    f"• Volume reduz gradualmente de 100% → 0%\n\n"
                    f"**Fade In:** Primeiros {player.crossfade_duration}s\n"
                    f"• Volume aumenta gradualmente de 0% → 100%\n\n"
                    "Resultado: Transição profissional como em rádios! 📻"
                ),
                inline=False,
            )

            embed.set_footer(
                text=f"💡 Duração configurável via CROSSFADE_DURATION={player.crossfade_duration}"
            )

            await ctx.send(embed=embed)
            self.logger.info(f"Crossfade ativado no servidor {ctx.guild.name}")

        elif mode_lower in ["off", "desativar", "desativo", "não", "no", "0"]:
            if not player.crossfade_enabled:
                await ctx.send("ℹ️ Crossfade já está desativado!")
                return

            player.crossfade_enabled = False

            # Cancelar fade em andamento se houver
            if player.fade_task:
                player.fade_task.cancel()
                player.fade_task = None

            embed = discord.Embed(
                title="🔴 Crossfade Desativado",
                description="Transições suaves desativadas. Músicas mudarão abruptamente.",
                color=discord.Color.red(),
            )

            embed.set_footer(text="💡 Use .crossfade on para reativar")

            await ctx.send(embed=embed)
            self.logger.info(f"Crossfade desativado no servidor {ctx.guild.name}")

        else:
            await ctx.send(
                "❌ Modo inválido! Use:\n"
                "• `.crossfade on` para ativar\n"
                "• `.crossfade off` para desativar\n"
                "• `.crossfade` para ver status"
            )

    @commands.command(name="panel", aliases=["painel", "controle"])
    async def panel_command(self, ctx: commands.Context):
        """
        Cria ou atualiza o painel de controle visual

        O painel mostra:
        • Música atual tocando com progresso
        • Fila de músicas
        • Controles interativos via reações

        Reações disponíveis:
        ⏯️ Play/Pause | ⏭️ Pular | ⏹️ Parar
        🔊 Vol+ | 🔉 Vol- | 🔁 Loop | 🎲 Autoplay
        """
        player = self.music_service.get_player(ctx.guild.id)

        if not player:
            await ctx.send("❌ Nenhum player ativo! Use `.play` para começar.")
            return

        # Deletar mensagem antiga se existir
        if player.control_panel_message:
            try:
                await player.control_panel_message.delete()
            except discord.HTTPException:
                pass
            player.control_panel_message = None

        # Criar novo painel
        await self.music_service.update_control_panel(player)

        # Deletar comando do usuário para manter o chat limpo
        try:
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.command(name="quota", aliases=["api", "limite"])
    async def quota_command(self, ctx: commands.Context):
        """Mostra estatísticas de uso das APIs (YouTube e Groq)"""
        stats = quota_tracker.get_stats()

        # Emoji baseado no percentual do YouTube
        if stats["daily_percent"] < 50:
            emoji = "🟢"
        elif stats["daily_percent"] < 80:
            emoji = "🟡"
        else:
            emoji = "🔴"

        embed = discord.Embed(
            title=f"{emoji} Uso das APIs",
            description="Estatísticas de consumo das APIs do bot",
            color=(
                discord.Color.green()
                if stats["daily_percent"] < 50
                else (
                    discord.Color.orange()
                    if stats["daily_percent"] < 80
                    else discord.Color.red()
                )
            ),
        )

        # ═══════════════ YouTube API ═══════════════
        daily_bar = self._create_progress_bar(stats["daily_percent"])
        embed.add_field(
            name="🎥 YouTube Data API v3",
            value=(
                f"```\n"
                f"Quota Diária:\n"
                f"├─ Usado:    {stats['daily_usage']:,} / {stats['daily_limit']:,}\n"
                f"├─ Restante: {stats['daily_remaining']:,}\n"
                f"└─ {daily_bar} {stats['daily_percent']:.1f}%\n"
                f"\n"
                f"Último Minuto: {stats['minute_usage']:,} / {stats['minute_limit']:,}\n"
                f"```"
            ),
            inline=False,
        )

        # Operações YouTube
        if stats["operations_count"]:
            ops_text = []
            for op_type, count in stats["operations_count"].items():
                cost = quota_tracker.OPERATION_COSTS.get(op_type, 1)
                total = count * cost
                ops_text.append(f"├─ {op_type}: {count}x (custo: {total:,})")

            embed.add_field(
                name="📋 Operações YouTube (24h)",
                value="```\n"
                + "\n".join(ops_text)
                + f"\n└─ Total: {stats['total_operations']} ops```",
                inline=False,
            )

        # ═══════════════ Groq API ═══════════════
        groq_emoji = (
            "🟢"
            if stats["groq_daily_percent"] < 50
            else ("🟡" if stats["groq_daily_percent"] < 80 else "🔴")
        )
        groq_bar = self._create_progress_bar(stats["groq_daily_percent"])

        embed.add_field(
            name=f"{groq_emoji} Groq API (IA Autoplay)",
            value=(
                f"```\n"
                f"Quota Diária:\n"
                f"├─ Usado:    {stats['groq_daily_usage']:,} / {stats['groq_daily_limit']:,}\n"
                f"├─ Restante: {stats['groq_daily_remaining']:,}\n"
                f"└─ {groq_bar} {stats['groq_daily_percent']:.1f}%\n"
                f"\n"
                f"Último Minuto: {stats['groq_minute_usage']} / {stats['groq_minute_limit']}\n"
                f"```"
            ),
            inline=False,
        )

        # Operações Groq
        if stats["groq_operations_count"]:
            groq_ops_text = []
            for op_type, count in stats["groq_operations_count"].items():
                groq_ops_text.append(f"├─ {op_type}: {count}x")

            embed.add_field(
                name="🤖 Operações Groq (24h)",
                value="```\n"
                + "\n".join(groq_ops_text)
                + f"\n└─ Total: {stats['groq_total_operations']} requisições```",
                inline=False,
            )

        embed.set_footer(
            text="💡 As quotas resetam à meia-noite | YouTube: PST | Groq: UTC"
        )

        await ctx.send(embed=embed)

    @commands.command(name="cachestats", aliases=["cache", "estatisticas"])
    async def cache_stats(self, ctx: commands.Context):
        """
        Mostra estatísticas do cache LRU de vídeos

        O cache armazena informações de vídeos já processados para
        evitar reprocessamento e reduzir chamadas ao yt-dlp.

        Uso: !cachestats
        """
        stats = self.music_service.get_cache_stats()

        # Emoji baseado no hit rate
        hit_rate = stats["hit_rate"]
        if hit_rate >= 70:
            emoji = "🟢"
            status = "Excelente"
        elif hit_rate >= 50:
            emoji = "🟡"
            status = "Bom"
        elif hit_rate >= 30:
            emoji = "🟠"
            status = "Regular"
        else:
            emoji = "🔴"
            status = "Baixo"

        embed = discord.Embed(
            title=f"{emoji} Estatísticas do Cache LRU",
            description="Cache de informações de vídeos processados",
            color=(
                discord.Color.green()
                if hit_rate >= 70
                else (
                    discord.Color.orange()
                    if hit_rate >= 50
                    else discord.Color.red()
                )
            ),
        )

        # 📊 Estatísticas Gerais
        embed.add_field(
            name="📊 Estatísticas",
            value=(
                f"```\n"
                f"Tamanho:    {stats['size']}/{stats['max_size']} vídeos\n"
                f"Ocupação:   {stats['size']/stats['max_size']*100:.1f}%\n"
                f"Total Reqs: {stats['total_requests']:,}\n"
                f"```"
            ),
            inline=False,
        )

        # 🎯 Hit Rate
        hits_bar = self._create_progress_bar(hit_rate, length=15)
        embed.add_field(
            name=f"🎯 Hit Rate - {status}",
            value=(
                f"```\n"
                f"Hits:   {stats['hits']:,} ({hit_rate:.1f}%)\n"
                f"Misses: {stats['misses']:,}\n"
                f"{hits_bar}\n"
                f"```"
            ),
            inline=False,
        )

        # ℹ️ Informações
        embed.add_field(
            name="ℹ️ Como Funciona",
            value=(
                "• **Hit:** Vídeo encontrado em cache (rápido)\n"
                "• **Miss:** Vídeo precisa ser extraído (lento)\n"
                "• **LRU:** Remove vídeos menos usados quando cheio\n"
                "• **Meta:** Hit rate >60% é considerado bom"
            ),
            inline=False,
        )

        # 💡 Dicas
        if hit_rate < 50:
            embed.add_field(
                name="💡 Dica",
                value=(
                    "Hit rate baixo pode indicar:\n"
                    "• Músicas muito variadas (normal)\n"
                    "• Cache muito pequeno (aumentar MAX_SIZE)\n"
                    "• Bot reiniciado recentemente (cache limpo)"
                ),
                inline=False,
            )

        embed.set_footer(
            text="💾 Cache é limpo ao reiniciar o bot | LRU = Least Recently Used"
        )

        await ctx.send(embed=embed)

    def _create_progress_bar(self, percent: float, length: int = 20) -> str:
        """Cria uma barra de progresso visual"""
        filled = int((percent / 100) * length)
        empty = length - filled
        return "█" * filled + "░" * empty

    @commands.command(name="help", aliases=["ajuda", "h"])
    async def help_command(self, ctx: commands.Context):
        """Mostra todos os comandos disponíveis"""
        embed = discord.Embed(
            title="🎵 Bot de Música - Comandos",
            description="Lista de todos os comandos disponíveis",
            color=discord.Color.blue(),
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
                f"`{config.COMMAND_PREFIX}remove <posição>` - Remove música da fila",
                f"`{config.COMMAND_PREFIX}clear` - Limpa a fila",
                f"`{config.COMMAND_PREFIX}shuffle` - Embaralha a fila",
                f"`{config.COMMAND_PREFIX}cancelar` - Cancela processamento de playlist",
            ],
            "ℹ️ Informações": [
                f"`{config.COMMAND_PREFIX}nowplaying` - Música atual",
                f"`{config.COMMAND_PREFIX}search <termo>` - Busca no YouTube",
                f"`{config.COMMAND_PREFIX}quota` - Mostra uso das APIs (YouTube + Groq)",
                f"`{config.COMMAND_PREFIX}cachestats` - Mostra estatísticas do cache LRU",
            ],
            "⚙️ Configurações": [
                f"`{config.COMMAND_PREFIX}volume <0-100>` - Ajusta o volume",
                f"`{config.COMMAND_PREFIX}autoplay [on/off]` - Música contínua automática",
                f"`{config.COMMAND_PREFIX}crossfade [on/off]` - Transição suave entre músicas",
                f"`{config.COMMAND_PREFIX}disconnect` - Desconecta o bot",
            ],
            "🎛️ Painel de Controle": [
                f"`{config.COMMAND_PREFIX}panel` - Mostra painel interativo",
                "**Controles via reações:**",
                "⏯️ Play/Pause | ⏭️ Skip | ⏹️ Stop",
                "🔊 Vol+ | 🔉 Vol- | 🔁 Loop | 🎲 Autoplay",
            ],
        }

        for category, cmds in commands_list.items():
            embed.add_field(name=category, value="\n".join(cmds), inline=False)

        embed.set_footer(text="🎵 YouTube Music Bot | Desenvolvido com ❤️")

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Listener para reações adicionadas às mensagens
        Processa reações no painel de controle
        """
        if user.bot:
            return

        # Verificar se é o servidor correto (tem player)
        if not reaction.message.guild:
            return

        player = self.music_service.get_player(reaction.message.guild.id)

        # Verificar se a reação é no painel de controle
        if (
            player.control_panel_message
            and reaction.message.id == player.control_panel_message.id
        ):
            # Verificar se o usuário está no canal de voz
            if not user.voice or not user.voice.channel:
                try:
                    await reaction.remove(user)
                    self.logger.debug(
                        f"🚫 Reação removida - {user.name} não está no canal de voz"
                    )
                except discord.Forbidden:
                    self.logger.warning(
                        "⚠️ Bot sem permissão 'Manage Messages' para remover reações"
                    )
                except discord.HTTPException:
                    pass
                return

            # Verificar se tem voice_client
            voice_client = player.voice_client
            if not voice_client:
                try:
                    await reaction.remove(user)
                    self.logger.debug(f"🚫 Reação removida - bot não está conectado")
                except discord.Forbidden:
                    self.logger.warning(
                        "⚠️ Bot sem permissão 'Manage Messages' para remover reações"
                    )
                except discord.HTTPException:
                    pass
                return

            # Processar a reação
            await self.music_service.handle_panel_reaction(
                player, voice_client, reaction, user
            )


async def setup(bot: commands.Bot):
    """Setup function para carregar o cog"""
    await bot.add_cog(MusicCommands(bot))
