"""
Gerenciador de Plugins
Carrega, gerencia e executa plugins dinamicamente
"""

import os
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Type
import logging

from .plugin_base import PluginBase


class PluginManager:
    """
    Gerenciador central de plugins

    Responsável por:
    - Descobrir plugins na pasta plugins/
    - Carregar/descarregar plugins dinamicamente
    - Gerenciar ciclo de vida dos plugins
    - Executar hooks dos plugins
    """

    def __init__(self, bot, plugins_dir: str = "plugins"):
        self.bot = bot
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}
        self.logger = logging.getLogger("plugins.manager")

    async def discover_plugins(self) -> List[str]:
        """
        Descobre todos os plugins disponíveis

        Returns:
            Lista de nomes de plugins encontrados
        """
        discovered = []

        if not self.plugins_dir.exists():
            self.logger.warning(f"Diretório de plugins não existe: {self.plugins_dir}")
            return discovered

        # Procurar por arquivos .py (exceto __init__ e base)
        for file in self.plugins_dir.glob("*.py"):
            if file.stem in ["__init__", "plugin_base", "plugin_manager"]:
                continue

            discovered.append(file.stem)

        self.logger.info(f"🔍 Descobertos {len(discovered)} plugins: {discovered}")
        return discovered

    async def load_plugin(self, plugin_name: str) -> bool:
        """
        Carrega um plugin específico

        Args:
            plugin_name: Nome do arquivo do plugin (sem .py)

        Returns:
            True se carregou com sucesso, False caso contrário
        """
        if plugin_name in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' já está carregado")
            return False

        try:
            # Construir caminho do módulo
            plugin_path = self.plugins_dir / f"{plugin_name}.py"

            if not plugin_path.exists():
                self.logger.error(f"Plugin '{plugin_name}' não encontrado")
                return False

            # Importar módulo dinamicamente
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}", plugin_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Encontrar classe que herda de PluginBase
            plugin_class = None
            for item_name in dir(module):
                item = getattr(module, item_name)
                if (
                    isinstance(item, type)
                    and issubclass(item, PluginBase)
                    and item is not PluginBase
                ):
                    plugin_class = item
                    break

            if not plugin_class:
                self.logger.error(
                    f"Plugin '{plugin_name}' não possui classe que herda de PluginBase"
                )
                return False

            # Instanciar plugin
            plugin_instance = plugin_class(self.bot)

            # Chamar on_load
            success = await plugin_instance.on_load()

            if not success:
                self.logger.error(f"Falha ao carregar plugin '{plugin_name}'")
                return False

            # Registrar comandos do plugin
            commands = plugin_instance.get_commands()
            for cmd in commands:
                # Verificar o tipo de comando e registrar apropriadamente
                if hasattr(cmd, "callback"):
                    # É um comando de prefixo (discord.ext.commands)
                    self.bot.add_command(cmd)
                    self.logger.info(f"  ✅ Comando de prefixo registrado: {cmd.name}")
                else:
                    # É um comando slash (discord.app_commands)
                    self.bot.tree.add_command(cmd)
                    self.logger.info(f"  ✅ Comando slash registrado: {cmd.name}")

            # Armazenar plugin
            self.plugins[plugin_name] = plugin_instance

            self.logger.info(f"✅ Plugin carregado: {plugin_instance}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao carregar plugin '{plugin_name}': {e}")
            import traceback

            traceback.print_exc()
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """
        Descarrega um plugin específico

        Args:
            plugin_name: Nome do plugin

        Returns:
            True se descarregou com sucesso, False caso contrário
        """
        if plugin_name not in self.plugins:
            self.logger.warning(f"Plugin '{plugin_name}' não está carregado")
            return False

        try:
            plugin = self.plugins[plugin_name]

            # Chamar on_unload
            await plugin.on_unload()

            # Remover comandos do plugin
            commands = plugin.get_commands()
            for cmd in commands:
                if hasattr(cmd, "callback"):
                    # É um comando de prefixo
                    self.bot.remove_command(cmd.name)
                    self.logger.info(f"  🗑️ Comando de prefixo removido: {cmd.name}")
                else:
                    # É um comando slash
                    self.bot.tree.remove_command(cmd.name)
                    self.logger.info(f"  🗑️ Comando slash removido: {cmd.name}")

            # Remover plugin
            del self.plugins[plugin_name]

            self.logger.info(f"🗑️ Plugin descarregado: {plugin_name}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao descarregar plugin '{plugin_name}': {e}")
            return False

    async def reload_plugin(self, plugin_name: str) -> bool:
        """
        Recarrega um plugin (descarrega e carrega novamente)

        Args:
            plugin_name: Nome do plugin

        Returns:
            True se recarregou com sucesso, False caso contrário
        """
        if plugin_name in self.plugins:
            await self.unload_plugin(plugin_name)

        return await self.load_plugin(plugin_name)

    async def load_all(self) -> int:
        """
        Carrega todos os plugins descobertos

        Returns:
            Número de plugins carregados com sucesso
        """
        discovered = await self.discover_plugins()
        loaded = 0

        for plugin_name in discovered:
            if await self.load_plugin(plugin_name):
                loaded += 1

        self.logger.info(f"📦 {loaded}/{len(discovered)} plugins carregados")
        return loaded

    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Retorna instância de um plugin carregado"""
        return self.plugins.get(plugin_name)

    def get_all_plugins(self) -> List[PluginBase]:
        """Retorna lista de todos os plugins carregados"""
        return list(self.plugins.values())

    def get_enabled_plugins(self) -> List[PluginBase]:
        """Retorna lista de plugins habilitados"""
        return [p for p in self.plugins.values() if p.enabled]

    async def broadcast_message(self, message) -> None:
        """Envia evento de mensagem para todos os plugins habilitados"""
        for plugin in self.get_enabled_plugins():
            try:
                await plugin.on_message(message)
            except Exception as e:
                self.logger.error(
                    f"Erro no plugin {plugin.name} processando mensagem: {e}"
                )

    async def broadcast_reaction_add(self, reaction, user) -> None:
        """Envia evento de reação para todos os plugins habilitados"""
        for plugin in self.get_enabled_plugins():
            try:
                await plugin.on_reaction_add(reaction, user)
            except Exception as e:
                self.logger.error(
                    f"Erro no plugin {plugin.name} processando reação: {e}"
                )

    async def broadcast_voice_state_update(self, member, before, after) -> None:
        """Envia evento de mudança de voz para todos os plugins habilitados"""
        for plugin in self.get_enabled_plugins():
            try:
                await plugin.on_voice_state_update(member, before, after)
            except Exception as e:
                self.logger.error(f"Erro no plugin {plugin.name} processando voz: {e}")
