# 📚 Documentação - Bot de Música para Discord

Bem-vindo à documentação completa do Bot de Música para Discord com IA!

---

## 📑 Índice Geral

### 🚀 Guias do Usuário

Para usuários que querem **instalar e usar** o bot:

- **[Início Rápido](guides/inicio-rapido.md)** ⚡ - Configure em 5 minutos
- **[Guia de Credenciais](guides/credenciais.md)** 🔑 - Discord + YouTube
- **[Criando Plugins](guides/criando-plugins.md)** 🔌 - Desenvolva seus próprios plugins
- **[Onde Encontrar](guides/onde-encontrar.md)** 📸 - Screenshots dos portais
- **[Owner ID](guides/owner-id.md)** 👤 - Como obter seu ID do Discord
- **[Visual Rápido](guides/visual-rapido.md)** 🎨 - Resumo visual
- **[Encerramento](guides/encerramento.md)** 🛑 - Como parar o bot corretamente

### 🔧 Documentação Técnica

Para desenvolvedores que querem **entender ou contribuir**:

- **[Arquitetura](technical/arquitetura.md)** 🏗️ - Design patterns e estrutura
- **[Otimizações](technical/otimizacoes.md)** ⚡ - Detalhes das 28 otimizações
- **[Sumário de Otimizações](technical/sumario-otimizacoes.md)** 📊 - Visão executiva (5min)
- **[Sistema de Plugins](technical/plugins.md)** 🔌 - Como criar plugins

### 🎵 Features Especiais

Documentação de funcionalidades avançadas:

- **[Autoplay](features/autoplay.md)** 🤖 - Sistema de autoplay básico
- **[Autoplay com IA](features/autoplay-ia.md)** 🧠 - IA Groq + 4 estratégias

### 📅 Planejamento

Roadmap e planos futuros:

- **[TODO](planning/todo.md)** 📋 - 47 ideias de melhorias
- **[Roadmap](planning/roadmap.md)** 🗺️ - Plano de evolução
- **[Implementação](planning/implementacao.md)** 🔨 - Plano técnico

### ❓ FAQ

- **[FAQ](faq.md)** - Perguntas frequentes e soluções

---

## 📂 Estrutura da Documentação

```
docs/
├── 📄 index.md                     # Este arquivo (índice geral)
├── 📄 faq.md                       # Perguntas frequentes
│
├── 📂 guides/                      # Guias do usuário
│   ├── inicio-rapido.md            # Setup rápido (5min)
│   ├── credenciais.md              # Discord + YouTube
│   ├── criando-plugins.md          # Desenvolva plugins
│   ├── visual-rapido.md            # Resumo visual
│   ├── onde-encontrar.md           # Screenshots
│   ├── owner-id.md                 # Como obter ID
│   └── encerramento.md             # Como parar o bot
│
├── 📂 technical/                   # Documentação técnica
│   ├── arquitetura.md              # Design patterns
│   ├── otimizacoes.md              # Detalhes técnicos
│   ├── sumario-otimizacoes.md      # Visão executiva
│   └── plugins.md                  # Sistema de plugins
│
├── 📂 features/                    # Features especiais
│   ├── autoplay.md                 # Autoplay básico
│   └── autoplay-ia.md              # Autoplay com IA
│
└── 📂 planning/                    # Planejamento
    ├── todo.md                     # Lista de melhorias
    ├── roadmap.md                  # Roadmap geral
    └── implementacao.md            # Plano técnico
```

---

## 🎯 Por Onde Começar?

### 👤 Sou Usuário

1. Leia o **[Início Rápido](guides/inicio-rapido.md)** (5 minutos)
2. Siga o **[Guia de Credenciais](guides/credenciais.md)** para configurar
3. Use **[Onde Encontrar](guides/onde-encontrar.md)** para localizar informações
4. Consulte o **[FAQ](faq.md)** se tiver problemas

### 👨‍💻 Sou Desenvolvedor

1. Leia o **[README principal](../README.md)** para visão geral
2. Entenda a **[Arquitetura](technical/arquitetura.md)** do projeto
3. Veja as **[Otimizações](technical/sumario-otimizacoes.md)** implementadas
4. Consulte o **[CONTRIBUTING](../CONTRIBUTING.md)** para contribuir
5. Veja o **[TODO](planning/todo.md)** para ideias de features

### 🤖 Quero Entender o Autoplay

1. Comece com **[Autoplay](features/autoplay.md)** (conceitos básicos)
2. Depois leia **[Autoplay com IA](features/autoplay-ia.md)** (detalhes da IA)
3. Veja os logs em **[AUTOPLAY_LOGS.md](../AUTOPLAY_LOGS.md)** (raiz do projeto)

---

## 🔗 Links Úteis

### Arquivos na Raiz do Projeto

- **[README.md](../README.md)** - Documentação principal
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Guia de contribuição
- **[CHANGELOG.md](../CHANGELOG.md)** - Histórico de versões
- **[LICENSE](../LICENSE)** - Licença do projeto

### Logs e Runtime

- **[AUTOPLAY_LOGS.md](../AUTOPLAY_LOGS.md)** - Logs detalhados do autoplay
- **[bot.log](../bot.log)** - Log principal do bot (gerado em runtime)

### Código Fonte

- **[main.py](../main.py)** - Ponto de entrada
- **[config.py](../config.py)** - Configurações
- **[requirements.txt](../requirements.txt)** - Dependências

---

## 📝 Contribuindo com a Documentação

Encontrou um erro? Quer melhorar algo? Ótimo!

### Como Contribuir

1. **Fork** o repositório
2. **Edite** o arquivo relevante em `docs/`
3. **Siga** o padrão Markdown existente
4. **Abra** um Pull Request

### Padrões de Documentação

- Use **Markdown** (.md)
- Títulos com emojis descritivos
- Code blocks com syntax highlighting
- Links relativos para outros docs
- Exemplos práticos sempre que possível

### Estrutura de Documento

```markdown
# 🎯 Título Principal

Descrição breve do que o documento contém.

---

## 📋 Índice

- [Seção 1](#seção-1)
- [Seção 2](#seção-2)

---

## Seção 1

Conteúdo...

### Subseção 1.1

Mais detalhes...

## Seção 2

Mais conteúdo...

---

**Última Atualização**: 13 de novembro de 2025
**Autor**: Nome do Autor
```

---

## 🆘 Precisa de Ajuda?

### Não Encontrou o que Procura?

- **[FAQ](faq.md)** - Verifique perguntas frequentes
- **[Issues](https://github.com/MatheusAlves96/bot-youtube-pao/issues)** - Reporte problemas
- **[Discussions](https://github.com/MatheusAlves96/bot-youtube-pao/discussions)** - Faça perguntas

### Sugestões de Melhoria

Tem uma ideia para melhorar a documentação? Abra uma [Issue](https://github.com/MatheusAlves96/bot-youtube-pao/issues/new) com a label `documentation`.

---

## 📊 Estatísticas da Documentação

- **Total de Documentos**: 17 arquivos
- **Guias de Usuário**: 6 documentos
- **Documentação Técnica**: 4 documentos
- **Features**: 2 documentos
- **Planejamento**: 3 documentos
- **FAQ**: 1 documento
- **Última Atualização**: 13 de novembro de 2025

---

<div align="center">

**📚 Documentação mantida com ❤️ pela comunidade**

[🏠 Voltar ao README](../README.md) •
[🤝 Contribuir](../CONTRIBUTING.md) •
[❓ FAQ](faq.md) •
[🐛 Reportar Issue](https://github.com/MatheusAlves96/bot-youtube-pao/issues)

</div>
