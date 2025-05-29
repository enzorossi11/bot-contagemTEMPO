import os
import subprocess

# Dados do repositório
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"

# Configura o Git (evita erros no Render)
subprocess.run(["git", "config", "--global", "user.email", "restore@render.com"])
subprocess.run(["git", "config", "--global", "user.name", "Render Restore Bot"])

# Recupera o token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"

# Garante que está atualizado com o último commit
subprocess.run(["git", "pull", repo_url, BRANCH])

print(f"{DB_FILE} restaurado com sucesso do GitHub.")
