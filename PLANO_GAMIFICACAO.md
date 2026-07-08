# 🎮 Plano de Implementação - Sistema de Gamificação

**Data:** 14 de novembro de 2025
**Versão:** 1.0
**Status:** 📋 Planejamento

---

## 📊 Visão Geral

Implementar um sistema completo de gamificação para aumentar o engajamento dos usuários com o bot de música, criando uma experiência mais interativa e recompensadora.

### 🎯 Objetivos

1. **Aumentar Engajamento**: Usuários mais ativos e participativos
2. **Retenção**: Criar motivação para uso contínuo
3. **Comunidade**: Fomentar competição saudável e colaboração
4. **Diversidade Musical**: Incentivar exploração de novos gêneros
5. **Qualidade**: Recompensar contribuições positivas

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Pastas
```
gamification/
├── __init__.py
├── xp_system.py           # Sistema de XP e níveis
├── achievements.py        # Conquistas e badges
├── leaderboard.py         # Rankings e competições
├── rewards.py             # Sistema de recompensas
├── stats_tracker.py       # Rastreamento de estatísticas
└── models/
    ├── __init__.py
    ├── user_profile.py    # Perfil do usuário
    ├── achievement.py     # Modelo de conquista
    └── season.py          # Temporadas competitivas
```

### Banco de Dados
```sql
-- Tabela de Perfis
CREATE TABLE user_profiles (
    user_id BIGINT PRIMARY KEY,
    guild_id BIGINT NOT NULL,
    username TEXT NOT NULL,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    title TEXT DEFAULT 'Novato',
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Estatísticas
CREATE TABLE user_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    songs_added INTEGER DEFAULT 0,
    songs_completed INTEGER DEFAULT 0,
    total_playtime INTEGER DEFAULT 0,
    genres_explored INTEGER DEFAULT 0,
    playlists_created INTEGER DEFAULT 0,
    commands_used INTEGER DEFAULT 0,
    votes_cast INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

-- Tabela de Conquistas
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    emoji TEXT NOT NULL,
    category TEXT NOT NULL,
    rarity TEXT NOT NULL,
    xp_reward INTEGER DEFAULT 0,
    requirement_type TEXT NOT NULL,
    requirement_value INTEGER NOT NULL
);

-- Tabela de Conquistas dos Usuários
CREATE TABLE user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    progress INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);

-- Tabela de Temporadas
CREATE TABLE seasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tabela de Rankings por Temporada
CREATE TABLE season_rankings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id INTEGER NOT NULL,
    user_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    xp_earned INTEGER DEFAULT 0,
    rank_position INTEGER,
    FOREIGN KEY (season_id) REFERENCES seasons(id),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);
```

---

## 📈 Sistema de XP e Níveis

### Estrutura de Níveis

| Nível | XP Necessário | Título | Emoji | Recompensa |
|-------|---------------|--------|-------|------------|
| 1 | 0 | Novato | 🆕 | - |
| 5 | 500 | Ouvinte | 🎧 | Badge Bronze |
| 10 | 1,500 | DJ Aprendiz | 🎵 | Comando !myplaylist |
| 15 | 3,000 | DJ Intermediário | 🎶 | Volume priority |
| 20 | 5,000 | DJ Profissional | 🎼 | Skip sem votação |
| 25 | 8,000 | Maestro | 🎻 | Badge Prata |
| 30 | 12,000 | Virtuoso | 🎹 | Custom title |
| 40 | 20,000 | Lenda | 🏆 | Badge Ouro |
| 50 | 30,000 | Ícone Musical | 👑 | Badge Platina |
| 75 | 60,000 | Deus da Música | ⚡ | Badge Diamante |
| 100 | 100,000 | Imortal | 💎 | Título personalizado + Cor |

### Fórmula de XP por Nível
```python
def xp_for_level(level: int) -> int:
    """Calcula XP total necessário para alcançar o nível"""
    return int(100 * level * (level + 1) / 2)

def level_from_xp(xp: int) -> int:
    """Calcula o nível baseado no XP total"""
    import math
    return int((-1 + math.sqrt(1 + 8 * xp / 100)) / 2)
```

### Ganho de XP

#### Ações de Música
- **Adicionar música** (+10 XP)
- **Música tocada completamente** (+5 XP)
- **Adicionar à fila durante autoplay** (+15 XP - incentivo!)
- **Criar playlist** (+25 XP)
- **Adicionar música à playlist** (+5 XP)
- **Compartilhar playlist** (+20 XP)

#### Interação Social
- **Votar em skip** (+2 XP)
- **Usar comando pela primeira vez** (+10 XP)
- **Usar comando** (+1 XP)
- **Ficar no canal de voz** (+5 XP/hora)
- **Reagir no painel de controle** (+1 XP)

#### Exploração Musical
- **Descobrir novo gênero** (+30 XP)
- **Tocar música de 5 gêneros diferentes no dia** (+50 XP - Bônus!)
- **Tocar 10 músicas em sequência** (+40 XP - Maratona!)
- **Tocar música com <100k views** (+15 XP - Explorador!)

#### Bônus Temporais
- **Primeira música do dia** (+20 XP)
- **10 músicas no dia** (+50 XP - Bônus Diário!)
- **Ativo 7 dias seguidos** (+200 XP - Bônus Semanal!)
- **Ativo 30 dias seguidos** (+1000 XP - Bônus Mensal!)

#### Multiplicadores
- **Fins de semana** (x1.5 XP - Sexta-Domingo)
- **Eventos especiais** (x2.0 XP)
- **Modo Party** (x1.2 XP - 3+ pessoas no canal)
- **Autoplay ativo** (x1.1 XP)

---

## 🏆 Sistema de Conquistas

### Categorias

#### 🎵 Músicas (Music Master)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Primeiro Passo | 🎵 | Adicione sua primeira música | 1 música | 10 | Comum |
| DJ Iniciante | 🎧 | Adicione 10 músicas | 10 músicas | 50 | Comum |
| Curador Musical | 🎼 | Adicione 50 músicas | 50 músicas | 150 | Incomum |
| Maestro da Fila | 🎻 | Adicione 100 músicas | 100 músicas | 300 | Raro |
| Lenda do Play | 🏆 | Adicione 500 músicas | 500 músicas | 1000 | Épico |
| Deus da Playlist | 👑 | Adicione 1000 músicas | 1000 músicas | 3000 | Lendário |

#### 🎧 Audição (Listener)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Ouvinte Casual | 👂 | Ouça 10 músicas completas | 10 músicas | 30 | Comum |
| Maratonista | 🏃 | Ouça 100 músicas completas | 100 músicas | 200 | Incomum |
| Viciado em Som | 🎸 | Ouça 500 músicas completas | 500 músicas | 800 | Raro |
| Audiófilo | 🎺 | Ouça 1000 músicas completas | 1000 músicas | 2000 | Épico |
| Mestre do Ritmo | 💿 | Ouça 5000 músicas completas | 5000 músicas | 5000 | Lendário |

#### 🌍 Exploração (Explorer)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Curioso | 🔍 | Ouça 3 gêneros diferentes | 3 gêneros | 40 | Comum |
| Explorador Musical | 🗺️ | Ouça 10 gêneros diferentes | 10 gêneros | 100 | Incomum |
| Viajante Sonoro | ✈️ | Ouça 20 gêneros diferentes | 20 gêneros | 300 | Raro |
| Cosmopolita | 🌎 | Ouça 30 gêneros diferentes | 30 gêneros | 600 | Épico |
| Colecionador Universal | 🌌 | Ouça todos os gêneros | 50+ gêneros | 2000 | Lendário |

#### 📋 Playlists (Curator)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Primeira Coleção | 📁 | Crie sua primeira playlist | 1 playlist | 25 | Comum |
| Organizador | 📚 | Crie 5 playlists | 5 playlists | 80 | Incomum |
| Arquivista | 🗄️ | Crie 15 playlists | 15 playlists | 250 | Raro |
| Curador Master | 💼 | Crie 30 playlists | 30 playlists | 600 | Épico |
| Bibliotecário Lendário | 📖 | Crie 50 playlists | 50 playlists | 1500 | Lendário |

#### ⏰ Tempo (Time Warrior)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Dedicado | ⏱️ | Use o bot por 1 hora | 1h | 20 | Comum |
| Fã de Carteirinha | ⏳ | Use o bot por 10 horas | 10h | 100 | Incomum |
| Entusiasta | 🕐 | Use o bot por 50 horas | 50h | 300 | Raro |
| Viciado | 🕰️ | Use o bot por 100 horas | 100h | 800 | Épico |
| Vida Musical | ⌛ | Use o bot por 500 horas | 500h | 3000 | Lendário |

#### 🔥 Sequências (Streaks)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Consistente | 📅 | Use o bot 3 dias seguidos | 3 dias | 30 | Comum |
| Frequentador | 📆 | Use o bot 7 dias seguidos | 7 dias | 100 | Incomum |
| Assíduo | 🗓️ | Use o bot 15 dias seguidos | 15 dias | 250 | Raro |
| Incansável | 📊 | Use o bot 30 dias seguidos | 30 dias | 700 | Épico |
| Imortal | 🔥 | Use o bot 100 dias seguidos | 100 dias | 5000 | Lendário |

#### 👥 Social (Community)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Animador | 🎉 | Toque música com 5+ pessoas | 5 pessoas | 30 | Comum |
| Anfitrião | 🎊 | Toque música com 10+ pessoas | 10 pessoas | 80 | Incomum |
| Estrela da Festa | 🌟 | Toque música com 20+ pessoas | 20 pessoas | 200 | Raro |
| Ídolo Popular | ⭐ | Toque música com 50+ pessoas | 50 pessoas | 500 | Épico |
| Rockstar | 🎸 | Toque música com 100+ pessoas | 100 pessoas | 2000 | Lendário |

#### 🎯 Especiais (Special Events)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Pioneiro | 🚀 | Seja um dos primeiros 100 usuários | Beta tester | 500 | Épico |
| Madrugador | 🌅 | Toque música às 3h da manhã | 03:00 | 50 | Incomum |
| Festeiro | 🎆 | Toque música na virada do ano | 00:00 31/12 | 200 | Raro |
| Descobridor | 💎 | Encontre música com <1k views | <1k views | 100 | Raro |
| Hipster | 😎 | Toque 50 músicas indie | 50 indie | 300 | Épico |

#### 🏅 Elite (Hardcore)
| Conquista | Emoji | Descrição | Requisito | XP | Raridade |
|-----------|-------|-----------|-----------|-----|----------|
| Top 10 | 🥉 | Entre no top 10 do servidor | Rank ≤10 | 500 | Épico |
| Top 3 | 🥈 | Entre no top 3 do servidor | Rank ≤3 | 1000 | Lendário |
| Número 1 | 🥇 | Seja #1 do servidor | Rank 1 | 3000 | Mítico |
| Perfeccionista | 💯 | Alcance nível 100 | Level 100 | 10000 | Mítico |
| Imortal | 👑 | Mantenha streak de 365 dias | 365 dias | 50000 | Divino |

**Total:** 50+ conquistas únicas

---

## 📊 Sistema de Rankings

### Tipos de Ranking

#### 🏆 Global (Servidor)
- Ordenado por XP total
- Atualizado em tempo real
- Top 100 exibido
- Badges especiais para top 10

#### 📅 Semanal
- Reseta toda segunda-feira 00:00
- XP ganho na semana
- Recompensa para top 3: XP bonus (x1.2 próxima semana)

#### 📆 Mensal
- Reseta todo dia 1º às 00:00
- XP ganho no mês
- Recompensa para top 3: Badge exclusivo

#### 🎯 Por Categoria
- **Mais Músicas Adicionadas**
- **Mais Tempo de Audição**
- **Mais Gêneros Explorados**
- **Mais Playlists Criadas**
- **Maior Streak**

### Visualização de Ranking

```
╔════════════════════════════════════════════════════════════╗
║              🏆 RANKING SEMANAL - BOT MUSICAL             ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  🥇 #1  │ 👑 MusicLover     │ Lv 45 │ 12,450 XP │ +850   ║
║  🥈 #2  │ 🎸 DJ_Master      │ Lv 38 │  9,320 XP │ +620   ║
║  🥉 #3  │ 🎧 Audiophile     │ Lv 32 │  7,180 XP │ +480   ║
║  4️⃣ #4  │ 🎵 BeatDrop       │ Lv 28 │  5,940 XP │ +320   ║
║  5️⃣ #5  │ 🎼 Symphony       │ Lv 25 │  4,820 XP │ +280   ║
║  6️⃣ #6  │ 🎹 Melody         │ Lv 22 │  3,960 XP │ +240   ║
║  7️⃣ #7  │ 🎺 JazzMan        │ Lv 20 │  3,280 XP │ +200   ║
║  8️⃣ #8  │ 🎻 Classical      │ Lv 18 │  2,750 XP │ +180   ║
║  9️⃣ #9  │ 🥁 DrumMaster     │ Lv 16 │  2,340 XP │ +150   ║
║  🔟 #10 │ 🎤 Vocalist       │ Lv 15 │  2,100 XP │ +120   ║
║                                                            ║
║  ...                                                       ║
║                                                            ║
║  42 │ ⭐ Você             │ Lv 12 │    890 XP │ +45    ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║  📊 Você subiu 8 posições esta semana! 📈                 ║
║  🎯 Faltam 210 XP para alcançar #41!                      ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🎁 Sistema de Recompensas

### Recompensas por Nível

| Nível | Recompensa | Descrição |
|-------|------------|-----------|
| 5 | Badge Bronze | Ícone visual no perfil |
| 10 | Comando !myplaylist | Criar playlists privadas |
| 15 | Volume Priority | Seus comandos de volume têm prioridade |
| 20 | Skip sem Votação | Pode dar skip direto (1x por hora) |
| 25 | Badge Prata | Ícone visual aprimorado |
| 30 | Custom Title | Escolher título personalizado |
| 40 | Badge Ouro | Ícone visual premium |
| 50 | Badge Platina | Ícone visual elite + cor no nome |
| 75 | Badge Diamante | Ícone visual diamante + animação |
| 100 | Badge Mítico | Tudo + efeito especial nos comandos |

### Recompensas por Conquistas

#### Conquistas Comuns
- XP Bonus: 10-50 XP

#### Conquistas Incomuns
- XP Bonus: 50-150 XP
- Badge visual

#### Conquistas Raras
- XP Bonus: 150-500 XP
- Badge animado
- Título temporário (7 dias)

#### Conquistas Épicas
- XP Bonus: 500-1500 XP
- Badge exclusivo animado
- Título permanente
- Cor no nome (7 dias)

#### Conquistas Lendárias
- XP Bonus: 1500-5000 XP
- Badge lendário animado com brilho
- Título permanente premium
- Cor no nome permanente
- Efeito especial nos comandos

---

## 💬 Comandos de Gamificação

### Perfil e Status

```bash
!profile [@usuário]
# Exibe perfil completo com:
# - Avatar, Nome, Título
# - Nível atual e XP
# - Próximo nível (barra de progresso)
# - Top 5 conquistas
# - Estatísticas gerais
# - Rank no servidor

!level [@usuário]
# Versão simplificada do !profile
# Apenas nível, XP e barra de progresso

!stats [@usuário]
# Estatísticas detalhadas:
# - Músicas adicionadas / ouvidas
# - Tempo total de audição
# - Gêneros explorados
# - Playlists criadas
# - Comandos usados
# - Streak atual

!rank [categoria]
# Mostra ranking do servidor
# Categorias: global, semanal, mensal, músicas, tempo, gêneros
```

### Conquistas

```bash
!achievements [@usuário]
# Lista todas as conquistas
# ✅ Desbloqueadas
# 🔒 Bloqueadas (com progresso se aplicável)

!achievement <nome>
# Detalhes de uma conquista específica
# - Descrição
# - Requisitos
# - Recompensas
# - Progresso atual
# - Quem possui (top 10)

!progress
# Mostra progresso em conquistas próximas
# "Você está a 5 músicas de desbloquear 'DJ Iniciante'!"
```

### Comparação Social

```bash
!compare @usuário
# Compara seu perfil com outro usuário
# - Níveis
# - XP
# - Conquistas (quem tem mais)
# - Estatísticas lado a lado

!versus @usuário [categoria]
# Desafio direto
# Compara estatísticas específicas
# Categorias: músicas, tempo, gêneros, playlists
```

### Rankings

```bash
!top [quantidade] [categoria]
# Exemplos:
# !top           → Top 10 global
# !top 20        → Top 20 global
# !top semanal   → Top 10 da semana
# !top músicas   → Top 10 por músicas adicionadas
# !top tempo     → Top 10 por tempo de audição

!leaderboard [categoria]
# Alias para !top com visual mais elaborado
```

### Títulos e Personalização

```bash
!title <título>
# Muda seu título personalizado (desbloqueia nível 30)
# Máximo 20 caracteres
# Filtro de palavrões

!color <hex>
# Muda cor do seu nome no perfil (desbloqueia nível 50)
# Formato: #RRGGBB
# Exemplo: !color #FF5733
```

---

## 🎨 Interface Visual

### Card de Perfil

```
╔══════════════════════════════════════════════════════════════╗
║  👤 PERFIL DE USUÁRIO                                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   [🎧]  MusicLover  │  👑 Maestro  │  #15 no Servidor      ║
║                                                              ║
║   ┌─ Nível 32 ────────────────────────────────────────┐     ║
║   │ ████████████████░░░░░░░░  78% (7,850 / 10,000 XP) │     ║
║   └──────────────────────────────────────────────────┘     ║
║                                                              ║
║   🏆 Conquistas: 45 / 50  (90%)                             ║
║   🎵 Músicas: 1,245                                         ║
║   ⏱️ Tempo: 156h 32min                                      ║
║   🌍 Gêneros: 28                                            ║
║   🔥 Streak: 42 dias                                        ║
║                                                              ║
║   ╭─ Top Conquistas ─────────────────────────────────╮     ║
║   │ 👑 Maestro              ⏰ Entusiasta             │     ║
║   │ 🏆 Lenda do Play        🗺️ Viajante Sonoro       │     ║
║   │ 🔥 Incansável                                     │     ║
║   ╰──────────────────────────────────────────────────╯     ║
║                                                              ║
║   💬 "A música é a linguagem da alma" 🎶                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Card de Conquista Desbloqueada

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           ✨ CONQUISTA DESBLOQUEADA! ✨                      ║
║                                                              ║
║                        🏆                                    ║
║                  LENDA DO PLAY                               ║
║                                                              ║
║          "Adicione 500 músicas à fila"                      ║
║                                                              ║
║              Raridade: ⭐⭐⭐⭐ ÉPICO                          ║
║                                                              ║
║                  +1000 XP ganhos!                           ║
║                                                              ║
║              Você subiu para Nível 35!                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

### Notificação de Level Up

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                  🎉 LEVEL UP! 🎉                            ║
║                                                              ║
║                   25 → 26                                    ║
║                                                              ║
║              Novo Título Desbloqueado:                       ║
║                   🎻 Maestro                                 ║
║                                                              ║
║                  Recompensas:                                ║
║              • Badge Prata 🥈                                ║
║              • +500 XP Bonus                                 ║
║                                                              ║
║          Próximo nível em 1,200 XP!                         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🚀 Fases de Implementação

### **Fase 1: Fundação (Semana 1-2)**
**Prioridade:** 🔴 Alta

**Objetivos:**
- Criar estrutura de banco de dados
- Implementar sistema básico de XP
- Sistema de níveis (1-100)
- Comandos básicos: !profile, !level, !stats

**Tarefas:**
1. Setup banco de dados SQLite
2. Criar modelos de dados (user_profile, user_stats)
3. Sistema de tracking de ações
4. Cálculo de XP e level-up
5. Comando !profile com card visual
6. Comando !level (simplificado)
7. Comando !stats (estatísticas)
8. Testes unitários

**Entregáveis:**
- ✅ Banco de dados funcional
- ✅ Sistema de XP operacional
- ✅ 3 comandos básicos
- ✅ 90%+ cobertura de testes

---

### **Fase 2: Conquistas (Semana 3-4)**
**Prioridade:** 🔴 Alta

**Objetivos:**
- Sistema completo de conquistas
- 50+ conquistas únicas
- Tracking de progresso
- Notificações de desbloqueio

**Tarefas:**
1. Criar sistema de achievements
2. Definir todas as conquistas (50+)
3. Sistema de verificação de requisitos
4. Tracking de progresso em tempo real
5. Notificações ao desbloquear
6. Comando !achievements
7. Comando !achievement <nome>
8. Comando !progress
9. Cards visuais de conquistas
10. Testes de integração

**Entregáveis:**
- ✅ 50+ conquistas implementadas
- ✅ Sistema de notificação
- ✅ 3 novos comandos
- ✅ Interface visual polida

---

### **Fase 3: Rankings (Semana 5)**
**Prioridade:** 🟡 Média

**Objetivos:**
- Sistema de rankings múltiplos
- Leaderboards dinâmicos
- Competição semanal/mensal

**Tarefas:**
1. Implementar ranking global
2. Sistema de temporadas (semanal/mensal)
3. Rankings por categoria
4. Comando !rank
5. Comando !top
6. Comando !leaderboard
7. Auto-reset de temporadas (cron job)
8. Recompensas para top 3
9. Interface de leaderboard visual

**Entregáveis:**
- ✅ 4 tipos de rankings
- ✅ Sistema de temporadas
- ✅ 3 novos comandos
- ✅ Recompensas automáticas

---

### **Fase 4: Social & Comparação (Semana 6)**
**Prioridade:** 🟢 Baixa

**Objetivos:**
- Recursos sociais e competitivos
- Comparação entre usuários
- Desafios diretos

**Tarefas:**
1. Comando !compare @usuário
2. Comando !versus @usuário
3. Sistema de badges visuais
4. Histórico de competições
5. Notificações de rankings
6. Interface de comparação

**Entregáveis:**
- ✅ 2 novos comandos sociais
- ✅ Sistema de badges
- ✅ Comparações visuais

---

### **Fase 5: Recompensas & Personalização (Semana 7)**
**Prioridade:** 🟢 Baixa

**Objetivos:**
- Sistema de recompensas desbloqueáveis
- Personalização de perfis
- Privilégios por nível

**Tarefas:**
1. Implementar recompensas por nível
2. Sistema de títulos customizados
3. Sistema de cores personalizadas
4. Comando !title
5. Comando !color
6. Privilégios de comandos (skip sem votação, etc)
7. Sistema de badges animados

**Entregáveis:**
- ✅ Sistema de recompensas completo
- ✅ Personalização de perfis
- ✅ Privilégios funcionais
- ✅ 2 novos comandos

---

### **Fase 6: Polimento & Otimização (Semana 8)**
**Prioridade:** 🟢 Baixa

**Objetivos:**
- Otimizar performance
- Melhorar UX
- Testes extensivos
- Documentação

**Tarefas:**
1. Otimização de queries do banco
2. Cache de rankings (Redis)
3. Melhorias visuais
4. Animações e efeitos
5. Testes de stress
6. Documentação completa
7. Tutoriais em vídeo
8. Beta testing com comunidade

**Entregáveis:**
- ✅ Performance otimizada
- ✅ UX polida
- ✅ Documentação completa
- ✅ Sistema 100% testado

---

## 📅 Timeline Resumido

```
Semana 1-2:  Fundação (XP, Níveis, Profile)        [██████████]
Semana 3-4:  Conquistas (50+ Achievements)         [██████████]
Semana 5:    Rankings (Leaderboards)               [█████░░░░░]
Semana 6:    Social (Compare, Versus)              [█████░░░░░]
Semana 7:    Recompensas (Títulos, Cores)          [███░░░░░░░]
Semana 8:    Polimento (UX, Performance)           [░░░░░░░░░░]

Total: 8 semanas (~2 meses)
```

---

## 💡 Ideias Adicionais de Gamificação

### 🎪 Eventos Especiais

#### Eventos Temporais
1. **Double XP Weekend** (Fins de semana)
   - Sexta 18h → Domingo 23:59
   - Todo XP ganha x2
   - Anúncio no servidor

2. **Temática Musical** (Mensal)
   - "Mês do Rock" - Bônus XP para rock
   - "Mês do Jazz" - Conquistas exclusivas de jazz
   - Badge especial do mês

3. **Maratona Musical** (Trimestral)
   - Evento de 48h
   - Objetivos coletivos (servidor)
   - Recompensas para todos se alcançarem meta
   - Ex: "Tocar 1000 músicas juntos"

#### Desafios Semanais
```
╔══════════════════════════════════════════════════════════════╗
║  🎯 DESAFIO DA SEMANA                                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  "Explorador de Ritmos"                                      ║
║                                                              ║
║  Objetivo: Tocar músicas de 5 gêneros diferentes            ║
║                                                              ║
║  Progresso: [████░░░░] 4/5 gêneros                          ║
║                                                              ║
║  Recompensa: +500 XP + Badge "Explorador"                   ║
║                                                              ║
║  Termina em: 2 dias, 5 horas                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

### 🎁 Sistema de Moedas Virtuais

#### "Music Coins" (MC)
- Moeda virtual do bot
- Ganhar através de:
  - Level up (+10 MC)
  - Conquistas (+5 a +50 MC)
  - Desafios semanais (+20 MC)
  - Daily login (+1 MC)

#### Loja de Recompensas
```
!shop
╔══════════════════════════════════════════════════════════════╗
║  🏪 LOJA DE RECOMPENSAS                                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. 🎨 Cor Temporária (7 dias)         │   50 MC           ║
║  2. 👑 Título Temporário (7 dias)      │  100 MC           ║
║  3. 🚀 Boost de XP 2x (24h)            │  150 MC           ║
║  4. ⏭️ Skip sem Votação (1x)          │   20 MC           ║
║  5. 🎵 Playlist Slot Extra             │  200 MC           ║
║  6. 🏆 Badge Exclusivo da Loja         │  500 MC           ║
║  7. 👀 Ver Histórico Completo          │   30 MC           ║
║  8. 📊 Stats Avançadas (30 dias)       │  100 MC           ║
║                                                              ║
║  💰 Seu saldo: 275 MC                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

!buy <item>
```

---

### 🏅 Sistema de Temporadas Competitivas

#### Conceito
- Temporadas de 3 meses (trimestrais)
- Reset parcial de XP (10% mantido)
- Rankings exclusivos por temporada
- Recompensas únicas

#### Estrutura de Temporada
```
Temporada 1: "Despertar Musical"
Data: Jan-Mar 2026
Tema: Exploração de gêneros

Objetivos Especiais:
- Tocar 50 gêneros diferentes
- Adicionar 100 músicas indie
- Maratona de 48h (evento)

Recompensas Exclusivas:
- Badge "Pioneiro S1"
- Título "Explorador do Despertar"
- 1000 XP Bonus para próxima temporada
```

#### Ranking de Temporada
- Top 100 ganham badge exclusivo
- Top 10 ganham título permanente
- Top 1 ganha badge mítico + efeito especial

---

### 🎲 Minigames Musicais

#### 1. "Adivinhe a Música"
```
!game guess

O bot toca 10 segundos de uma música aleatória
Usuários tentam adivinhar:
- Nome da música
- Artista
- Gênero

Pontos por:
- Resposta correta: +50 XP
- Resposta rápida (<10s): +20 XP bonus
- Streak de acertos: +10 XP por streak
```

#### 2. "Batalha de DJs"
```
!game dj_battle @oponente

Cada DJ adiciona 5 músicas
Usuários do servidor votam nas músicas
Vencedor: quem teve mais votos

Prêmio: +200 XP + Badge "DJ Champion"
```

#### 3. "Quiz Musical"
```
!game quiz [tema]

10 perguntas sobre música:
- História da música
- Curiosidades de artistas
- Gêneros musicais
- Teoria musical

Pontos por resposta certa: +10 XP
Tempo limite: 30s por pergunta
```

---

### 📈 Sistema de Guilds/Clãs

#### Conceito
- Usuários podem criar/juntar-se a guilds
- Competição entre guilds
- XP compartilhado (soma de todos membros)
- Benefícios coletivos

#### Comandos
```
!guild create <nome>         # Criar guild (custo: 500 MC)
!guild join <nome>           # Entrar em guild
!guild leave                 # Sair da guild
!guild info [nome]           # Info da guild
!guild rank                  # Ranking de guilds
!guild donate <MC>           # Doar moedas para guild
```

#### Benefícios de Guild
- **Level 1 Guild** (10 membros): +5% XP para todos
- **Level 5 Guild** (25 membros): +10% XP + Badge de guild
- **Level 10 Guild** (50 membros): +15% XP + Cor exclusiva
- **Level 20 Guild** (100 membros): +20% XP + Título + Efeitos especiais

#### Ranking de Guilds
```
╔══════════════════════════════════════════════════════════════╗
║  🏰 RANKING DE GUILDS - SERVIDOR                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🥇 #1 │ 🎵 Music Legends      │ 50 membros │ 1,245,000 XP ║
║  🥈 #2 │ 🎸 Rock Warriors      │ 45 membros │   980,500 XP ║
║  🥉 #3 │ 🎧 Bass Boosted       │ 42 membros │   876,200 XP ║
║  4️⃣ #4 │ 🎹 Piano Masters      │ 38 membros │   654,100 XP ║
║  5️⃣ #5 │ 🥁 Drum Circle        │ 35 membros │   532,800 XP ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

### 🎨 Sistema de Conquistas Dinâmicas

#### Conquistas que Evoluem
Ao invés de conquistas estáticas, criar conquistas que evoluem:

**Exemplo: "Colecionador"**
```
🥉 Bronze:    Adicionar 50 músicas
🥈 Prata:     Adicionar 100 músicas
🥇 Ouro:      Adicionar 500 músicas
💎 Diamante:  Adicionar 1000 músicas
👑 Mítico:    Adicionar 5000 músicas
```

Cada tier desbloqueia um upgrade visual da conquista.

---

### 🏆 Sistema de Troféus Raros

#### Troféus Únicos (1 por servidor)
- **"Primeiro Sangue"**: Primeira música adicionada no servidor
- **"Fundador"**: Primeiro a alcançar nível 100
- **"Inovador"**: Primeiro a desbloquear todas as conquistas

#### Troféus Limitados (Top 10 apenas)
- **"Elite"**: Top 10 do ranking global
- **"Lendário"**: Top 10 de 3 temporadas consecutivas

#### Troféus de Eventos
- **"Campeão do Verão 2026"**: Vencedor do evento de verão
- **"Maratonista 2026"**: Participante da maratona de 48h

---

## 📊 Métricas de Sucesso

### KPIs do Sistema de Gamificação

#### Engajamento
- **Meta:** +50% usuários ativos diários
- **Meta:** +200% comandos utilizados por usuário
- **Meta:** Tempo médio de sessão +30%

#### Retenção
- **Meta:** 80% usuários retornam após 7 dias
- **Meta:** 60% usuários retornam após 30 dias
- **Meta:** Streak médio de 10+ dias

#### Participação
- **Meta:** 70% usuários com pelo menos 1 conquista
- **Meta:** 40% usuários com nível 10+
- **Meta:** 90% usuários checam !profile semanalmente

#### Social
- **Meta:** 50% usuários participam de rankings
- **Meta:** 30% usuários em guilds
- **Meta:** 100+ comparações (!compare) por dia

---

## 🔧 Considerações Técnicas

### Performance
- **Cache de Rankings**: Redis com TTL de 5 minutos
- **Batch Updates**: Atualizar XP em lote a cada 30s
- **Índices de DB**: Otimizar queries de ranking
- **Paginação**: Limitar resultados a 100 por página

### Escalabilidade
- **Sharding de DB**: Por servidor Discord (guild_id)
- **Queue de Notificações**: RabbitMQ para conquistas
- **CDN**: Cachear badges e imagens

### Segurança
- **Rate Limiting**: 10 comandos/min por usuário
- **Validação**: Sanitizar inputs de títulos/cores
- **Anti-Cheat**: Detectar farming de XP
- **Backup**: Backup diário do banco de dados

---

## 📚 Referências e Inspirações

### Sistemas Similares
1. **MEE6** (Discord Bot)
   - Sistema de níveis
   - Comandos de perfil
   - Rankings

2. **Arcane** (Discord Bot)
   - Interface visual premium
   - Personalização avançada

3. **Duolingo**
   - Streaks e engajamento diário
   - Sistema de XP motivador

4. **Xbox Achievements**
   - Conquistas com raridade
   - Gamerscore (XP)

5. **League of Legends**
   - Sistema de honra
   - Ranking por temporada
   - Recompensas exclusivas

---

## ✅ Checklist de Implementação

### Fase 1: Fundação
- [ ] Setup banco de dados SQLite
- [ ] Modelos de dados (User, Stats)
- [ ] Sistema de tracking de ações
- [ ] Cálculo de XP
- [ ] Sistema de level-up
- [ ] Comando !profile
- [ ] Comando !level
- [ ] Comando !stats
- [ ] Testes unitários (90%+)
- [ ] Documentação da API

### Fase 2: Conquistas
- [ ] Sistema de achievements
- [ ] Definir 50+ conquistas
- [ ] Verificação de requisitos
- [ ] Tracking de progresso
- [ ] Notificações de desbloqueio
- [ ] Comando !achievements
- [ ] Comando !achievement <nome>
- [ ] Comando !progress
- [ ] Cards visuais
- [ ] Testes de integração

### Fase 3: Rankings
- [ ] Ranking global
- [ ] Sistema de temporadas
- [ ] Rankings por categoria
- [ ] Comando !rank
- [ ] Comando !top
- [ ] Comando !leaderboard
- [ ] Auto-reset (cron)
- [ ] Recompensas top 3
- [ ] Interface visual

### Fase 4: Social
- [ ] Comando !compare
- [ ] Comando !versus
- [ ] Sistema de badges
- [ ] Histórico de competições
- [ ] Notificações de ranking

### Fase 5: Recompensas
- [ ] Sistema de recompensas
- [ ] Títulos customizados
- [ ] Cores personalizadas
- [ ] Comando !title
- [ ] Comando !color
- [ ] Privilégios por nível
- [ ] Badges animados

### Fase 6: Polimento
- [ ] Otimização de queries
- [ ] Cache de rankings (Redis)
- [ ] Melhorias visuais
- [ ] Animações
- [ ] Testes de stress
- [ ] Documentação completa
- [ ] Beta testing

---

## 🎯 Conclusão

Este sistema de gamificação completo transformará o bot de música em uma experiência **interativa, recompensadora e viciante**. Com **50+ conquistas**, **100 níveis**, **rankings competitivos**, **recompensas exclusivas** e **eventos especiais**, os usuários terão motivos constantes para usar o bot e explorar novas músicas.

**Tempo estimado de implementação:** 8 semanas
**Complexidade:** Média-Alta
**Impacto no engajamento:** +50% a +200%
**ROI:** Altíssimo

---

**💡 Próximo Passo:** Aprovar o plano e iniciar Fase 1 (Fundação) na próxima sprint!

