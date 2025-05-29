import os
import datetime
import subprocess

# Configurações
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"

# Token e URL do repositório
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_URL = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"

# Mensagem de commit
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
commit_message = f"Backup automático database pontos {now}"

# Configura Git
subprocess.run(["git", "config", "--global", "user.email", "backup@render.com"])
subprocess.run(["git", "config", "--global", "user.name", "Render Backup Bot"])

# (Re)define a origem
subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", REPO_URL])

# Faz pull com rebase
subprocess.run(["git", "pull", "--rebase", "origin", BRANCH])

# Adiciona e comita
subprocess.run(["git", "add", DB_FILE])
commit_result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)

# Sai se não houver mudanças
if "nothing to commit" in commit_result.stdout + commit_result.stderr:
    print("Nenhuma mudança para commitar.")
    exit(0)

# Push
subprocess.run(["git", "push", "origin", BRANCH])
