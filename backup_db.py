import os
import datetime
import subprocess

# Dados do repositório
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"

# Caminho do banco
DB_FILE = "tempo_online.db"

# Nome do commit
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
commit_message = f"Backup automático database pontos {now}"

# Configuração global (opcional, mas ajuda o git a não travar)
subprocess.run(["git", "config", "--global", "user.email", "backup@render.com"])
subprocess.run(["git", "config", "--global", "user.name", "Render Backup Bot"])

# Adiciona o arquivo do banco ao stage
subprocess.run(["git", "add", DB_FILE])

# Faz o commit
subprocess.run(["git", "commit", "-m", commit_message])

# Pega o token do ambiente seguro
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Monta o link com autenticação
repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"

# Faz o push
subprocess.run(["git", "push", repo_url, BRANCH])
