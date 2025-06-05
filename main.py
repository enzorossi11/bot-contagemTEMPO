import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
import sqlite3
import os
import json
import random
from comandos import setup_comandos

TOKEN = os.environ["DISCORD_TOKEN"]
AFK_CHANNEL_ID = 978353439669125151
CANAL_UP_ID = 1377160080188772362
MUSICA_BOT_ID = 411916947773587456

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

conn = sqlite3.connect("tempo_online.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    user_id INTEGER PRIMARY KEY,
    tempo_total INTEGER DEFAULT 0,
    entrou_em TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS historico (
    user_id INTEGER,
    timestamp TEXT,
    segundos INTEGER
)
""")
conn.commit()

with open("niveis.json", encoding="utf-8") as f:
    NIVEIS = json.load(f)

def agora():
    return datetime.utcnow().isoformat()

def formatar_tempo(segundos_total):
    minutos = segundos_total // 60
    horas = minutos // 60
    minutos_restantes = minutos % 60
    dias = horas // 24
    horas_restantes = horas % 24
    if dias >= 1:
        return f"{dias} dias {horas_restantes} horas {minutos_restantes} minutos"
    else:
        return f"{horas} horas {minutos_restantes} minutos"

def calcular_nivel(tempo_total):
    for i in reversed(range(len(NIVEIS))):
        if tempo_total >= NIVEIS[i]["tempo_segundos"]:
            return i + 1, NIVEIS[i]
    return 1, NIVEIS[0]

@bot.event
async def on_ready():
    await restore_db_from_github()
    print(f"✅ Bot conectado como {bot.user}")
    verificar_tempos.start()

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == MUSICA_BOT_ID:
        return

    agora_iso = agora()

    if before.channel is None and after.channel is not None:
        if after.channel.id == AFK_CHANNEL_ID:
            return
        cursor.execute("UPDATE usuarios SET entrou_em = ? WHERE user_id = ?", (agora_iso, member.id))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO usuarios (user_id, entrou_em) VALUES (?, ?)", (member.id, agora_iso))
        conn.commit()

    elif before.channel is not None and after.channel is None:
        cursor.execute("SELECT entrou_em, tempo_total FROM usuarios WHERE user_id = ?", (member.id,))
        row = cursor.fetchone()
        if row and row[0]:
            entrou_em = datetime.fromisoformat(row[0])
            tempo_total = row[1]
            tempo_online = int((datetime.utcnow() - entrou_em).total_seconds())
            novo_total = tempo_total + tempo_online
            cursor.execute("UPDATE usuarios SET tempo_total = ?, entrou_em = NULL WHERE user_id = ?", (novo_total, member.id))
            cursor.execute("INSERT INTO historico (user_id, timestamp, segundos) VALUES (?, ?, ?)", (member.id, agora_iso, tempo_online))
            conn.commit()

            # checar nível
            cursor.execute("SELECT tempo_total FROM usuarios WHERE user_id = ?", (member.id,))
            tempo_atual = cursor.fetchone()[0]
            nivel_antigo, _ = calcular_nivel(tempo_total)
            nivel_novo, dados_novo = calcular_nivel(tempo_atual)

            if nivel_novo > nivel_antigo and nivel_novo >= 5:
                canal = bot.get_channel(CANAL_UP_ID)
                try:
                    nome = dados_novo["nome"]
                    emoji = dados_novo["emoji"]
                    description = f"{member.mention} agora é **{nome}** {emoji}\n🕒 Tempo total: {formatar_tempo(tempo_atual)}"

                    embed = discord.Embed(
                        title=random.choice(["📈 Subiu de Nível!", "📢 Novo Nível Desbloqueado!"]),
                        description=description,
                        color=0x00ffcc
                    )

                    faixa = ""
                    if 5 <= nivel_novo <= 9: faixa = "5-9"
                    elif 10 <= nivel_novo <= 14: faixa = "10-14"
                    elif 15 <= nivel_novo <= 19: faixa = "15-19"
                    elif 20 <= nivel_novo <= 24: faixa = "20-24"

                    with open("frases_niveis.json", encoding="utf-8") as f:
                        frases = json.load(f)
                        if faixa in frases:
                            embed.add_field(name="🗣️", value=random.choice(frases[faixa]), inline=False)

                    await canal.send(embed=embed)
                    await member.send(embed=embed)
                except Exception as e:
                    print(f"Erro ao enviar mensagem de up: {e}")

@tasks.loop(minutes=1)
async def verificar_tempos():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            membros_validos = [m for m in vc.members if m.id != MUSICA_BOT_ID and not m.bot and not m.voice.self_mute and not m.voice.self_deaf]
            if vc.id == AFK_CHANNEL_ID or len(membros_validos) < 2:
                continue
            for member in membros_validos:
                cursor.execute("UPDATE usuarios SET tempo_total = tempo_total + 60 WHERE user_id = ?", (member.id,))
                cursor.execute("INSERT INTO historico (user_id, timestamp, segundos) VALUES (?, ?, ?)" , (member.id, agora(), 60))
    conn.commit()

setup_comandos(bot, conn, cursor, NIVEIS)



@tasks.loop(hours=1)
async def atualizar_recordes():
    agora = datetime.utcnow()
    if agora.hour != 2:  # Evita rodar a lógica fora da janela desejada
        return

    hoje = agora.date()
    ontem = hoje - timedelta(days=1)
    inicio_ontem = datetime.combine(ontem, datetime.min.time()).isoformat()
    fim_ontem = datetime.combine(ontem, datetime.max.time()).isoformat()

    semana_inicio = hoje - timedelta(days=7)
    inicio_semana = datetime.combine(semana_inicio, datetime.min.time()).isoformat()

    rec_path = "recordes.json"

    try:
        with open(rec_path, "r", encoding="utf-8") as f:
            rec = json.load(f)
    except FileNotFoundError:
        rec = {
            "maior_tempo_dia": {"usuario": "N/A", "tempo": 0, "data": "N/A"},
            "maior_tempo_semana": {"usuario": "N/A", "tempo": 0, "data": "N/A"},
            "maior_qtd_membros_call": {"quantidade": 0, "data": "N/A"}
        }

    # Maior tempo de 1 dia
    row = cursor.execute("""
        SELECT user_id, SUM(segundos) FROM historico
        WHERE timestamp >= ? AND timestamp <= ?
        GROUP BY user_id
        ORDER BY SUM(segundos) DESC
        LIMIT 1
    """, (inicio_ontem, fim_ontem)).fetchone()

    if row:
        user_id, tempo = row
        if tempo > rec["maior_tempo_dia"]["tempo"]:
            membro = bot.get_user(user_id)
            nome = membro.display_name if membro else f"ID {user_id}"
            rec["maior_tempo_dia"] = {
                "usuario": nome,
                "tempo": tempo,
                "data": ontem.isoformat()
            }

    # Maior tempo de 1 semana
    row = cursor.execute("""
        SELECT user_id, SUM(segundos) FROM historico
        WHERE timestamp >= ?
        GROUP BY user_id
        ORDER BY SUM(segundos) DESC
        LIMIT 1
    """, (inicio_semana,)).fetchone()

    if row:
        user_id, tempo = row
        if tempo > rec["maior_tempo_semana"]["tempo"]:
            membro = bot.get_user(user_id)
            nome = membro.display_name if membro else f"ID {user_id}"
            rec["maior_tempo_semana"] = {
                "usuario": nome,
                "tempo": tempo,
                "data": hoje.isoformat()
            }

    # Maior quantidade de pessoas simultâneas em call (verificado a cada tick no tempo)
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            membros_validos = [
                m for m in vc.members
                if not m.bot and not m.voice.self_mute and not m.voice.self_deaf
            ]
            qtd = len(membros_validos)
            if qtd > rec["maior_qtd_membros_call"]["quantidade"]:
                rec["maior_qtd_membros_call"]["quantidade"] = qtd
                rec["maior_qtd_membros_call"]["data"] = hoje.isoformat()

    with open(rec_path, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=2, ensure_ascii=False)


atualizar_recordes.start()

@bot.command(name="ranking")
async def ranking_manual(ctx, tipo=None):
    if ctx.author.id != 343856610235383809:
        await ctx.send("🚫 Você não tem permissão para isso.")
        return

    tipo = (tipo or "").lower()

    if tipo == "diario":
        await enviar_ranking("diario")
        await ctx.send("✅ Ranking diário enviado manualmente.")
    elif tipo == "semanal":
        await enviar_ranking("semanal")
        await ctx.send("✅ Ranking semanal enviado manualmente.")
    elif tipo == "alltime":
        await enviar_ranking("alltime")
        await ctx.send("✅ Ranking all time enviado manualmente.")
    else:
        await ctx.send("❌ Tipo inválido. Use: `!ranking now diario`, `semanal` ou `alltime`.")


bot.run(TOKEN)



import base64
import requests
import aiocron

GITHUB_REPO = 'enzorossi11/bot-contagemTEMPO'
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OWNER_ID = 343856610235383809
DB_FILE = 'tempo_online.db'
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/contents/tempo_online.db.b64'

@aiocron.crontab('0 11 * * *')
async def scheduled_backup():
    await backup_db()

async def backup_db():
    try:
        with open(DB_FILE, 'rb') as f:
            encoded_content = base64.b64encode(f.read()).decode('utf-8')

        response = requests.get(GITHUB_API_URL, headers={
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        })
        if response.status_code == 200:
            sha = response.json()['sha']
            requests.put(GITHUB_API_URL,
                headers={
                    'Authorization': f'token {GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                json={
                    'message': 'Backup automático/manual',
                    'content': encoded_content,
                    'sha': sha
                }
            )
        else:
            requests.put(GITHUB_API_URL,
                headers={
                    'Authorization': f'token {GITHUB_TOKEN}',
                    'Accept': 'application/vnd.github.v3+json'
                },
                json={
                    'message': 'Primeiro backup',
                    'content': encoded_content
                }
            )
        print("Backup enviado para o GitHub.")
    except Exception as e:
        print("Erro ao fazer backup:", e)

async def restore_db_from_github():
    try:
        response = requests.get(GITHUB_API_URL, headers={
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        })

        if response.status_code == 200:
            content = base64.b64decode(response.json()['content'])
            with open(DB_FILE, 'wb') as f:
                f.write(content)
            print("Banco restaurado do GitHub.")
            return True
        else:
            print("Nenhum backup encontrado.")
            return False
    except Exception as e:
        print("Erro ao restaurar banco:", e)
        return False

@bot.command()
async def backup_database(ctx):
    if ctx.author.id != OWNER_ID:
        return
    await backup_db()
    await ctx.send("📦 Backup enviado pro GitHub!")

@bot.command()
async def restore(ctx):
    if ctx.author.id != OWNER_ID:
        return
    await ctx.send("""⚠️ Isso vai restaurar o banco do GitHub e apagar o atual.
Digite `!confirmar_restore` pra continuar.""")
Digite `!confirmar_restore` pra continuar.")

@bot.command()
async def confirmar_restore(ctx):
    if ctx.author.id != OWNER_ID:
        return
    sucesso = await restore_db_from_github()
    if sucesso:
        await ctx.send("✅ Banco restaurado com sucesso.")
    else:
        await ctx.send("❌ Erro ao restaurar o banco. Verifique o GitHub.")
