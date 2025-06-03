import discord
from discord.ext import commands
import datetime

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

def setup_comandos(bot, conn, cursor, niveis):

    @bot.command(name="pontos", aliases=["perfil"])
    async def pontos(ctx):
        user_id = ctx.author.id
        cursor.execute("SELECT tempo_total FROM usuarios WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        tempo_total = int(row[0]) if row else 0

        # calcular nível
        nivel, dados = 1, niveis[0]
        for i in reversed(range(len(niveis))):
            if tempo_total >= niveis[i]["tempo_segundos"]:
                nivel = i + 1
                dados = niveis[i]
                break

        # tempo para o próximo nível
        tempo_prox = None
        if nivel < len(niveis):
            tempo_prox = niveis[nivel]["tempo_segundos"] - tempo_total
        else:
            tempo_prox = 0

        progresso_pct = 100 if tempo_prox == 0 else int((tempo_total - dados["tempo_segundos"]) / (niveis[nivel]["tempo_segundos"] - dados["tempo_segundos"]) * 100)

        embed = discord.Embed(
            title=f"📈 Estatísticas de {ctx.author.display_name}",
            color=discord.Color.blurple()
        )
        embed.add_field(name="🕒 Tempo total", value=formatar_tempo(tempo_total), inline=False)
        embed.add_field(name="🏅 Nível atual", value=f"{dados['emoji']} {dados['nome']} (Nível {nivel})", inline=False)
        embed.add_field(name="📊 Progresso", value=f"{progresso_pct}% — faltam {formatar_tempo(tempo_prox)}", inline=False)

        await ctx.send(embed=embed)

    @bot.command(name="toptempo")
    async def toptempo(ctx):
        try:
            with open("recordes.json", encoding="utf-8") as f:
                rec = json.load(f)

            embed = discord.Embed(title="🏆 Recordes do Servidor", color=0xf1c40f)
            embed.add_field(name="📅 Maior tempo em 1 dia", value=f"{rec['maior_tempo_dia']['usuario']} — {formatar_tempo(rec['maior_tempo_dia']['tempo'])} ({rec['maior_tempo_dia']['data']})", inline=False)
            embed.add_field(name="📆 Maior tempo em 1 semana", value=f"{rec['maior_tempo_semana']['usuario']} — {formatar_tempo(rec['maior_tempo_semana']['tempo'])} ({rec['maior_tempo_semana']['semana']})", inline=False)
            embed.add_field(name="🫂 Maior número de pessoas em call", value=f"{rec['maior_qtd_membros_call']['quantidade']} pessoas ({rec['maior_qtd_membros_call']['data']})", inline=False)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Erro ao carregar recordes: {e}")

    @bot.command(name="comandos")
    async def comandos(ctx):
        embed = discord.Embed(title="📜 Comandos disponíveis", color=discord.Color.green())
        embed.add_field(name="!pontos ou !perfil", value="Mostra seu tempo total, semanal, hoje, nível atual, progresso e ranking.", inline=False)
        embed.add_field(name="!toptempo", value="Exibe os recordes históricos do servidor.", inline=False)
        if ctx.author.id == 343856610235383809:
            embed.add_field(name="!ranking now", value="Força geração dos rankings mesmo fora do horário.", inline=False)
            embed.add_field(name="!backup now", value="Gera backup manual do banco e envia pro GitHub.", inline=False)
            embed.add_field(name="!debug addtempo @user tempo", value="Adiciona tempo (em segundos) a um usuário. Só você pode usar.", inline=False)
        await ctx.send(embed=embed)
