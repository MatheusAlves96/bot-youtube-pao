"""
Classe base para plugins
Todos os plugins devem herdar desta classe
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import discord
from discord.ext import commands


class PluginBase(ABC):
    """
    Classe base para todos os plugins do bot

    Atributos:
        name: Nome do plugin
        version: Versão do plugin
        description: Descrição do que o plugin faz
        author: Autor do plugin
        enabled: Se o plugin está habilitado
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.enabled = True

    @property
    @abstractmethod
    def name(self) -> str:
        """Nome do plugin"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Versão do plugin (formato: X.Y.Z)"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Descrição do que o plugin faz"""
        pass

    @property
    def author(self) -> str:
        """Autor do plugin (opcional)"""
        return "Unknown"

    @abstractmethod
    async def on_load(self) -> bool:
        """
        Chamado quando o plugin é carregado

        Returns:
            True se carregou com sucesso, False caso contrário
        """
        pass

    async def on_unload(self) -> bool:
        """
        Chamado quando o plugin é descarregado

        Returns:
            True se descarregou com sucesso, False caso contrário
        """
        return True

    async def on_enable(self) -> bool:
        """
        Chamado quando o plugin é habilitado

        Returns:
            True se habilitou com sucesso, False caso contrário
        """
        self.enabled = True
        return True

    async def on_disable(self) -> bool:
        """
        Chamado quando o plugin é desabilitado

        Returns:
            True se desabilitou com sucesso, False caso contrário
        """
        self.enabled = False
        return True

    def get_commands(self) -> list:
        """
        Retorna lista de comandos Discord do plugin

        Returns:
            Lista de comandos (discord.app_commands.Command)
        """
        return []

    def get_config(self) -> Dict[str, Any]:
        """
        Retorna configurações do plugin

        Returns:
            Dicionário com configurações
        """
        return {}

    async def on_message(self, message: discord.Message) -> None:
        """Hook para processar mensagens"""
        pass

    async def on_reaction_add(
        self, reaction: discord.Reaction, user: discord.User
    ) -> None:
        """Hook para processar reações adicionadas"""
        pass

    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        """Hook para processar mudanças de estado de voz"""
        pass

    def __str__(self) -> str:
        return f"{self.name} v{self.version} by {self.author}"

    def __repr__(self) -> str:
        return f"<Plugin {self.name} v{self.version} enabled={self.enabled}>"
