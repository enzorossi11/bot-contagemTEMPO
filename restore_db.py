import os
import shutil
import requests

# Configurações
GITHUB_USERNAME = "enzorossi11"
REPO_NAME = "bot-contagemTEMPO"
BRANCH = "main"
DB_FILE = "tempo_online.db"
TOKEN = os.environ.get("GITHUB_TOKEN")

# URL do arquivo bruto no GitHub
url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/{DB_FILE}"

# Caminho local onde o arquivo deve ser salvo
destino = os.path.join(os.getcwd(), DB_FILE)

# Baixa o arquivo
print(f"Baixando {url}...")
headers = {"Authorization": f"token {TOKEN}"}
r = requests.get(url, headers=headers)

if r.status_code == 200:
    with open(destino, "wb") as f:
        f.write(r.content)
    print(f"{DB_FILE} restaurado com sucesso.")
else:
    print(f"Erro ao baixar o banco de dados: {r.status_code} - {r.text}")
