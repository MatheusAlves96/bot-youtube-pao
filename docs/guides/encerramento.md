# 🛑 Guia de Encerramento do Bot

## ✅ Método Normal (Ctrl+C)

O bot agora está configurado para responder corretamente ao **Ctrl+C**:

1. Pressione **Ctrl+C** uma vez no terminal onde o bot está rodando
2. Aguarde alguns segundos para encerramento gracioso
3. Se necessário, pressione **Ctrl+C** novamente para forçar o encerramento

### Mensagens que você verá:
```
🛑 Sinal de interrupção recebido (Ctrl+C)
Encerrando bot... (Pressione Ctrl+C novamente para forçar)
Iniciando encerramento gracioso...
Desconectando de X canais de voz...
Fechando conexão do bot...
✅ Bot encerrado com sucesso
👋 Até logo!
```

## 🔧 Melhorias Implementadas

### 1. **Tratamento de Sinais**
- Handler personalizado para `SIGINT` (Ctrl+C)
- Encerramento gracioso em duas etapas:
  - 1ª tentativa: Encerramento gracioso
  - 2ª tentativa: Encerramento forçado

### 2. **Método `shutdown()`**
- Desconecta automaticamente de todos os canais de voz
- Fecha conexão do Discord graciosamente
- Limpa recursos antes de encerrar

### 3. **Tratamento de Exceções**
- Captura `KeyboardInterrupt` em múltiplos níveis
- Usa `finally` para garantir limpeza
- Logs informativos sobre o processo de encerramento

## 🆘 Se Ctrl+C Não Funcionar

### Opção 1: Script de Encerramento
Execute em outro terminal:
```powershell
python stop_bot.py
```

Este script:
- Encontra o processo do bot automaticamente
- Tenta encerrar graciosamente
- Força encerramento se necessário

### Opção 2: Task Manager (Windows)
1. Abra o **Gerenciador de Tarefas** (Ctrl+Shift+Esc)
2. Procure por processo **python.exe** ou **pythonw.exe**
3. Clique com botão direito > **Finalizar Tarefa**

### Opção 3: PowerShell
```powershell
# Encontrar o processo
Get-Process python | Where-Object {$_.CommandLine -like "*main.py*"}

# Encerrar (substitua XXXX pelo PID encontrado)
Stop-Process -Id XXXX
```

### Opção 4: Comando taskkill (Windows)
```powershell
taskkill /F /IM python.exe
```

## 📝 Dicas

### Para desenvolvimento:
- Use **Ctrl+C** uma vez e aguarde
- Monitore os logs para verificar o encerramento
- Se travar, use **Ctrl+C** duas vezes

### Em produção:
- Configure supervisores (systemd, PM2, etc.)
- Use comandos de gestão de processos
- Implemente health checks

## 🐛 Problemas Conhecidos

### Bot não responde ao Ctrl+C:
**Causa**: Loop bloqueado ou operação I/O travada
**Solução**:
1. Usar `stop_bot.py`
2. Forçar com Task Manager
3. Verificar logs para identificar operação travada

### Erro "Event loop is closed":
**Causa**: Tentativa de operação async após loop fechado
**Solução**: O código já trata isso - não requer ação

### Canais de voz não desconectam:
**Causa**: Timeout na desconexão
**Solução**: O código usa `force=True` para garantir desconexão

## ✨ Testando o Encerramento

1. Inicie o bot:
```powershell
python main.py
```

2. Pressione **Ctrl+C**

3. Verifique as mensagens de log:
```
🛑 Sinal de interrupção recebido
Iniciando encerramento gracioso...
✅ Bot encerrado com sucesso
👋 Até logo!
```

Se tudo estiver correto, o processo deve encerrar em 2-5 segundos.
