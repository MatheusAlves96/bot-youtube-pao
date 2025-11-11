# 🎵 Autoplay - Música Contínua Automática

## 📖 O que é?

O **Autoplay** é um recurso que permite ao bot continuar tocando músicas automaticamente quando a fila acabar. Ele busca vídeos relacionados à última música tocada usando a YouTube Data API v3.

## 🚀 Como usar

### Ativar Autoplay
```
.autoplay on
```

### Desativar Autoplay
```
.autoplay off
```

### Ver Status
```
.autoplay
```

## ⚙️ Como funciona

1. **Quando a fila acaba**: Se o autoplay estiver ativo, o bot busca automaticamente vídeos relacionados
2. **Busca inteligente**: Usa a YouTube API para encontrar músicas similares baseadas na última tocada
3. **Evita repetição**: Mantém histórico das últimas 50 músicas para não repetir
4. **Adiciona múltiplas**: Adiciona 5 músicas por vez para manter a fila sempre com conteúdo

## 📊 Configurações (arquivo .env)

```env
# Autoplay ativado por padrão?
AUTOPLAY_ENABLED=False

# Quantas músicas adicionar de cada vez
AUTOPLAY_QUEUE_SIZE=5

# Tamanho do histórico (evita repetição)
AUTOPLAY_HISTORY_SIZE=50
```

## 💡 Consumo de API

⚠️ **IMPORTANTE**: O autoplay consome quota da YouTube API!

- **Custo por busca**: 100 unidades
- **Quota diária gratuita**: 10.000 unidades
- **Exemplo**: Com autoplay ativo, você pode tocar ~100 "sessões" por dia antes da quota acabar

### Dicas para economizar quota:

1. **Desative quando não precisar**: Use `.autoplay off` se já tem uma playlist grande
2. **Monitore o uso**: Use `.quota` para ver quanto consumiu
3. **Playlists longas**: Melhor adicionar playlists inteiras do que depender do autoplay

## 🎯 Recursos

### ✅ O que o Autoplay faz:

- ✅ Busca músicas relacionadas automaticamente
- ✅ Evita repetir músicas recentes
- ✅ Adiciona várias músicas por vez
- ✅ Filtra apenas vídeos de categoria "Music"
- ✅ Continua tocando sem interrupção
- ✅ Mostra notificação quando adiciona músicas
- ✅ Mantém histórico persistente por sessão

### ❌ Limitações:

- ❌ Consome quota da API (100 unidades por busca)
- ❌ Histórico é resetado quando o bot reinicia
- ❌ Pode adicionar músicas que você não gosta (mas são relacionadas)
- ❌ Depende da API do YouTube estar disponível

## 🔍 Monitoramento

### Ver uso da API:
```
.quota
```

Mostra:
- Quota usada hoje
- Quota restante
- Operações realizadas
- Histórico de uso

### Exemplo de saída:
```
🟢 YouTube API - Uso de Quota

Quota Diária:
Usado:    500 / 10,000 unidades
Restante: 9,500 unidades
Progresso: ████░░░░░░░░░░░░░░░░ 5.0%

Último Minuto:
Usado: 100 / 1,800,000

Operações (últimas 24h):
search: 5x (custo total: 500)
Total: 5 operações
```

## 🎮 Comandos Relacionados

```
.play <url/busca>     - Adiciona música à fila
.queue                - Ver fila atual
.autoplay on          - Ativar autoplay
.autoplay off         - Desativar autoplay
.autoplay             - Ver status
.quota                - Ver uso da API
.clear                - Limpar fila (não afeta autoplay)
```

## 🐛 Solução de Problemas

### Autoplay não está adicionando músicas?

1. **Verifique se está ativado**: `.autoplay`
2. **Veja a quota**: `.quota` (pode ter esgotado)
3. **Logs no console**: Procure por mensagens de erro
4. **Última música**: Autoplay precisa de pelo menos 1 música tocada

### Músicas repetindo?

- O histórico mantém 50 músicas por padrão
- Se tocar mais de 50, pode começar a repetir
- Aumente `AUTOPLAY_HISTORY_SIZE` no .env

### Quota esgotada?

- Aguarde até meia-noite (PST) para resetar
- Ou desative o autoplay: `.autoplay off`
- Use playlists normais em vez de autoplay

## 📝 Notas Técnicas

### Algoritmo de Busca:

1. Quando música termina e fila vazia
2. Extrai ID do último vídeo tocado
3. Usa YouTube API `search.list` com `relatedToVideoId`
4. Filtra por categoria "Music" (ID=10)
5. Exclui vídeos no histórico
6. Busca 15 vídeos, retorna os 5 primeiros válidos
7. Extrai informações completas com yt-dlp
8. Adiciona à fila e histórico
9. Começa a tocar se nada está tocando

### Prevenção de Repetição:

- Mantém `deque` com últimos 50 IDs de vídeo
- Ao buscar relacionados, passa lista de exclusão
- Histórico é por servidor (guild)
- FIFO: mais antigos saem automaticamente

### Performance:

- Busca assíncrona (não bloqueia bot)
- Flag `is_fetching_autoplay` previne buscas duplicadas
- Cache do yt-dlp acelera extração
- Busca em background durante reprodução

## 🎯 Casos de Uso

### Ideal para:

- 🎧 Ouvir música ambiente enquanto trabalha
- 🎮 Sessões longas de gaming
- 📚 Estudar com música contínua
- 🎉 Festas com música automática

### Não recomendado para:

- ❌ Quando tem playlist específica em mente
- ❌ Quota da API está acabando
- ❌ Quer controle total sobre cada música
- ❌ Servidor com muitos usuários (gasta quota rápido)

## 💬 Feedback

O autoplay adiciona músicas que você não gostou? Considere:

1. Tocar músicas mais específicas inicialmente
2. Criar playlists curadas manualmente
3. Usar `.skip` para pular músicas ruins
4. YouTube API melhora com base no que você toca mais

---

**Desenvolvido com ❤️ para manter a música sempre tocando!**
