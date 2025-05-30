import requests
import base64
import datetime
import os

GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

# Nome do commit
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
commit_message = f"Backup automático database pontos {now}"

# Lê o conteúdo do arquivo
with open(DB_FILE, "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

# Verifica se o arquivo já existe para pegar o SHA
url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{DB_FILE}"
headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

response = requests.get(url, headers=headers)
sha = response.json().get("sha") if response.status_code == 200 else None

# Faz upload do arquivo
data = {
    "message": commit_message,
    "content": content,
    "branch": BRANCH
}
if sha:
    data["sha"] = sha

put_response = requests.put(url, headers=headers, json=data)

if put_response.status_code in [200, 201]:
    print("✔ Backup enviado com sucesso!")
else:
    print("❌ Falha ao enviar backup:")
    print(put_response.json())
