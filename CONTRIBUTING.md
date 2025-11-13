# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o Bot de Música para Discord! Este guia vai ajudá-lo a começar.

---

## 📋 Índice

- [Código de Conduta](#-código-de-conduta)
- [Como Posso Contribuir?](#-como-posso-contribuir)
- [Processo de Desenvolvimento](#-processo-de-desenvolvimento)
- [Padrões de Código](#-padrões-de-código)
- [Estrutura de Commits](#-estrutura-de-commits)
- [Pull Request Process](#-pull-request-process)
- [Reportando Bugs](#-reportando-bugs)
- [Sugerindo Features](#-sugerindo-features)

---

## 📜 Código de Conduta

### Nossa Promessa

Nós nos comprometemos a tornar a participação neste projeto uma experiência livre de assédio para todos, independentemente de idade, tamanho corporal, deficiência, etnia, identidade e expressão de gênero, nível de experiência, nacionalidade, aparência pessoal, raça, religião ou identidade e orientação sexual.

### Nossos Padrões

**Exemplos de comportamento que contribuem para um ambiente positivo:**
- ✅ Usar linguagem acolhedora e inclusiva
- ✅ Respeitar pontos de vista e experiências diferentes
- ✅ Aceitar críticas construtivas graciosamente
- ✅ Focar no que é melhor para a comunidade
- ✅ Mostrar empatia com outros membros da comunidade

**Exemplos de comportamento inaceitável:**
- ❌ Uso de linguagem ou imagens sexualizadas
- ❌ Comentários insultuosos/depreciativos (trolling)
- ❌ Assédio público ou privado
- ❌ Publicar informações privadas de outros sem permissão
- ❌ Outras condutas que seriam consideradas inadequadas em um ambiente profissional

---

## 🎯 Como Posso Contribuir?

### 1. 🐛 Reportar Bugs

Encontrou um bug? Ótimo! Siga estes passos:

1. **Verifique se já foi reportado**: Procure nas [Issues existentes](https://github.com/MatheusAlves96/bot-youtube-pao/issues)
2. **Crie uma nova Issue** com o template de bug report
3. **Inclua**:
   - Descrição clara do problema
   - Steps para reproduzir (1, 2, 3...)
   - Comportamento esperado vs comportamento real
   - Screenshots (se aplicável)
   - Logs relevantes (`bot.log`, traceback)
   - Ambiente: OS, Python version, versão do bot
   - Informações adicionais

**Template de Bug Report:**
```markdown
**Descrição do Bug**
Descrição clara e concisa do que é o bug.

**Steps para Reproduzir**
1. Vá para '...'
2. Execute '....'
3. Digite '....'
4. Veja o erro

**Comportamento Esperado**
O que você esperava que acontecesse.

**Screenshots**
Se aplicável, adicione screenshots para ajudar a explicar seu problema.

**Logs**
```
Cole aqui os logs relevantes do bot.log
```

**Ambiente**
- OS: [ex. Windows 10, Ubuntu 20.04]
- Python Version: [ex. 3.10.0]
- Bot Version: [ex. 2.0.0]

**Contexto Adicional**
Qualquer outra informação relevante sobre o problema.
```

### 2. 💡 Sugerir Features

Tem uma ideia para melhorar o bot? Perfeito!

1. **Verifique se já foi sugerido**: Procure nas Issues e em [TODO.md](TODO.md)
2. **Crie uma Feature Request** com detalhes claros
3. **Inclua**:
   - Descrição da feature
   - Motivação (por que é útil?)
   - Exemplos de uso
   - Possíveis implementações
   - Alternativas consideradas

**Template de Feature Request:**
```markdown
**Descrição da Feature**
Descrição clara e concisa da feature que você quer adicionar.

**Motivação**
Por que essa feature seria útil? Que problema ela resolve?

**Solução Proposta**
Descreva como você imagina que essa feature funcionaria.

**Alternativas Consideradas**
Descreva alternativas que você considerou.

**Contexto Adicional**
Screenshots, mockups, exemplos de outros bots, etc.
```

### 3. 📝 Melhorar Documentação

Documentação nunca é demais! Você pode:
- Corrigir typos
- Clarificar instruções confusas
- Adicionar exemplos
- Traduzir documentação
- Criar tutoriais em vídeo

### 4. 💻 Contribuir com Código

Quer adicionar código? Siga o [Processo de Desenvolvimento](#-processo-de-desenvolvimento) abaixo.

---

## 🔧 Processo de Desenvolvimento

### 1. Fork & Clone

```bash
# Fork o repositório no GitHub (clique em "Fork")

# Clone seu fork
git clone https://github.com/SEU_USERNAME/bot-youtube-pao.git
cd bot-youtube-pao

# Adicione o repositório original como upstream
git remote add upstream https://github.com/MatheusAlves96/bot-youtube-pao.git
```

### 2. Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar dependências de desenvolvimento
pip install pytest pytest-asyncio black flake8 mypy
```

### 3. Criar Branch

```bash
# Atualizar main
git checkout main
git pull upstream main

# Criar branch para sua feature
git checkout -b feature/AmazingFeature
# Ou para bug fix
git checkout -b fix/IssueNumber
```

**Convenção de Nomes de Branches:**
- `feature/nome-da-feature` - Nova funcionalidade
- `fix/numero-da-issue` - Correção de bug
- `docs/descricao` - Alterações na documentação
- `refactor/descricao` - Refatoração
- `test/descricao` - Adição/correção de testes

### 4. Fazer Mudanças

- ✅ Siga os [Padrões de Código](#-padrões-de-código)
- ✅ Adicione type hints em tudo
- ✅ Docstrings em todas as funções/classes
- ✅ Comentários em código complexo
- ✅ Testes para novas funcionalidades

### 5. Testar

```bash
# Rodar testes
pytest

# Type checking
mypy .

# Linting
flake8 .

# Formatação
black .
```

### 6. Commit

```bash
# Adicionar arquivos
git add .

# Commit com mensagem descritiva
git commit -m "Add: Equalizer de áudio com 10 bandas"

# Ou para bug fix
git commit -m "Fix: #123 - Crash ao processar playlist vazia"
```

### 7. Push & Pull Request

```bash
# Push para seu fork
git push origin feature/AmazingFeature

# Abrir Pull Request no GitHub
```

---

## 📐 Padrões de Código

### Python Style Guide (PEP 8)

```python
# ✅ BOM - Type hints, docstring, nomes descritivos
async def extract_video_info(url: str, requester: discord.Member) -> Song:
    """
    Extrai informações de um vídeo do YouTube.

    Args:
        url: URL do vídeo ou termo de busca
        requester: Membro que solicitou a música

    Returns:
        Objeto Song com informações do vídeo

    Raises:
        ValueError: Se a URL for inválida ou vídeo indisponível
    """
    if not url:
        raise ValueError("URL não pode ser vazia")

    # Código aqui...
    return song


# ❌ RUIM - Sem type hints, sem docstring
async def extract(u, r):
    if not u:
        raise ValueError("err")
    # Código aqui...
    return s
```

### Estrutura de Classes

```python
class MusicService:
    """
    Serviço de música - Singleton
    Gerencia players de música para diferentes servidores

    Attributes:
        players: Dict mapeando guild_id para MusicPlayer
        ytdl: Instância do yt-dlp
    """

    _instance: Optional["MusicService"] = None

    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Inicializa o serviço"""
        if self._initialized:
            return

        self._initialized = True
        self.players: Dict[int, MusicPlayer] = {}
        # Resto da inicialização...
```

### Nomenclatura

```python
# Classes: PascalCase
class MusicPlayer:
    pass

# Funções/Métodos: snake_case
def extract_video_info():
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_QUEUE_SIZE = 100

# Variáveis: snake_case
current_song = None

# Privados: _prefixo
_internal_cache = {}

# Protegidos: __prefixo (name mangling)
__private_method()
```

### Type Hints

```python
# ✅ Use type hints em TUDO
from typing import List, Dict, Optional, Any

def get_player(guild_id: int) -> MusicPlayer:
    """Retorna player do servidor"""
    return self.players[guild_id]

async def search_videos(
    query: str,
    max_results: int = 5
) -> List[Dict[str, Any]]:
    """Busca vídeos no YouTube"""
    pass

# Para Optional (pode ser None)
def get_song() -> Optional[Song]:
    return self.current_song
```

### Docstrings (Google Style)

```python
def complex_function(arg1: str, arg2: int, flag: bool = False) -> Dict[str, Any]:
    """
    Descrição breve da função em uma linha.

    Descrição mais detalhada da função, se necessário.
    Pode ter múltiplos parágrafos.

    Args:
        arg1: Descrição do primeiro argumento
        arg2: Descrição do segundo argumento
        flag: Descrição do argumento opcional (default: False)

    Returns:
        Dicionário com as seguintes chaves:
            - 'status': Status da operação (str)
            - 'data': Dados retornados (Any)

    Raises:
        ValueError: Se arg1 for vazio
        ConnectionError: Se não conseguir conectar à API

    Examples:
        >>> result = complex_function("test", 42)
        >>> print(result['status'])
        'success'
    """
    pass
```

### Logs

```python
# ✅ Use logging, não print()
self.logger.info("✅ Música adicionada à fila: {song.title}")
self.logger.warning("⚠️ Quota alta: {usage}/{limit}")
self.logger.error(f"❌ Erro ao processar: {e}", exc_info=True)
self.logger.debug(f"🔍 Debug info: {data}")

# ❌ Não use print()
print("Music added")  # ❌ ERRADO
```

### Async/Await

```python
# ✅ Use async/await corretamente
async def fetch_data(url: str) -> Dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# ✅ Use asyncio.gather para operações paralelas
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)

# ❌ Não bloqueie o event loop
time.sleep(5)  # ❌ ERRADO - bloqueia tudo
await asyncio.sleep(5)  # ✅ CORRETO
```

---

## 📝 Estrutura de Commits

### Formato

```
<tipo>: <descrição curta> [#issue]

[corpo opcional - explicação detalhada]

[rodapé opcional - breaking changes, referências]
```

### Tipos de Commit

- `Add:` - Nova funcionalidade
- `Fix:` - Correção de bug
- `Refactor:` - Refatoração sem mudar comportamento
- `Docs:` - Alterações na documentação
- `Style:` - Formatação, espaços, ponto-e-vírgula
- `Test:` - Adição/correção de testes
- `Perf:` - Melhoria de performance
- `Chore:` - Tarefas de manutenção (build, CI, deps)

### Exemplos

```bash
# ✅ Bons commits
Add: Equalizer de áudio com 10 bandas #45

Fix: #123 - Crash ao processar playlist vazia

Refactor: Simplificar lógica de autoplay

Docs: Atualizar README com instruções de instalação

Perf: Reduzir uso de memória no cache LRU (-30%)

Test: Adicionar testes para music_service.py


# ❌ Commits ruins
Update stuff  # Muito vago
Fixed things  # O que foi corrigido?
WIP  # Não commitar WIP
asdfasdf  # Sem sentido
```

### Mensagens de Commit Detalhadas

```bash
# Para commits complexos, use corpo detalhado
git commit -m "Add: Sistema de equalizer de áudio

Implementa equalizer de 10 bandas com presets:
- Bass Boost
- Treble
- Flat
- Rock, Pop, Jazz

Usa FFmpeg filters para processar áudio em tempo real.
Configuração salva por servidor no banco de dados.

Closes #45"
```

---

## 🔄 Pull Request Process

### 1. Antes de Abrir o PR

**Checklist:**
- [ ] Código segue os [Padrões de Código](#-padrões-de-código)
- [ ] Todos os testes passam (`pytest`)
- [ ] Type checking passa (`mypy`)
- [ ] Linting passa (`flake8`)
- [ ] Código formatado (`black`)
- [ ] Docstrings atualizados
- [ ] README.md atualizado (se necessário)
- [ ] CHANGELOG.md atualizado (features/fixes significativos)
- [ ] Branch atualizado com main (`git merge upstream/main`)

### 2. Criar Pull Request

**Template de PR:**
```markdown
## Descrição
Descrição clara do que o PR faz.

## Tipo de Mudança
- [ ] 🐛 Bug fix (mudança que corrige um issue)
- [ ] ✨ Nova feature (mudança que adiciona funcionalidade)
- [ ] 💥 Breaking change (fix ou feature que quebra compatibilidade)
- [ ] 📝 Documentação (mudanças apenas na documentação)
- [ ] ♻️ Refatoração (mudança que não corrige bug nem adiciona feature)
- [ ] ⚡ Performance (melhoria de performance)

## Issues Relacionadas
Fixes #123
Closes #456

## Testes
Descreva os testes que você executou:
- [ ] Teste A
- [ ] Teste B

## Screenshots (se aplicável)
Adicione screenshots para mudanças visuais.

## Checklist
- [ ] Meu código segue os padrões do projeto
- [ ] Realizei self-review do meu código
- [ ] Comentei código complexo
- [ ] Atualizei a documentação
- [ ] Minhas mudanças não geram novos warnings
- [ ] Adicionei testes que provam que meu fix funciona
- [ ] Testes unitários novos e existentes passam localmente
- [ ] Mudanças dependentes foram mergeadas

## Observações Adicionais
Qualquer informação adicional relevante.
```

### 3. Code Review

- Seja receptivo a feedbacks
- Responda comentários educadamente
- Faça mudanças solicitadas
- Peça esclarecimentos se algo não estiver claro

### 4. Merge

Após aprovação:
1. Squash commits se houver muitos commits pequenos
2. Certifique-se que CI/CD passou
3. Aguarde o merge por um mantenedor

---

## 🐛 Reportando Bugs

### Informações Essenciais

Ao reportar um bug, inclua:

**1. Ambiente**
```
OS: Windows 10 Pro 21H2
Python: 3.10.0
Bot Version: 2.0.0
discord.py: 2.3.2
yt-dlp: 2023.12.30
```

**2. Logs**
```
# bot.log (últimas 50 linhas relevantes)
[2025-11-13 14:23:15] ERROR: Erro ao extrair playlist
Traceback (most recent call last):
  File "services/music_service.py", line 234, in extract_playlist
    ...
ValueError: Playlist vazia ou sem vídeos disponíveis
```

**3. Steps para Reproduzir**
```
1. Digite `!play https://youtube.com/playlist?list=XYZ`
2. Aguardar processamento
3. Bot trava e não responde
4. Logs mostram erro de ValueError
```

**4. Comportamento Esperado vs Real**
```
Esperado: Bot processa playlist e adiciona músicas à fila
Real: Bot trava com erro "Playlist vazia"
```

---

## 💡 Sugerindo Features

### Checklist da Feature

Antes de sugerir, considere:

- [ ] **É útil para a maioria dos usuários?**
- [ ] **Já existe em outro bot?** (análise comparativa)
- [ ] **É tecnicamente viável?**
- [ ] **Tem impacto em performance/quota?**
- [ ] **Complexidade de implementação** (baixa/média/alta)

### Estrutura da Sugestão

```markdown
## Feature: Equalizer de Áudio

### Descrição
Sistema de equalizer de 10 bandas para ajustar graves, médios e agudos.

### Motivação
Usuários querem customizar o som. Exemplo: boost de graves para EDM,
treble para podcasts.

### Solução Proposta
1. Usar FFmpeg filters (`equalizer=...`)
2. Presets salvos por servidor
3. Comando `.eq <preset>` ou `.eq <band> <value>`

### Alternativas
- Equalizer de 5 bandas (mais simples)
- Apenas presets fixos (sem customização)

### Impacto
- Performance: Médio (processamento FFmpeg)
- Complexidade: Média (~2-3 dias)
- Quota: Nenhuma (local)

### Mockup
```
!eq bassboost
✅ Equalizer aplicado: Bass Boost
🔊 Graves: +6dB | Médios: 0dB | Agudos: -3dB
```
```

---

## 🧪 Testes

### Escrevendo Testes

```python
# tests/test_music_service.py
import pytest
from services.music_service import MusicService

@pytest.fixture
def music_service():
    """Fixture para criar instância do serviço"""
    return MusicService.get_instance()

@pytest.mark.asyncio
async def test_extract_info_valid_url(music_service):
    """Testa extração de informações de URL válida"""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    requester = MockMember()  # Mock de discord.Member

    song = await music_service.extract_info(url, requester)

    assert song is not None
    assert song.title != ""
    assert song.url == url
    assert song.requester == requester

@pytest.mark.asyncio
async def test_extract_info_invalid_url(music_service):
    """Testa que URL inválida lança exceção"""
    url = "https://invalid-url.com"
    requester = MockMember()

    with pytest.raises(ValueError):
        await music_service.extract_info(url, requester)
```

### Rodando Testes

```bash
# Todos os testes
pytest

# Teste específico
pytest tests/test_music_service.py

# Com cobertura
pytest --cov=. --cov-report=html

# Verbose
pytest -v
```

---

## 📚 Recursos

### Documentação Oficial
- [Discord.py Docs](https://discordpy.readthedocs.io/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [Groq API](https://console.groq.com/docs)

### Style Guides
- [PEP 8](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

### Ferramentas
- [Black](https://black.readthedocs.io/) - Formatador
- [Flake8](https://flake8.pycqa.org/) - Linter
- [MyPy](https://mypy.readthedocs.io/) - Type checker
- [Pytest](https://docs.pytest.org/) - Testing framework

---

## 🆘 Precisa de Ajuda?

### Onde Encontrar Suporte

- **Issues do GitHub**: [Abrir Issue](https://github.com/MatheusAlves96/bot-youtube-pao/issues/new)
- **Discussões**: [GitHub Discussions](https://github.com/MatheusAlves96/bot-youtube-pao/discussions)
- **Documentação**: [Guias Completos](INDICE.md)
- **FAQ**: [Perguntas Frequentes](FAQ.md)

### Etiqueta

- Seja educado e respeitoso
- Pesquise antes de perguntar (Issues, FAQ, Docs)
- Forneça contexto completo
- Seja paciente aguardando respostas

---

## ⭐ Reconhecimento

Todos os contribuidores serão adicionados ao **CONTRIBUTORS.md** e mencionados nos release notes!

**Obrigado por contribuir! 🎉**

---

**Última Atualização**: 13 de novembro de 2025
**Mantenedor**: [@MatheusAlves96](https://github.com/MatheusAlves96)
