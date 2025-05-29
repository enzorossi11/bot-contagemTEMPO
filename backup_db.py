import os
import datetime
import subprocess

# CONFIG
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_URL = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
COMMIT_MSG = f"Backup automático database pontos {datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')}"

# Setup Git
subprocess.run(["git", "config", "--global", "user.email", "backup@render.com"])
subprocess.run(["git", "config", "--global", "user.name", "Render Backup Bot"])

# Garante que está na branch correta
subprocess.run(["git", "checkout", "-B", BRANCH])

# Redefine remote
subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", REPO_URL])

# Faz pull rebase seguro
subprocess.run(["git", "pull", "--rebase", "origin", BRANCH])

# Adiciona e comita
subprocess.run(["git", "add", DB_FILE])
commit_result = subprocess.run(["git", "commit", "-m", COMMIT_MSG], capture_output=True, text=True)

# Sai se não houver mudanças
if "nothing to commit" in (commit_result.stdout + commit_result.stderr):
    print("Nenhuma mudança para commitar.")
    exit(0)

# Força o push mesmo com divergência
subprocess.run(["git", "push", "--force", "origin", BRANCH])
