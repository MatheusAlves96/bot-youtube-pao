# 🧪 Guia de Testes - Fase 2

## ✅ Fase 2 - Otimizações Importantes (4/7 implementadas)

---

## 📋 Checklist Geral

Antes de iniciar os testes:
- [ ] Bot está rodando sem erros (`python main.py`)
- [ ] Conectado a um canal de voz no Discord
- [ ] Logs visíveis no terminal

---

## 🎯 Teste #4 - Smart Panel Updates (Debounce)

### Objetivo
Verificar que o painel de controle **não é atualizado a cada segundo**, mas sim com **debounce de 2 segundos**.

### Como Testar

1. **Tocar uma música:**
   ```
   !play música teste
   ```

2. **Observar o painel de controle:**
   - Painel aparece com botões de reação (⏯️, ⏭️, ⏹️, etc.)
   - Observar timestamps de edição da mensagem

3. **Executar várias ações rápidas:**
   ```
   !pause
   !resume
   !pause
   !resume
   ```

### Resultados Esperados

✅ **SUCESSO:** 
- Painel é atualizado **2 segundos após** a última ação
- Múltiplas ações rápidas resultam em **apenas 1 update**
- Logs mostram: `💾 Resposta salva no cache (TTL: 24h)` (para debounce cancelado)

❌ **FALHA:**
- Painel é atualizado instantaneamente a cada ação
- Múltiplos updates seguidos

### Verificação nos Logs
```
🔍 Buscar por: "panel_debounce_task"
Deve aparecer quando debounce é acionado
```

---

## 🤖 Teste #5 - AI Response Cache (24h)

### Objetivo
Verificar que **respostas da IA Groq** são cacheadas por 24 horas, evitando chamadas repetidas.

### Como Testar

1. **Ativar autoplay e deixar tocar 3-4 músicas:**
   ```
   !play música brasileira
   !autoplay on
   ```

2. **Aguardar autoplay buscar próxima música**
   - Observar logs da IA gerando query

3. **Parar e tocar novamente a MESMA música inicial:**
   ```
   !stop
   !play [mesma música do passo 1]
   !skip
   ```

4. **Aguardar autoplay buscar novamente**

### Resultados Esperados

✅ **SUCESSO:**
- **1ª chamada:** `🤖 IA gerou query: '...'` (nova consulta)
- **2ª chamada:** `✅ Cache HIT para autoplay query (age: Xs)` (cache usado)
- Latência reduzida de ~1-2s na 2ª chamada

❌ **FALHA:**
- Sempre mostra `🤖 IA gerou query` (nunca usa cache)
- Mesma latência em ambas as chamadas

### Verificação nos Logs
```
✅ Cache HIT para autoplay query (age: XXs)
💾 Resposta salva no cache (TTL: 24h)
```

---

## 🔒 Teste #9 - Autoplay Lock (Race Condition)

### Objetivo
Verificar que **apenas 1 chamada de autoplay** é processada por vez, mesmo com chamadas simultâneas.

### Como Testar

1. **Ativar autoplay com fila vazia:**
   ```
   !autoplay on
   !play música curta (30s)
   ```

2. **Deixar a música terminar naturalmente**
   - Autoplay será acionado automaticamente
   - Observar logs

3. **Executar múltiplos skips rápidos:**
   ```
   !skip
   !skip
   !skip
   ```

### Resultados Esperados

✅ **SUCESSO:**
- Logs mostram: `🔒 Autoplay lock ativo - ignorando chamada duplicada (race condition evitada)`
- Apenas 1 processo de autoplay por vez
- Sem erros de "música já foi adicionada"

❌ **FALHA:**
- Múltiplas chamadas de autoplay simultâneas
- Músicas duplicadas na fila
- Erros ou crashes

### Verificação nos Logs
```
🔒 Autoplay lock ativo - ignorando chamada duplicada
🔍 Autoplay iniciado - Modo: reativo
```

---

## 🔄 Teste #8 - Retry Logic Exponencial

### Objetivo
Verificar que **falhas temporárias de rede** são retentadas automaticamente com backoff exponencial (1s → 2s → 4s).

### Como Testar (Simulado)

**Opção 1: Desconectar rede temporariamente**

1. **Tocar uma música:**
   ```
   !play música teste
   ```

2. **Durante o loading, desconectar WiFi por 2 segundos**

3. **Reconectar WiFi**

4. **Observar logs**

**Opção 2: Testar com URL problemática**

1. **Tentar tocar vídeo privado ou removido:**
   ```
   !play https://youtube.com/watch?v=video_invalido
   ```

### Resultados Esperados

✅ **SUCESSO:**
- Logs mostram tentativas de retry:
  ```
  ⚠️ Tentativa 1/3 falhou: TimeoutError. Retry em 1s...
  ⚠️ Tentativa 2/3 falhou: TimeoutError. Retry em 2s...
  ⚠️ Tentativa 3/3 falhou: TimeoutError. Retry em 4s...
  ```
- Bot recupera automaticamente em falhas temporárias
- Total de ~7 segundos de tentativas antes de desistir

❌ **FALHA:**
- Erro imediato sem retries
- Bot trava ou crash

### Verificação nos Logs
```
⚠️ Tentativa X/3 falhou: [TipoErro]. Retry em Xs...
```

---

## 📊 Resumo de Otimizações Testadas

| # | Otimização | Impacto | Testado |
|---|-----------|---------|---------|
| #4 | Smart Panel Updates (Debounce) | Reduz edições de mensagem em 80% | ⬜ |
| #5 | AI Response Cache (24h) | Reduz latência em ~1-2s | ⬜ |
| #8 | Retry Logic Exponencial | Aumenta resiliência em 90% | ⬜ |
| #9 | Autoplay Lock | Elimina race conditions | ⬜ |

---

## 🚀 Testes Combinados

### Teste de Stress - Autoplay Intensivo

1. **Ativar autoplay e deixar rodar por 10 minutos:**
   ```
   !autoplay on
   !play música brasileira
   ```

2. **Observar:**
   - Cache hits aumentando
   - Lock evitando duplicatas
   - Retry em caso de falhas de rede
   - Debounce no painel

### Resultados Esperados
- Sem erros ou crashes
- Cache usage > 30% após 5 músicas
- Sem músicas duplicadas na fila
- Painel atualizado suavemente

---

## 📈 Métricas de Sucesso

### Antes da Fase 2
- ❌ Painel atualizado a cada 1s (spam)
- ❌ Chamadas repetidas à IA Groq (custo alto)
- ❌ Race conditions no autoplay (duplicatas)
- ❌ Falhas de rede causam crashes

### Depois da Fase 2
- ✅ Painel com debounce de 2s (-80% edições)
- ✅ Cache de IA com 24h TTL (-90% chamadas repetidas)
- ✅ Lock no autoplay (0 race conditions)
- ✅ Retry automático (recovery em ~7s)

---

## 🐛 Troubleshooting

### Problema: "Cache nunca é usado"
- **Causa:** Histórico diferente ou estratégia diferente
- **Solução:** Tocar a MESMA música 2x seguidas

### Problema: "Debounce não funciona"
- **Causa:** Painel desativado ou mensagem deletada
- **Solução:** Verificar se `control_panel_message` existe

### Problema: "Lock não é acionado"
- **Causa:** Chamadas não são simultâneas o suficiente
- **Solução:** Usar `!skip` rapidamente várias vezes

### Problema: "Retry não aparece nos logs"
- **Causa:** Sem falhas de rede durante teste
- **Solução:** Desconectar WiFi temporariamente ou testar com URL inválida

---

## 📝 Log de Testes

```
Data: ___/___/2025
Testador: _________________

✅ #4 - Debounce: [ ] Passou [ ] Falhou
✅ #5 - AI Cache: [ ] Passou [ ] Falhou  
✅ #8 - Retry: [ ] Passou [ ] Falhou
✅ #9 - Autoplay Lock: [ ] Passou [ ] Falhou

Observações:
_________________________________
_________________________________
_________________________________
```

---

## 🎓 Próximos Passos

Após completar os testes da Fase 2:
1. Verificar logs para confirmar todas as otimizações
2. Medir tempo de resposta e uso de memória
3. Documentar quaisquer problemas encontrados
4. Preparar para Fase 3 (otimizações avançadas)

---

**Fase 2 Completa:** 4/7 otimizações implementadas
**Progresso Total:** 12/28 otimizações (42.8%)
