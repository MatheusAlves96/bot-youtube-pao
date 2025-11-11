# 📊 Sistema de Logs do Autoplay

## Visão Geral

O bot possui um **sistema de log especializado** para o Autoplay, separado dos logs gerais, que registra todo o fluxo de decisão e operação do sistema de reprodução automática.

## Arquivos de Log

### 📁 `bot.log` (Log Geral)
- **Localização**: Raiz do projeto
- **Conteúdo**: Operações gerais do bot (comandos, músicas, erros)
- **Nível**: Configurável via `LOG_LEVEL` (padrão: INFO)

### 📁 `logs/autoplay.log` (Log Especializado)
- **Localização**: `logs/autoplay.log`
- **Conteúdo**: Fluxo completo do autoplay com detalhamento técnico
- **Nível**: DEBUG (registra tudo)
- **Formato**: Estruturado para análise e troubleshooting

## Estrutura de uma Sessão de Autoplay

Cada sessão de autoplay registra as seguintes etapas:

### 1️⃣ **Início da Sessão**
```
================================================================================
🎬 NOVA SESSÃO AUTOPLAY - 2025-11-11 15:30:45
📀 Vídeo base: Five Finger Death Punch - Wash It All Away (Explicit)
👤 Canal: Five Finger Death Punch
================================================================================
```

### 2️⃣ **Estratégia de Busca**
```
🎯 Estratégia #0 | Fonte: IA Groq
🔍 Query gerada: 'heavy metal bandas similar Five Finger Death Punch'
```

**Estratégias Disponíveis:**
- **#0**: IA Groq (gênero detectado)
- **#1**: IA variação (variação do gênero)
- **#2**: IA aleatório (gênero aleatório)
- **#3**: IA brasileiro (música brasileira geral)

### 3️⃣ **Busca na API do YouTube**
```
📡 YouTube API Search retornou 30 resultados (quota: +100)
```

### 4️⃣ **Batch Processing**
```
📦 Processando 24 candidatos em batch...
⚡ Batch Duration API: 24 vídeos em 0.52s (46.2 vídeos/s) - Economia: 23 chamadas!
```

**Otimização**: Uma única chamada API em vez de 24 chamadas individuais (economia de 98% de quota).

### 5️⃣ **Filtros de Duração (por vídeo)**
```
✅ [APROVADO] Breaking Benjamin - The Diary of Jane | 4min | Dentro dos limites (1-15min)
⏭️ [REJEITADO] Metal Music Mix 2024 | 62min | Muito longo (62min > 15min)
⏭️ [REJEITADO] Five Finger Death Punch - Shorts | 0min | Muito curto (0min < 1min)
```

**Filtros Configuráveis:**
- `AUTOPLAY_MIN_DURATION` (padrão: 1 min) - Evita shorts/TikToks
- `AUTOPLAY_MAX_DURATION` (padrão: 15 min) - Evita playlists/lives

### 6️⃣ **Resumo dos Filtros**
```
📊 Filtro de Duração: 18/24 aprovados (75.0%) | Limites: 1-15min
   ├─ 6 vídeos rejeitados por duração
```

### 7️⃣ **Validação IA (por vídeo)**
```
🤖 Validando 18 vídeos com IA (Groq)...

✅ IA [APROVADO] Breaking Benjamin - The Diary of Jane | Confiança: 95% | Razão: Música oficial
❌ IA [REJEITADO] The Story of Five Finger Death Punch | Confiança: 85% | Razão: Documentário
✅ IA [APROVADO] Disturbed - Down With The Sickness | Confiança: 95% | Razão: Gênero similar
```

**Critérios da IA:**
- ✅ Aprovado: Músicas oficiais, covers, remixes, ao vivo, gênero similar
- ❌ Rejeitado: Documentários, podcasts, reações, análises, tutoriais

### 8️⃣ **Resumo da Validação IA**
```
🎯 Validação IA: 15/18 aprovados (83.3%) | Quota Groq: +1
```

### 9️⃣ **Vídeos Adicionados à Fila**
```
🎵 SELECIONADO: Breaking Benjamin - The Diary of Jane
   ├─ Canal: Breaking Benjamin
   └─ URL: https://www.youtube.com/watch?v=...
✅ Adicionado à fila (posição #1): Breaking Benjamin - The Diary of Jane

🎵 SELECIONADO: Disturbed - Down With The Sickness
   ├─ Canal: Disturbed
   └─ URL: https://www.youtube.com/watch?v=...
✅ Adicionado à fila (posição #2): Disturbed - Down With The Sickness
```

### 🔟 **Finalização da Sessão**
```
✅ Sessão finalizada: SUCESSO
📊 Vídeos adicionados: 2 | Tempo total: 3.42s
================================================================================
```

## Análise de Falhas

### ⚠️ Tentativa Falhada
```
⚠️ Tentativa 1/2 falhou | Razão: Nenhum vídeo encontrado após filtros
```

**Detecção de Loop:**
- Após **2 falhas consecutivas**, o sistema muda automaticamente para a próxima estratégia
- Previne loops infinitos quando histórico está muito cheio

### ❌ Erro Crítico
```
❌ ERRO: Timeout na busca de vídeos relacionados
   └─ Exceção: TimeoutError: Request timeout after 30s

❌ Sessão finalizada: FALHA
📊 Vídeos adicionados: 0 | Tempo total: 30.15s
================================================================================
```

## Métricas Importantes

### 🎯 Taxa de Aprovação por Etapa

1. **Busca API → Batch**: ~80% passam filtros iniciais (título, canal)
2. **Batch → Duração**: ~70-80% passam filtros de duração
3. **Duração → IA**: ~80-85% passam validação IA
4. **Taxa Final**: ~50-60% dos vídeos originais chegam à fila

### ⚡ Performance

- **Batch Processing**: ~40-60 vídeos/segundo
- **Tempo Total**: 2-5 segundos por sessão (com IA)
- **Economia de Quota**: 95%+ (batch API + IA)

## Troubleshooting

### Problema: "Nenhum vídeo encontrado"

**Verifique no log:**
```
📊 Filtro de Duração: 0/24 aprovados (0.0%) | Limites: 1-15min
   ├─ 24 vídeos rejeitados por duração
```

**Solução**: Ajustar `AUTOPLAY_MAX_DURATION` no `.env`:
```env
# Para heavy metal/rock progressivo
AUTOPLAY_MAX_DURATION=20

# Para pop/eletrônica
AUTOPLAY_MAX_DURATION=10
```

### Problema: IA rejeitando músicas válidas

**Verifique no log:**
```
❌ IA [REJEITADO] Metallica - Enter Sandman (Live) | Confiança: 85% | Razão: Suspeita de cover
```

**Causa**: IA muito conservadora
**Solução**: Conteúdo já aprovado mesmo que IA rejeite (fallback automático)

### Problema: Estratégias não variando

**Verifique no log:**
```
🎯 Estratégia #0 | Fonte: IA Groq
🎯 Estratégia #0 | Fonte: IA Groq  (sempre a mesma)
```

**Causa**: Sistema só muda após 2 falhas consecutivas
**Comportamento Normal**: Estratégia 0 funciona na maioria dos casos

## Configurações Relacionadas

```env
# Filtros de duração do autoplay
AUTOPLAY_MIN_DURATION=1      # Min em minutos (evita shorts)
AUTOPLAY_MAX_DURATION=15     # Max em minutos (evita playlists)

# Tamanho da fila de autoplay
AUTOPLAY_QUEUE_SIZE=2        # Músicas adicionadas por vez

# Histórico (evita repetições)
AUTOPLAY_HISTORY_SIZE=100    # Últimas X músicas

# Nível de log geral (autoplay sempre usa DEBUG)
LOG_LEVEL=INFO               # DEBUG para máximo detalhamento no bot.log
```

## Leitura do Log

### Buscar Sessões Específicas
```bash
# Todas as sessões
grep "NOVA SESSÃO AUTOPLAY" logs/autoplay.log

# Sessões com falha
grep "Sessão finalizada: FALHA" logs/autoplay.log

# Vídeos rejeitados pela IA
grep "IA \[REJEITADO\]" logs/autoplay.log
```

### Analisar Performance
```bash
# Tempo médio das sessões
grep "Tempo total:" logs/autoplay.log

# Taxa de aprovação dos filtros
grep "Filtro de Duração:" logs/autoplay.log

# Taxa de aprovação da IA
grep "Validação IA:" logs/autoplay.log
```

### Debugar Filtros de Duração
```bash
# Vídeos rejeitados por serem muito longos
grep "Muito longo" logs/autoplay.log

# Vídeos rejeitados por serem muito curtos
grep "Muito curto" logs/autoplay.log
```

## Benefícios do Sistema de Logs

✅ **Debugging Facilitado**: Identifique rapidamente onde o autoplay falha  
✅ **Otimização**: Analise performance de cada etapa  
✅ **Auditoria**: Histórico completo das decisões da IA  
✅ **Troubleshooting**: Resolva problemas sem adivinhar  
✅ **Métricas**: Taxas de aprovação, tempo de resposta, uso de quota  

## Exemplo de Análise de Problema

**Usuário reporta**: "Autoplay não está funcionando para heavy metal"

**Análise do log** (`logs/autoplay.log`):
```
📊 Filtro de Duração: 0/24 aprovados (0.0%) | Limites: 1-10min
   ├─ 24 vídeos rejeitados por duração
⏭️ [REJEITADO] Iron Maiden - Rime of the Ancient Mariner | 13min | Muito longo (13min > 10min)
⏭️ [REJEITADO] Dream Theater - Octavarium | 24min | Muito longo (24min > 10min)
```

**Diagnóstico**: Limite de 10min muito restritivo para metal progressivo  
**Solução**: Aumentar `AUTOPLAY_MAX_DURATION` para 15-20 minutos  
**Tempo de resolução**: < 2 minutos ⚡

---

**Dica**: Mantenha `logs/autoplay.log` acessível para troubleshooting. Logs antigos são sobrescritos automaticamente para economizar espaço.
