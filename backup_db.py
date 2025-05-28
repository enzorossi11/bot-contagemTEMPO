import subprocess
import datetime

def executar_backup():
    try:
        # Nome do arquivo a fazer backup
        db_file = "tempo_online.db"

        # Nome do commit com data
        commit_message = f"Backup automático database pontos {datetime.datetime.now().isoformat(timespec='seconds')}"

        # Comandos Git
        subprocess.run(["git", "config", "--global", "user.name", "BackupBot"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "backup@bot.com"], check=True)
        subprocess.run(["git", "add", db_file], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("Backup enviado com sucesso.")
    except subprocess.CalledProcessError as e:
        print("Erro ao fazer backup:", e)

if __name__ == "__main__":
    executar_backup()
