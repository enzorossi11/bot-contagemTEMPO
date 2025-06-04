
import discord
from discord.ext import commands

def setup_comandos(bot, conn, cursor, niveis):
    @bot.command()
    async def pontos(ctx, membro: discord.Member = None):
        membro = membro or ctx.author
        cursor.execute("SELECT tempo_total FROM tempo_online WHERE usuario_id = ?", (membro.id,))
        resultado = cursor.fetchone()
        tempo = resultado[0] if resultado else 0
        horas = tempo // 3600
        minutos = (tempo % 3600) // 60
        await ctx.send(f"🕒 {membro.display_name} tem {horas}h {minutos}m de tempo no canal de voz.")

    @bot.command()
    async def niveis(ctx):
        import json
        with open("niveis.json", "r", encoding="utf-8") as file:
            niveis_json = json.load(file)

        embed = discord.Embed(title="📶 Lista de Níveis", color=0x3498db)
        for nivel in niveis_json:
            nome = nivel["nome"]
            emoji = nivel["emoji"]
            tempo = nivel["tempo"]
            embed.add_field(name=f"{emoji} {nome}", value=f"`{tempo}`", inline=False)

        
        embed.add_field(
            name="🧠 Base de Dados",
            value=(
                "`!restore` — Pega o backup do GitHub e substitui o banco atual do bot. (use só se o banco der problema)\n"
                "`!confirmar_restore` — Confirma a restauração e apaga o banco atual.\n"
                "`!backup_database` — Pega a versão atual da database do Render e salva no GitHub agora."
            ),
            inline=False
        )

        await ctx.send(embed=embed)

    @bot.command()
    async def comandos(ctx):
        embed = discord.Embed(title="📜 Lista de Comandos", color=0x00ff00)
        embed.add_field(name="🎯 Sistema de Pontuação", value="`!pontos` `!niveis`", inline=False)
        embed.add_field(
            name="🧠 Base de Dados",
            value=(
                "`!restore` — Pega o backup do GitHub e substitui o banco atual do bot. (use só se o banco der problema)
"
                "`!confirmar_restore` — Confirma a restauração e apaga o banco atual.
"
                "`!backup_database` — Pega a versão atual da database do Render e salva no GitHub agora."
            ),
            inline=False
        )
        
        embed.add_field(
            name="🧠 Base de Dados",
            value=(
                "`!restore` — Pega o backup do GitHub e substitui o banco atual do bot. (use só se o banco der problema)\n"
                "`!confirmar_restore` — Confirma a restauração e apaga o banco atual.\n"
                "`!backup_database` — Pega a versão atual da database do Render e salva no GitHub agora."
            ),
            inline=False
        )

        await ctx.send(embed=embed)
