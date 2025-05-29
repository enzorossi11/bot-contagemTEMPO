import os
import datetime
import subprocess
import sys

# Dados do repositório
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"

# Mensagem de commit
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
commit_message = f"Backup automático database pontos {now}"

# Token e URL do repositório
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REPO_URL = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"

# Configura o Git
subprocess.run(["git", "config", "--global", "user.email", "backup@render.com"])
subprocess.run(["git", "config", "--global", "user.name", "Render Backup Bot"])

# Garante que estamos rastreando a branch correta da origem
subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)
subprocess.run(["git", "remote", "add", "origin", REPO_URL])
subprocess.run(["git", "fetch", "origin"])
subprocess.run(["git", "checkout", "-B", BRANCH, "--track", f"origin/{BRANCH}"])

# Adiciona e comita o arquivo
subprocess.run(["git", "add", DB_FILE])
commit_result = subprocess.run(["git", "commit", "-m", commit_message], capture_output=True, text=True)

# Pula se não houver mudanças
if "nothing to commit" in (commit_result.stdout + commit_result.stderr).lower():
    print("Nenhuma mudança para commitar.")
    sys.exit(0)

# Tenta push forçado para resolver conflitos
push_result = subprocess.run(["git", "push", "--force", "origin", BRANCH], capture_output=True, text=True)
print(push_result.stdout)
print(push_result.stderr)
