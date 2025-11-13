# 🔌 Sistema de Plugins do Bot

## 📚 Visão Geral

O sistema de plugins permite estender as funcionalidades do bot sem modificar o código core.

## 🏗️ Estrutura

```
plugins/
├── __init__.py              # Exporta classes base
├── plugin_base.py           # Classe base PluginBase
├── plugin_manager.py        # Gerenciador de plugins
├── example_hello.py         # Plugin de exemplo
└── seu_plugin.py            # Seus plugins aqui!
```

## ✨ Criando um Plugin

### 1. Estrutura Básica

```python
from plugins.plugin_base import PluginBase
import discord
from discord import app_commands

class MeuPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "Meu Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Descrição do que meu plugin faz"

    @property
    def author(self) -> str:
        return "Seu Nome"

    async def on_load(self) -> bool:
        """Inicialização do plugin"""
        print(f"✅ {self.name} carregado!")
        return True  # True = sucesso, False = falha
```

### 2. Adicionando Comandos

```python
def get_commands(self) -> list:
    """Retorna lista de comandos Discord"""

    @app_commands.command(
        name="meucomando",
        description="Descrição do comando"
    )
    async def meu_comando(interaction: discord.Interaction):
        await interaction.response.send_message("Olá!")

    return [meu_comando]
```

### 3. Hooks de Eventos

```python
async def on_message(self, message: discord.Message) -> None:
    """Chamado em TODA mensagem"""
    if message.author.bot:
        return

    if "palavra-chave" in message.content.lower():
        await message.channel.send("Detectei a palavra-chave!")

async def on_reaction_add(
    self,
    reaction: discord.Reaction,
    user: discord.User
) -> None:
    """Chamado quando alguém adiciona reação"""
    if reaction.emoji == "👍":
        await reaction.message.channel.send(f"{user.mention} curtiu!")

async def on_voice_state_update(
    self,
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
) -> None:
    """Chamado quando alguém entra/sai de canal de voz"""
    if before.channel is None and after.channel is not None:
        print(f"{member.name} entrou em {after.channel.name}")
```

## 📦 Exemplo Completo: Plugin de Contador

```python
from plugins.plugin_base import PluginBase
import discord
from discord import app_commands

class ContadorPlugin(PluginBase):
    def __init__(self, bot):
        super().__init__(bot)
        self.contador = 0

    @property
    def name(self) -> str:
        return "Contador"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "Conta quantas vezes um comando foi usado"

    async def on_load(self) -> bool:
        self.contador = 0
        return True

    def get_commands(self) -> list:
        @app_commands.command(
            name="contar",
            description="Incrementa o contador"
        )
        async def contar(interaction: discord.Interaction):
            self.contador += 1
            await interaction.response.send_message(
                f"🔢 Contador: {self.contador}"
            )

        @app_commands.command(
            name="resetar",
            description="Reseta o contador"
        )
        async def resetar(interaction: discord.Interaction):
            self.contador = 0
            await interaction.response.send_message(
                "✅ Contador resetado!"
            )

        return [contar, resetar]
```

## 🎮 Comandos de Gerenciamento

### Discord:
- `/plugins` - Lista todos os plugins carregados
- `/plugin_load nome` - Carrega um plugin
- `/plugin_unload nome` - Descarrega um plugin
- `/plugin_reload nome` - Recarrega um plugin

## 🚀 Carregamento Automático

Os plugins são carregados automaticamente quando o bot inicia. Basta colocar o arquivo `.py` na pasta `plugins/`.

## 💡 Dicas

1. **Nome do arquivo**: Use snake_case (exemplo: `meu_plugin.py`)
2. **Nome da classe**: Use PascalCase e termine com `Plugin` (exemplo: `MeuPlugin`)
3. **Sempre retorne True em on_load()**: Se retornar False, o plugin não será carregado
4. **Use self.bot**: Você tem acesso à instância do bot via `self.bot`
5. **Logs**: Use `print()` ou configure um logger próprio

## ⚠️ Limitações

- Plugins não podem modificar outros plugins diretamente
- Comandos duplicados causarão erro
- Plugins com erro no `on_load()` não serão carregados
- Sempre teste seu plugin antes de usar em produção!

## 🔧 Debugging

Se seu plugin não carregar:

1. Verifique se herda de `PluginBase`
2. Verifique se implementa todas as propriedades obrigatórias
3. Verifique se `on_load()` retorna `True`
4. Veja os logs do bot para erros específicos

## 📝 Template Vazio

```python
from plugins.plugin_base import PluginBase

class MeuNovoPlugin(PluginBase):
    @property
    def name(self) -> str:
        return "Nome do Plugin"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "O que este plugin faz"

    async def on_load(self) -> bool:
        # Inicialização aqui
        return True

    # Adicione métodos conforme necessário:
    # - get_commands()
    # - on_message()
    # - on_reaction_add()
    # - on_voice_state_update()
```

## 🎯 Próximos Passos

1. Copie o template acima
2. Salve como `plugins/seu_plugin.py`
3. Implemente suas funcionalidades
4. Reinicie o bot ou use `/plugin_load seu_plugin`
5. Teste com `/plugins` para ver se carregou

---

**Divirta-se criando plugins! 🚀**
