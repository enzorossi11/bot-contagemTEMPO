import subprocess
from datetime import datetime
import os
import shutil

# Caminho do banco original e nome do arquivo de backup
db_path = "tempo_online.db"
backup_path = "tempo_online.db"  # Mantém o mesmo nome para sobrescrever

# Garante que estamos no diretório do projeto
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Atualiza o arquivo de backup
shutil.copyfile(db_path, backup_path)

# Define as variáveis necessárias
repo_url = "https://oauth2:os.getenv("GITHUB_TOKEN")@github.com/enzorossi11/bot-contagemTEMPO.git"
branch = "main"

# Configurações iniciais de git
subprocess.run(["git", "config", "--global", "user.email", "backup@bot.com"])
subprocess.run(["git", "config", "--global", "user.name", "Bot Backup"])

# Adiciona o arquivo de banco de dados
subprocess.run(["git", "add", "tempo_online.db"])

# Faz commit com horário UTC
timestamp = datetime.utcnow().isoformat()
commit_message = f"Backup automático database pontos {timestamp}"
subprocess.run(["git", "commit", "-m", commit_message])

# Faz push para o repositório remoto (com token)
subprocess.run(["git", "push", repo_url, branch])
