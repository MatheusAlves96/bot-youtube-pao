"""
Sistema de Plugins do Bot
Permite estender funcionalidades sem modificar o core
"""

from .plugin_base import PluginBase
from .plugin_manager import PluginManager

__all__ = ["PluginBase", "PluginManager"]
