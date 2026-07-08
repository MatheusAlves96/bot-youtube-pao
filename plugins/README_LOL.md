# 🎮 Plugin League of Legends - Guia de Configuração

Plugin para trazer informações de League of Legends para seu servidor Discord.

---

## 📋 Features Implementadas

✅ **Informações de Invocador** - Busca dados de jogadores pelo nome
✅ **Dados de Campeões** - Informações, stats, skins
✅ **Rotação Gratuita** - Campeões grátis da semana
✅ **Patch Notes** - Versão atual e links
✅ **Easter Eggs** - Reações automáticas a palavras-chave

---

## 🔑 Obtendo a Riot API Key

### Passo 1: Criar Conta de Desenvolvedor

1. Acesse [Riot Developer Portal](https://developer.riotgames.com/)
2. Faça login com sua conta Riot/LoL
3. Aceite os termos de uso

### Passo 2: Gerar API Key

1. No dashboard, vá em **"REGENERATE API KEY"**
2. Copie a chave gerada (formato: `RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`)
3. ⚠️ **Atenção**:
   - A chave **Development** expira em 24 horas
   - Para uso prolongado, aplique para **Production Key**

### Passo 3: Configurar no Bot

Adicione ao seu arquivo `.env`:

```env
# ===== RIOT GAMES API (OPCIONAL - Plugin LoL) =====
RIOT_API_KEY=RGAPI-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 🚀 Instalação do Plugin

### 1. O plugin já está criado!

Arquivo: `plugins/league_of_legends.py`

### 2. Carregar o Plugin

O plugin será carregado automaticamente na próxima vez que iniciar o bot.

Ou carregue manualmente:
```
!plugin load league_of_legends
```

### 3. Verificar Status

```
!plugin list
!plugin info league_of_legends
```

---

## 🎮 Comandos Disponíveis

### Informações do Plugin
```
!lol
!league
```
Mostra informações sobre o plugin e comandos disponíveis.

### Buscar Invocador
```
!summoner <nome>
!invocador <nome>
!player <nome>

Exemplos:
!summoner brTT
!invocador Faker
```
Busca informações de um jogador (nível, ícone, etc).

**Requisito**: RIOT_API_KEY configurada

### Informações de Campeão
```
!champion <nome>
!champ <nome>
!campeao <nome>

Exemplos:
!champion Yasuo
!champ Ahri
!campeao Lee Sin
```
Mostra informações detalhadas do campeão:
- Nome e título
- Splash art
- Função (Assassino, Mago, etc)
- Dificuldade
- Stats base (HP, AD, Armor, MR)

**Nota**: Não requer API Key (usa Data Dragon)

### Rotação Gratuita
```
!rotation
!free
!gratuitos
```
Lista os campeões gratuitos da semana.

**Requisito**: RIOT_API_KEY configurada

### Patch Notes
```
!patch
!patchnotes
!versao
```
Mostra a versão atual do jogo e link para patch notes.

---

## 📊 Exemplos de Uso

### Exemplo 1: Buscar Invocador
```
Você: !summoner brTT

Bot: 🔍 Buscando invocador brTT...

[Embed com:]
👤 brTT
📊 Nível: 487
🆔 Summoner ID: abc12345...
[Ícone do perfil]
```

### Exemplo 2: Info de Campeão
```
Você: !champion Yasuo

Bot: 🔍 Buscando campeão Yasuo...

[Embed com:]
Yasuo - O Imperdoável
[Splash art]
🎭 Função: Assassin, Fighter
📊 Dificuldade: ⭐⭐⭐⭐⭐⭐⭐⭐
💪 Atributos Base:
   ❤️ HP: 490
   ⚔️ AD: 60
   🛡️ Armor: 30
   ✨ MR: 32
```

### Exemplo 3: Rotação Gratuita
```
Você: !rotation

Bot: 🔍 Buscando rotação gratuita...

[Embed com:]
🎁 Campeões Gratuitos da Semana
14 campeões disponíveis gratuitamente!
```

---

## 🔧 Configuração Avançada

### Alterar Região

Por padrão, o plugin usa **BR1** (Brasil). Para alterar:

Edite `plugins/league_of_legends.py`:

```python
async def get_summoner_by_name(self, summoner_name: str, region: str = "na1"):
    # Regiões disponíveis:
    # br1, euw1, eun1, jp1, kr, la1, la2, na1, oc1, ru, tr1
```

### Adicionar Cache

Para reduzir chamadas à API, você pode implementar cache:

```python
from functools import lru_cache
import asyncio

@lru_cache(maxsize=100)
async def get_champion_data_cached(self, champion_name: str):
    return await self.get_champion_data(champion_name)
```

---

## 🆙 Próximas Features (Ideias)

### Médio Prazo
- [ ] **Ranked Info** - Elo, LP, winrate
- [ ] **Match History** - Últimas partidas
- [ ] **Champion Mastery** - Maestria de campeões
- [ ] **Live Game** - Partida em andamento
- [ ] **Leaderboard** - Ranking do servidor

### Longo Prazo
- [ ] **Build Recomendada** - Items, runas
- [ ] **Counter Picks** - Sugestões de counters
- [ ] **Tier List** - Meta atual
- [ ] **Notificações** - Avisos de patch, eventos
- [ ] **Estatísticas do Servidor** - Ranking interno

---

## 📚 Recursos da API

### APIs Utilizadas

1. **Riot Games API** (requer key)
   - Summoner-V4: Informações de invocadores
   - Champion-V3: Rotação gratuita
   - Outros endpoints disponíveis

2. **Data Dragon** (público, sem key)
   - Dados de campeões
   - Imagens (splash, icons)
   - Versões do jogo

### Links Úteis

- [Riot Developer Portal](https://developer.riotgames.com/)
- [API Documentation](https://developer.riotgames.com/apis)
- [Data Dragon](https://developer.riotgames.com/docs/lol#data-dragon)
- [Community Discord](https://discord.gg/riotgamesdevrel)

---

## 🐛 Troubleshooting

### ❌ "API Key não configurada"

**Solução**: Adicione `RIOT_API_KEY` no arquivo `.env`

### ❌ "Invocador não encontrado"

**Causas possíveis**:
1. Nome digitado incorretamente
2. Invocador em outra região
3. Conta inexistente

**Solução**: Verifique o nome e região

### ❌ "API Error: 403"

**Causa**: API Key inválida ou expirada

**Solução**:
1. Gere nova key no Developer Portal
2. Development keys expiram em 24h
3. Considere aplicar para Production key

### ❌ "API Error: 429"

**Causa**: Rate limit excedido

**Solução**:
- Development key: 20 requisições/segundo, 100 req/2min
- Aguarde alguns minutos
- Implemente cache para reduzir chamadas

### ❌ "Campeão não encontrado"

**Causa**: Nome incorreto ou formatação

**Solução**:
- Use nome em inglês
- Remova espaços (LeBlanc → Leblanc)
- Primeira letra maiúscula

---

## 🤝 Contribuindo

Quer adicionar novas features ao plugin?

1. Edite `plugins/league_of_legends.py`
2. Adicione novos comandos em `get_commands()`
3. Teste com `!plugin reload league_of_legends`
4. Documente no README

### Exemplo de Nova Feature

```python
@commands.command(name="build")
async def champion_build(ctx, champion_name: str):
    """Build recomendada para um campeão"""
    # Implementar lógica aqui
    pass

# Adicionar ao return de get_commands():
return [
    lol_info,
    summoner_search,
    champion_info,
    free_rotation,
    patch_info,
    champion_build  # Nova feature
]
```

---

## 📄 Licença

Este plugin segue a mesma licença do bot principal.

**Riot Games Legal**:
- Este projeto não é afiliado com a Riot Games
- League of Legends © Riot Games, Inc.
- Uso da API está sujeito aos [Termos de Uso](https://developer.riotgames.com/policies/general)

---

## 📞 Suporte

**Problemas com o plugin?**
- Abra uma issue: [GitHub Issues](https://github.com/MatheusAlves96/bot-youtube-pao/issues)
- Tag: `plugin:lol`

**Problemas com a API Riot?**
- Acesse: [Riot API Support](https://developer.riotgames.com/support)

---

**Última Atualização**: 13 de novembro de 2025
**Versão do Plugin**: 1.0.0
**Autor**: [@MatheusAlves96](https://github.com/MatheusAlves96)
