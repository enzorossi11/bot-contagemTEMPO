
# 🤖 Bot de Contagem de Tempo em Canais de Voz (Discord)

Este bot monitora automaticamente o tempo que os usuários passam em canais de voz no Discord e gera:
- Pontuação por tempo online
- Sistema de níveis personalizado
- Rankings diários, semanais e históricos
- Frases sarcásticas para cada tipo de ranking
- Mensagens de evolução de nível
- Backups automáticos do banco de dados para o GitHub

---

## 📁 Estrutura do Repositório

| Arquivo                    | Descrição |
|----------------------------|-----------|
| `main.py`                 | Código principal com eventos, backup e controle de banco |
| `comandos.py`             | Comandos organizados (`!pontos`, `!niveis`, `!comandos` etc.) |
| `frases_diarias.json`     | Frases sarcásticas do ranking diário |
| `frases_semanais.json`    | Frases do ranking semanal |
| `frases_niveis.json`      | Frases de evolução de nível |
| `niveis.json`             | Estrutura de níveis (tempo necessário, nome e emoji) |
| `recordes.json`           | Armazena recordes históricos de tempo online |
| `tempo_online.db.b64`     | Backup do banco de dados, salvo automaticamente no GitHub |

---

## ⚙️ Funcionamento Geral

### 🔊 Rastreamento de Voz
- O bot escuta eventos de entrada e saída em canais de voz.
- Se o usuário estiver ativo (não mudo/surdo/sozinho), o tempo é acumulado.
- Esse tempo alimenta o sistema de pontuação e rankings.

### 🧮 Pontuação e Níveis
- 1 ponto = 1 hora online (60 minutos = 3600 segundos)
- A cada ponto acumulado, o usuário pode subir de nível.
- A estrutura de níveis e os tempos necessários estão no `niveis.json`.

### 🎯 Rankings
- Ranking diário: Top 10 usuários de hoje
- Ranking semanal: Top 20 da semana
- Ranking all time: Top 30 acumulado de todos os tempos
- Enviados automaticamente em embed com emojis e frases sarcásticas

---

## 💾 Banco de Dados

### Armazenamento
- O bot usa um banco local chamado `tempo_online.db` (SQLite).
- Ele é criado automaticamente no Render a cada novo deploy.

### Backup Automático
- Todo dia às **08h da manhã (horário de Brasília)**, o bot faz um backup do banco atual para o GitHub como `tempo_online.db.b64`.

### Restauração Automática
- Ao iniciar (por exemplo, após um novo deploy), o bot **restaura automaticamente o banco mais recente do GitHub** antes de começar a rodar.

---

## 🧠 Comandos do Bot

### 🎯 Sistema de Pontuação
- `!pontos`: Mostra quanto tempo o usuário já acumulou.
- `!niveis`: Lista todos os níveis possíveis com emojis e tempo.

### 🧠 Base de Dados
- `!backup_database`: Salva imediatamente o banco do Render no GitHub.
- `!restore`: Inicia processo de restauração (somente o dono do bot pode usar).
- `!confirmar_restore`: Executa a restauração do backup do GitHub.

### ℹ️ Informações
- `!comandos`: Lista todos os comandos do bot, organizados por categoria.

---

## 🛠️ Setup no Render

1. Faça fork do repositório no GitHub.
2. Crie um novo serviço no [Render.com](https://render.com).
3. Aponte o serviço para seu repositório.
4. Defina as variáveis de ambiente:
   - `DISCORD_TOKEN`: Token do seu bot do Discord
   - `GITHUB_TOKEN`: Token com permissão de escrita no seu repositório
5. O bot vai iniciar automaticamente e restaurar a base de dados mais recente do GitHub.

---

## ⚠️ Regras de Manutenção

- Sempre rode `!backup_database` **antes de qualquer commit** ou alteração importante no código.
- Nunca suba o arquivo `tempo_online.db` bruto para o repositório. Apenas o `.b64` é utilizado.
- Os arquivos `backup_db.py`, `restore_db.py` e `tempo_online.db` **devem ser removidos do repositório.**

---

## ✍️ Autor

Desenvolvido e mantido por **Enzo Rossi**.
