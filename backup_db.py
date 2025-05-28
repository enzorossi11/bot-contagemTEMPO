import os
import shutil
import datetime
from git import Repo

# Caminhos
REPO_DIR = os.getcwd()
DB_NAME = "tempo_online.db"
BACKUP_NAME = "tempo_online.db"
GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_URL = f"https://{GITHUB_TOKEN}@github.com/enzorossi11/bot-contagemTEMPO.git"

# Inicializa ou abre repositório Git
if not os.path.exists(os.path.join(REPO_DIR, ".git")):
    repo = Repo.clone_from(REPO_URL, REPO_DIR)
else:
    repo = Repo(REPO_DIR)

# Puxa alterações mais recentes
origin = repo.remotes.origin
origin.pull()

# Garante que o banco está salvo com o nome correto
shutil.copyfile(DB_NAME, os.path.join(REPO_DIR, BACKUP_NAME))

# Adiciona e commita
repo.git.add(BACKUP_NAME)
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
repo.index.commit(f"Backup automático database pontos {now}")

# Faz push
origin.push()
print("Backup realizado com sucesso.")
