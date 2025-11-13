# 🧪 Testes - Bot de Música para Discord

Diretório de testes unitários e de integração do projeto.

---

## 📋 Estrutura

```
tests/
├── README.md                       # Este arquivo
├── test_batch_processing.py        # Testes de processamento em batch
└── test_duration_parse.py          # Testes de parsing de duração
```

---

## 🚀 Como Executar os Testes

### Instalar Dependências de Teste

```bash
pip install pytest pytest-asyncio pytest-cov
```

### Executar Todos os Testes

```bash
# Rodar todos os testes
pytest

# Com verbose
pytest -v

# Com cobertura
pytest --cov=. --cov-report=html

# Teste específico
pytest tests/test_duration_parse.py
```

---

## 📝 Testes Disponíveis

### `test_batch_processing.py`

Testa o sistema de processamento em batch de vídeos do YouTube.

**O que é testado:**
- Processamento de múltiplos vídeos simultaneamente
- Validação de dados retornados
- Performance do batch processing

**Como rodar:**
```bash
pytest tests/test_batch_processing.py -v
```

### `test_duration_parse.py`

Testa o parsing de durações no formato ISO 8601 do YouTube.

**O que é testado:**
- Parsing de `PT1H2M3S` → `3723` segundos
- Parsing de `PT4M33S` → `273` segundos
- Casos extremos (PT0S, PT1H, etc)

**Como rodar:**
```bash
pytest tests/test_duration_parse.py -v
```

---

## ✅ Cobertura de Testes

**Status Atual:**
- `test_batch_processing.py`: ✅ Implementado
- `test_duration_parse.py`: ✅ Implementado
- `test_music_service.py`: ⏳ Planejado
- `test_youtube_service.py`: ⏳ Planejado
- `test_ai_service.py`: ⏳ Planejado
- `test_quota_tracker.py`: ⏳ Planejado

**Meta**: Cobertura >80%

---

## 🎯 Próximos Testes a Implementar

### Alta Prioridade

- [ ] **test_music_service.py**
  - Testar `extract_info()` com URLs válidas/inválidas
  - Testar `extract_playlist()` com playlists
  - Testar sistema de fila (add, remove, clear, shuffle)
  - Testar crossfade e pré-carregamento

- [ ] **test_youtube_service.py**
  - Testar `search_video()` com queries
  - Testar `get_related_videos()` com filtros
  - Testar `get_videos_duration_batch()` em lote
  - Testar validação de vídeos pela IA

- [ ] **test_ai_service.py**
  - Testar `generate_autoplay_query()` com estratégias
  - Testar `validate_videos()` com diferentes tipos
  - Testar cache de respostas (24h TTL)
  - Testar fallback quando IA indisponível

### Média Prioridade

- [ ] **test_quota_tracker.py**
  - Testar rastreamento de quota YouTube
  - Testar rastreamento de quota Groq
  - Testar limites por minuto
  - Testar reset diário

- [ ] **test_bot_client.py**
  - Testar carregamento de cogs
  - Testar eventos (on_ready, on_error)
  - Testar shutdown gracioso

- [ ] **test_plugin_system.py**
  - Testar carregamento de plugins
  - Testar hot reload
  - Testar comandos de plugins

---

## 📚 Recursos de Teste

### Pytest Fixtures Úteis

```python
import pytest
from unittest.mock import Mock, AsyncMock

@pytest.fixture
def mock_discord_member():
    """Mock de um membro do Discord"""
    member = Mock()
    member.id = 123456789
    member.name = "TestUser"
    member.mention = "@TestUser"
    return member

@pytest.fixture
def mock_voice_client():
    """Mock de um cliente de voz"""
    client = Mock()
    client.is_connected.return_value = True
    client.is_playing.return_value = False
    return client

@pytest.fixture
async def music_service():
    """Fixture para o serviço de música"""
    from services.music_service import MusicService
    service = MusicService.get_instance()
    yield service
    # Cleanup se necessário
```

### Testes Assíncronos

```python
import pytest

@pytest.mark.asyncio
async def test_extract_info_valid_url(music_service, mock_discord_member):
    """Testa extração de informações de URL válida"""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    song = await music_service.extract_info(url, mock_discord_member)

    assert song is not None
    assert song.title != ""
    assert song.url == url
```

### Mocking de APIs Externas

```python
from unittest.mock import patch

@pytest.mark.asyncio
@patch('services.youtube_service.YouTubeService.search_video')
async def test_search_with_mock(mock_search):
    """Testa busca com mock da API"""
    mock_search.return_value = [
        {
            'id': 'video1',
            'title': 'Test Video',
            'channel': 'Test Channel'
        }
    ]

    results = await youtube_service.search_video("test")

    assert len(results) == 1
    assert results[0]['title'] == 'Test Video'
```

---

## 🔧 Configuração do Pytest

### `pytest.ini` (raiz do projeto)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --tb=short
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

---

## 💡 Boas Práticas

### Nomenclatura

- **Arquivos**: `test_<modulo>.py`
- **Classes**: `TestNomeDaClasse`
- **Funções**: `test_<funcionalidade>_<cenario>`

### Estrutura de Teste

```python
def test_funcionalidade_cenario():
    """Docstring explicando o teste"""
    # Arrange (Preparar)
    input_data = "test"
    expected_output = "TEST"

    # Act (Agir)
    result = funcao_a_testar(input_data)

    # Assert (Verificar)
    assert result == expected_output
```

### Cobertura

- Teste casos de **sucesso** e **falha**
- Teste **edge cases** (valores extremos)
- Teste **exceções** esperadas
- Mock **APIs externas** (YouTube, Groq, Discord)

---

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError"

```bash
# Certifique-se de estar no diretório raiz
cd c:\Users\Matheus\Documents\projeto\bot-youtube-pao

# Instale o projeto em modo development
pip install -e .
```

### Erro: "asyncio.TimeoutError"

```python
# Aumente o timeout em testes assíncronos
@pytest.mark.asyncio
@pytest.mark.timeout(30)  # 30 segundos
async def test_slow_operation():
    pass
```

### Testes Lentos

```bash
# Execute apenas testes rápidos
pytest -m "not slow"

# Execute apenas testes de unidade
pytest -m unit
```

---

## 📊 CI/CD

### GitHub Actions (Planejado)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov

    - name: Run tests
      run: pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 🤝 Contribuindo com Testes

Veja [CONTRIBUTING.md](../CONTRIBUTING.md) para detalhes sobre:
- Como escrever testes
- Padrões de código
- Como submeter Pull Requests

---

**Última Atualização**: 13 de novembro de 2025
**Mantenedor**: [@MatheusAlves96](https://github.com/MatheusAlves96)
