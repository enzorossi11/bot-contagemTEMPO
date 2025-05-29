import os
import datetime
import subprocess

# Dados do repositório
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"

# Mensagem de commit
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
commit_message = f"Backup automático database pontos {now}"

# Configura o Git
subprocess.run(["git", "config", "--global", "user.email", "backup@render.com"])
subprocess.run(["git", "config", "--global", "user.name", "Render Backup Bot"])

# Puxa alterações remotas antes de commitar
subprocess.run(["git", "pull", f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git", BRANCH])

# Marca o arquivo como modificado
subprocess.run(["git", "add", DB_FILE])
commit_result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)

# Se não houver mudanças, para
if "nothing to commit" in commit_result.stdout + commit_result.stderr:
    print("Nenhuma mudança para commitar.")
    exit(0)

# Push com autenticação
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
subprocess.run(["git", "push", repo_url, BRANCH])
