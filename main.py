# tempo_bot.py final com ranking diario, semanal e all time + frases + formatação de tempo
import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, timedelta, time
import sqlite3
import json
import os
import random


TOKEN = "MTM3Njc3OTM0MjUxNjA2MDMxMQ.G5uOC2.xDr8bPH1rHDyfRkhkPXEQ_FkkxpCuj8hKP8tV8"
AFK_CHANNEL_ID = 978353439669125151
RANKING_CHANNEL_ID = 1377160080188772362

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.guilds = True
intents.message_content = True

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

with open("frases_diarias.json", encoding="utf-8") as f:
    FRASES_DIARIAS = json.load(f)

with open("frases_semanais.json", encoding="utf-8") as f:
    FRASES_SEMANAIS = json.load(f)

def agora():
    return datetime.utcnow().isoformat()

def formatar_tempo(segundos_total):
    minutos = segundos_total // 60
    horas = minutos // 60
    minutos_restantes = minutos % 60
    dias = horas // 24
    horas_restantes = horas % 24

    if dias >= 30:
        meses = dias // 30
        dias_restantes = dias % 30
        return f"{meses}m {dias_restantes}d {horas_restantes}h{minutos_restantes}m"
    elif dias >= 1:
        if dias == 1:
            return f"1 dia {horas_restantes}h{minutos_restantes}m"
        else:
            return f"{dias} dias {horas_restantes}h{minutos_restantes}m"
    else:
        return f"{horas}h{minutos_restantes}m"

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")
    verificar_tempos.start()
    enviar_rankings.start()

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        if after.channel.id == AFK_CHANNEL_ID:
            return
        cursor.execute("UPDATE usuarios SET entrou_em = ? WHERE user_id = ?", (agora(), member.id))
        if cursor.rowcount == 0:
            cursor.execute("INSERT INTO usuarios (user_id, entrou_em) VALUES (?, ?)", (member.id, agora()))
        conn.commit()
    elif before.channel is not None and after.channel is None:
        cursor.execute("SELECT entrou_em, tempo_total FROM usuarios WHERE user_id = ?", (member.id,))
        row = cursor.fetchone()
        if row and row[0]:
            entrou_em = datetime.fromisoformat(row[0])
            tempo_total = row[1]
            tempo_online = int((datetime.utcnow() - entrou_em).total_seconds())
            cursor.execute("UPDATE usuarios SET tempo_total = ?, entrou_em = NULL WHERE user_id = ?", (tempo_total + tempo_online, member.id))
            cursor.execute("INSERT INTO historico (user_id, timestamp, segundos) VALUES (?, ?, ?)", (member.id, agora(), tempo_online))
            conn.commit()

@tasks.loop(minutes=1)
async def verificar_tempos():
    for guild in bot.guilds:
        for vc in guild.voice_channels:
            if vc.id == AFK_CHANNEL_ID or len(vc.members) < 2:
                continue
            for member in vc.members:
                if member.bot or member.voice.self_mute or member.voice.self_deaf:
                    continue
                cursor.execute("UPDATE usuarios SET tempo_total = tempo_total + 60 WHERE user_id = ?", (member.id,))
                cursor.execute("INSERT INTO historico (user_id, timestamp, segundos) VALUES (?, ?, ?)" , (member.id, agora(), 60))
    conn.commit()

async def gerar_ranking(periodo_segundos, limite, frases, all_time=False):
    agora_dt = datetime.utcnow()
    inicio = agora_dt - timedelta(seconds=periodo_segundos)
    if all_time:
        cursor.execute("SELECT user_id, tempo_total FROM usuarios ORDER BY tempo_total DESC LIMIT ?", (limite,))
        dados = cursor.fetchall()
    else:
        cursor.execute("SELECT user_id, SUM(segundos) FROM historico WHERE timestamp >= ? GROUP BY user_id ORDER BY SUM(segundos) DESC LIMIT ?", (inicio.isoformat(), limite))
        dados = cursor.fetchall()

    linhas = []
    for i, (user_id, segundos) in enumerate(dados, start=1):
        try:
            membro = bot.get_user(user_id) or await bot.fetch_user(user_id)
            mencao = membro.mention
        except:
            mencao = f"<@{user_id}>"
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "🏆"
        tempo_fmt = formatar_tempo(segundos)
        frase = ""
        if all_time:
            frase = f"{i}. {emoji} {mencao} — {tempo_fmt}"
        else:
            fonte = random.choice(frases)
            frase = f"{i}. {emoji} {mencao} — {tempo_fmt}\n   🗢️ \"{fonte}\""
        linhas.append(frase)
    return "\n".join(linhas)

@tasks.loop(time=time(hour=20, minute=0))
async def enviar_rankings():
    agora = datetime.utcnow()
    canal = bot.get_channel(RANKING_CHANNEL_ID)
    if not canal:
        return
    titulo = "RANKING DA VAGABUNDAGEM"
    embed = discord.Embed(title=f"\U0001f3c6 {titulo} – {agora.strftime('%d/%m/%Y')}", color=0x2ecc71)

    diario = await gerar_ranking(86400, 10, FRASES_DIARIAS)
    embed.add_field(name="\U0001f31e Ranking Diário (24h)", value=diario or "Sem dados", inline=False)

    if agora.weekday() == 6:  # Domingo
        semanal = await gerar_ranking(604800, 20, FRASES_SEMANAIS)
        all_time = await gerar_ranking(999999999, 30, FRASES_SEMANAIS, all_time=True)
        embed.add_field(name="\U0001f4c6 Ranking Semanal (7 dias)", value=semanal or "Sem dados", inline=False)
        embed.add_field(name="\u23f3 Ranking All Time", value=all_time or "Sem dados", inline=False)

    await canal.send(embed=embed)

@bot.command()
async def pontos(ctx, membro: discord.Member = None):
    membro = membro or ctx.author
    cursor.execute("SELECT tempo_total FROM usuarios WHERE user_id = ?", (membro.id,))
    row = cursor.fetchone()
    tempo = int(row[0]) if row else 0
    await ctx.send(f"{membro.display_name} tem {formatar_tempo(tempo)} acumulados em canal de voz.")

bot.run(TOKEN)
